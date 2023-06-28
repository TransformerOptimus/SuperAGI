from __future__ import absolute_import

from datetime import datetime, timedelta
from celery import Celery

from superagi.config.config import get_config
from superagi.jobs.agent_executor import AgentExecutor
from superagi.models.agent_scheduler import AgentScheduler
from superagi.jobs.agent_executor import ScheduledAgentExecutor
from superagi.models.db import connect_db
from sqlalchemy.orm import sessionmaker
from superagi.lib.logger import logger

engine = connect_db()
Session = sessionmaker(bind=engine)

redis_url = get_config('REDIS_URL')

app = Celery("superagi", include=["superagi.worker"], imports=["superagi.worker"])
app.conf.broker_url = "redis://" + redis_url + "/0"
app.conf.result_backend = "redis://" + redis_url + "/0"
app.conf.worker_concurrency = 10

beat_schedule = {
    'initialize-schedule-agent': {
        'task': 'initialize-schedule-agent', 
        'schedule': timedelta(minutes=5),
    },
}
app.conf.beat_schedule = beat_schedule

@app.task(name="initialize-schedule-agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def initialize_schedule_agent_task():
    update_next_scheduled_time()
    get_scheduled_agents()


def parse_interval_to_seconds(interval: str) -> int:
    units = {"Minutes": 60, "Hours": 3600, "Days": 86400, "Weeks": 604800, "Months": 2592000}
    value, unit = interval.split(" ")
    return int(value) * units[unit]

def create_agent_name_with_timestamp() -> str:
    timestamp = datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
    return f"Run {timestamp}"

def check_time_difference(agent, now):
    next_scheduled_time = agent.next_scheduled_time
    interval = agent.recurrence_interval
    interval_in_seconds = max(parse_interval_to_seconds(interval), 300)
    return (now - next_scheduled_time).total_seconds() > interval_in_seconds

def update_next_schedule(agent, start_time, interval_in_seconds, now):
    time_diff = now - start_time
    num_intervals_passed = time_diff.total_seconds() // interval_in_seconds  
    updated_next_scheduled_time = start_time + timedelta(seconds=(interval_in_seconds * (num_intervals_passed + 1)))
    agent.next_scheduled_time = updated_next_scheduled_time
    
def update_next_scheduled_time():
    now = datetime.now()
    
    session = Session()
    scheduled_agents = session.query(AgentScheduler).filter(
    (AgentScheduler.start_time < now) &
    (AgentScheduler.next_scheduled_time < now)).all()
    for agent in scheduled_agents:
        if check_time_difference(agent, now):
            update_next_schedule(agent, agent.start_time, parse_interval_to_seconds(agent.recurrence_interval), now)
    session.commit()

def should_execute_and_remove_agent(agent, interval, interval_in_seconds):
    next_scheduled_time = agent.next_scheduled_time
    expiry_date = agent.expiry_date
    expiry_runs = agent.expiry_runs
    current_runs = agent.current_runs
    if not interval:
        return True, True
    if expiry_date is None and expiry_runs is None:
        return True, False
    elif expiry_date is not None and datetime.now() < expiry_date:
        return True, False
    elif expiry_runs != -1 and current_runs < expiry_runs:
        return True, False
    if (expiry_date is not None and datetime.now() >= expiry_date) or (expiry_runs != -1 and current_runs >= expiry_runs):
        return False, True
    return False, False

def execute_agent(agent, agent_id):
    agent_name = create_agent_name_with_timestamp()
    agent.current_runs += 1
    ScheduledAgentExecutor.execute_scheduled_agent(agent_id, agent_name)

def update_next_schedule(agent, interval_in_seconds):
    next_scheduled_time = agent.next_scheduled_time + timedelta(seconds=interval_in_seconds)
    agent.next_scheduled_time = next_scheduled_time

def get_scheduled_agents():
    now = datetime.now()
    last_5_minutes = now - timedelta(minutes=5)
    session = Session()
    scheduled_agents = session.query(AgentScheduler).filter(AgentScheduler.next_scheduled_time.between(last_5_minutes, now)).all()
    logger.info("////////////// SCHEDULED AGENTS")
    logger.info(scheduled_agents)
    agents_to_remove = []

    for agent in scheduled_agents:
        interval = agent.recurrence_interval
        interval_in_seconds = parse_interval_to_seconds(interval)
        agent_id = agent.agent_id
        agent_name = create_agent_name_with_timestamp()
        current_runs = agent.current_runs

        should_execute_agent, should_remove_agent = should_execute_and_remove_agent(agent, interval, interval_in_seconds)
        if should_execute_agent:
            ScheduledAgentExecutor.execute_scheduled_agent(agent_id, agent_name)
            agent.current_runs = current_runs + 1

            if interval and not should_remove_agent:
                next_scheduled_time = next_scheduled_time + timedelta(seconds=interval_in_seconds)
                agent.next_scheduled_time = next_scheduled_time

            session.commit()

        if should_remove_agent:
            agents_to_remove.append(agent)

    for agent in agents_to_remove:
        session.delete(agent)
        session.commit()


@app.task(name="execute_agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    from superagi.jobs.agent_executor import AgentExecutor
    logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))
    AgentExecutor().execute_next_action(agent_execution_id=agent_execution_id)


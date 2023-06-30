from __future__ import absolute_import

from datetime import datetime, timedelta
import pytz
from celery import Celery

from superagi.config.config import get_config
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_scheduler import AgentScheduler
from superagi.jobs.agent_executor import ScheduledAgentExecutor
from superagi.lib.logger import logger
from superagi.models.db import connect_db
from sqlalchemy.orm import sessionmaker

redis_url = get_config('REDIS_URL') or 'localhost:6379'
engine = connect_db()
Session = sessionmaker(bind=engine)

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

def create_agent_name_with_timestamp(agent_id) -> str:
    session = Session()
    user_timezone = session.query(AgentConfiguration).filter(AgentConfiguration.key == "user_timezone", AgentConfiguration.agent_id==agent_id).first()

    if user_timezone and user_timezone.value:
        current_time = datetime.now().astimezone(pytz.timezone(user_timezone.value))
    else:
        current_time = datetime.now().astimezone(pytz.timezone('GMT'))
        
    timestamp = current_time.strftime(" %d %B %Y %H:%M")
    return f"Run{timestamp}"

def check_time_difference(agent, now):
    next_scheduled_time = agent.next_scheduled_time
    return (now - next_scheduled_time).total_seconds() > 300

    
def update_next_scheduled_time():
    now = datetime.now()

    session = Session()
    scheduled_agents = session.query(AgentScheduler).filter(
    (AgentScheduler.start_time <= now) &
    (AgentScheduler.next_scheduled_time <= now) &
    (AgentScheduler.status == "RUNNING")).all()
    
    for agent in scheduled_agents:
        if check_time_difference(agent, now):
            if agent.recurrence_interval is not None:
                interval_in_seconds = parse_interval_to_seconds(agent.recurrence_interval)
                time_diff = now - agent.start_time
                num_intervals_passed = time_diff.total_seconds() // interval_in_seconds  
                updated_next_scheduled_time = agent.start_time + timedelta(seconds=(interval_in_seconds * (num_intervals_passed + 1)))
                agent.next_scheduled_time = updated_next_scheduled_time
            else:
                agent.status = "TERMINATED"
            session.commit()

def should_execute_and_remove_agent(agent, interval):
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

def execute_schedule(should_execute_agent, should_remove_agent, interval_in_seconds, session, agent, agent_name):
    if should_execute_agent:
        ScheduledAgentExecutor.execute_scheduled_agent(agent.agent_id, agent_name)
        agent.current_runs = agent.current_runs + 1

        if agent.recurrence_interval and not should_remove_agent:
            next_scheduled_time = agent.next_scheduled_time + timedelta(seconds=interval_in_seconds)
            agent.next_scheduled_time = next_scheduled_time

            session.commit()

def remove_completed_agents(agents_to_remove, session):
    for agent in agents_to_remove:
        agent.status = "COMPLETED"
        session.commit()

def get_scheduled_agents():
    now = datetime.now()
    last_5_minutes = now - timedelta(minutes=5)
    
    session = Session()
    scheduled_agents = session.query(AgentScheduler).filter(AgentScheduler.next_scheduled_time.between(last_5_minutes, now)).all()
    agents_to_remove = []

    for agent in scheduled_agents:
        interval = agent.recurrence_interval
        interval_in_seconds = 0  # default value
        if interval is not None:
            interval_in_seconds = parse_interval_to_seconds(interval)
        agent_id = agent.agent_id
        agent_name = create_agent_name_with_timestamp(agent_id)

        should_remove_agent = False
        should_execute_agent, should_remove_agent = should_execute_and_remove_agent(agent, interval)
        execute_schedule(should_execute_agent, should_remove_agent, interval_in_seconds, session, agent, agent_name)

        if should_remove_agent:
            agents_to_remove.append(agent)

        remove_completed_agents(agents_to_remove, session)


@app.task(name="execute_agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    from superagi.jobs.agent_executor import AgentExecutor
    logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))
    AgentExecutor().execute_next_action(agent_execution_id=agent_execution_id)


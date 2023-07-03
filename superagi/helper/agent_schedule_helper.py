from superagi.models.db import connect_db
from sqlalchemy.orm import sessionmaker
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_schedule import AgentSchedule
from datetime import datetime, timedelta
from superagi.helper.time_helper import parse_interval_to_seconds, check_time_difference
import pytz

engine = connect_db()
Session = sessionmaker(bind=engine)

class AgentScheduleHelper:
    @classmethod
    def _create_execution_name_for_scheduling(cls, agent_id) -> str:
        session = Session()
        user_timezone = session.query(AgentConfiguration).filter(AgentConfiguration.key == "user_timezone", AgentConfiguration.agent_id==agent_id).first()

        if user_timezone and user_timezone.value:
            current_time = datetime.now().astimezone(pytz.timezone(user_timezone.value))
        else:
            current_time = datetime.now().astimezone(pytz.timezone('GMT'))
            
        timestamp = current_time.strftime(" %d %B %Y %H:%M")
        return f"Run{timestamp}"
    
    @classmethod
    def update_next_scheduled_time(cls):
        now = datetime.now()

        session = Session()
        scheduled_agents = session.query(AgentSchedule).filter(
        (AgentSchedule.start_time <= now) &
        (AgentSchedule.next_scheduled_time <= now) &
        (AgentSchedule.status == "RUNNING")).all()

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
        session.close()

    @classmethod
    def _should_execute_and_remove_agent(cls, agent, interval):
        expiry_date = agent.expiry_date
        expiry_runs = agent.expiry_runs
        current_runs = agent.current_runs
        if not interval:
            return True, True
        if expiry_date is None and expiry_runs is None:
            return True, False
        elif expiry_date is not None and datetime.now() < expiry_date:
            if agent.next_scheduled_time + timedelta(seconds=parse_interval_to_seconds(interval)) <= agent.expiry_date:
                return True, True
            return True, False
        elif expiry_runs != -1 and current_runs < expiry_runs:
            if current_runs+1 == expiry_runs:
                return True, True
            return True, False
        if (expiry_date is not None and datetime.now() >= expiry_date) or (expiry_runs != -1 and current_runs >= expiry_runs):
            return False, True
        return False, False

    @classmethod
    def _execute_schedule(cls, should_execute_agent, should_remove_agent, interval_in_seconds, session, agent, agent_name):
        from superagi.jobs.agent_executor import ScheduledAgentExecutor
        if should_execute_agent:
            ScheduledAgentExecutor.execute_scheduled_agent(agent.agent_id, agent_name)
            agent.current_runs = agent.current_runs + 1

            if agent.recurrence_interval and not should_remove_agent:
                next_scheduled_time = agent.next_scheduled_time + timedelta(seconds=interval_in_seconds)
                agent.next_scheduled_time = next_scheduled_time

            session.commit()

    @classmethod
    def __remove_completed_agents(cls, agents_to_remove, session):
        for agent in agents_to_remove:
            agent.status = "COMPLETED"
            session.commit()

    @classmethod
    def get_scheduled_agents(cls):
        now = datetime.now()
        last_five_minutes = now - timedelta(minutes=5)
        
        session = Session()
        scheduled_agents = session.query(AgentSchedule).filter(AgentSchedule.next_scheduled_time.between(last_five_minutes, now)).all()
        agents_to_remove = []

        for agent in scheduled_agents:
            interval = agent.recurrence_interval
            interval_in_seconds = 0  # default value
            if interval is not None:
                interval_in_seconds = parse_interval_to_seconds(interval)
            agent_id = agent.agent_id
            agent_name = cls._create_execution_name_for_scheduling(agent_id)

            should_remove_agent = False
            should_execute_agent, should_remove_agent = cls._should_execute_and_remove_agent(agent, interval)
            cls._execute_schedule(should_execute_agent, should_remove_agent, interval_in_seconds, session, agent, agent_name)

            if should_remove_agent:
                agents_to_remove.append(agent)

        cls.__remove_completed_agents(agents_to_remove, session)

        session.close()
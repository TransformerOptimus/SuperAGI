from superagi.models.db import connect_db
from sqlalchemy.orm import sessionmaker
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_schedule import AgentSchedule
from datetime import datetime, timedelta
from superagi.helper.time_helper import parse_interval_to_seconds
import pytz

engine = connect_db()
Session = sessionmaker(bind=engine)


class AgentScheduleHelper:
    AGENT_SCHEDULE_TIME_INTERVAL = 300

    def run_scheduled_agents(self):
        now = datetime.now()
        last_five_minutes = now - timedelta(minutes=5)

        session = Session()
        scheduled_agents = session.query(AgentSchedule).filter(
            AgentSchedule.next_scheduled_time.between(last_five_minutes, now), AgentSchedule.status == "SCHEDULED").all()

        for agent in scheduled_agents:
            interval = agent.recurrence_interval
            interval_in_seconds = 0  # default value
            if interval is not None:
                interval_in_seconds = parse_interval_to_seconds(interval)
            agent_id = agent.agent_id
            agent_name = self._create_execution_name_for_scheduling(agent_id)

            should_execute_agent = self._should_execute_agent(agent, interval)

            self._execute_schedule(should_execute_agent, interval_in_seconds, session, agent,
                                   agent_name)

        for agent in scheduled_agents:
            if self._can_remove_agent(agent, interval):
                agent.status = "COMPLETED"
                session.commit()

        session.close()

    def update_next_scheduled_time(self):
        now = datetime.now()

        session = Session()
        scheduled_agents = session.query(AgentSchedule).filter(
            AgentSchedule.start_time <= now, AgentSchedule.next_scheduled_time <= now,
            AgentSchedule.status == "SCHEDULED").all()

        for agent in scheduled_agents:
            if (now - agent.next_scheduled_time).total_seconds() < AgentScheduleHelper.AGENT_SCHEDULE_TIME_INTERVAL:
                continue
            if agent.recurrence_interval is not None:
                interval_in_seconds = parse_interval_to_seconds(agent.recurrence_interval)
                time_diff = now - agent.start_time
                num_intervals_passed = time_diff.total_seconds() // interval_in_seconds
                updated_next_scheduled_time = agent.start_time + timedelta(
                    seconds=(interval_in_seconds * (num_intervals_passed + 1)))
                agent.next_scheduled_time = updated_next_scheduled_time
            else:
                agent.status = "TERMINATED"
            session.commit()
        session.close()
        
    def _create_execution_name_for_scheduling(self, agent_id) -> str:
        session = Session()
        user_timezone = session.query(AgentConfiguration).filter(AgentConfiguration.key == "user_timezone",
                                                                 AgentConfiguration.agent_id == agent_id).first()

        if user_timezone and user_timezone.value:
            current_time = datetime.now().astimezone(pytz.timezone(user_timezone.value))
        else:
            current_time = datetime.now().astimezone(pytz.timezone('GMT'))

        timestamp = current_time.strftime(" %d %B %Y %H:%M")
        return f"Run{timestamp}"

    def _check_time_difference(agent, now):
        next_scheduled_time = agent.next_scheduled_time
        return (now - next_scheduled_time).total_seconds() > AgentScheduleHelper.AGENT_SCHEDULE_TIME_INTERVAL



    def _should_execute_agent(self, agent, interval):
        expiry_date = agent.expiry_date
        expiry_runs = agent.expiry_runs
        current_runs = agent.current_runs

        # If there's no interval or there are no restrictions on when or how many times an agent can run
        if not interval or (expiry_date is None and expiry_runs == -1):
            return True

        # Check if the agent's expiry date has not passed yet
        if expiry_date and datetime.now() < expiry_date:
            return True

        # Check if the agent has not yet run as many times as allowed
        if expiry_runs != -1 and current_runs < expiry_runs:
            return True

        # If none of the conditions to run the agent is met, return False (i.e., do not run the agent)
        return False


    def _can_remove_agent(self, agent, interval):
        expiry_date = agent.expiry_date
        expiry_runs = agent.expiry_runs
        current_runs = agent.current_runs

        # Calculate the next scheduled time only if an interval exists.
        next_scheduled = agent.next_scheduled_time + timedelta(seconds=parse_interval_to_seconds(interval)) if interval else None

        # If there's no interval, the agent can be removed
        if not interval:
            return True

        # If the agent's expiry date has not come yet and next schedule is before expiry date, it cannot be removed
        if expiry_date and datetime.now() < expiry_date and (next_scheduled is None or next_scheduled <= expiry_date):
            return False

        # If agent has not yet run as many times as allowed, it cannot be removed
        if expiry_runs != -1 and current_runs < expiry_runs:
            return False

        # If there are no restrictions on when or how many times an agent can run, it cannot be removed
        if expiry_date is None and expiry_runs == -1:
            return False

        # If none of the conditions to keep the agent is met, we return True (i.e., the agent can be removed)
        return True

    def _execute_schedule(self, should_execute_agent, interval_in_seconds, session, agent, agent_name):
        from superagi.jobs.scheduling_executor import ScheduledAgentExecutor
        if should_execute_agent:
            ScheduledAgentExecutor.execute_scheduled_agent(agent.agent_id, agent_name)
            agent.current_runs = agent.current_runs + 1

            if agent.recurrence_interval:
                next_scheduled_time = agent.next_scheduled_time + timedelta(seconds=interval_in_seconds)
                agent.next_scheduled_time = next_scheduled_time

            session.commit()

from sqlalchemy.orm import Session
from superagi.models.events import Event
from sqlalchemy.exc import SQLAlchemyError
from superagi.models.agent_execution import AgentExecution
from datetime import datetime
from sqlalchemy import Integer


class AnalyticsHelper:
    @classmethod
    def create_event(cls, session: Session, event_name: str, event_value: int,
                     json_property: dict, agent_id: int, org_id: int) -> Event:
        event = Event(
            event_name=event_name,
            event_value=event_value,
            json_property=json_property,
            agent_id=agent_id,
            org_id=org_id,
        )
        session.add(event)
        session.commit()
        return event

    @classmethod
    def calculate_run_completed_metrics(cls, session: Session) -> dict:
        result = {'total_tokens': 0, 'total_calls': 0, 'runs_completed': 0}

        try:
            query_result = session.query(Event).filter_by(event_name="run_completed").all()

            for res in query_result:
                if 'tokens_consumed' in res.json_property:
                    result['total_tokens'] += res.json_property['tokens_consumed']
                if 'calls' in res.json_property:
                    result['total_calls'] += res.json_property['calls']

                result['runs_completed'] += 1

            session.close()

        except SQLAlchemyError as e:
            print(str(e))

        return result

    @classmethod
    def fetch_agent_data(cls, session: Session) -> dict:
        agent_details_dict = {}
        models_used_dict = {}

        try:
            agent_created_events = session.query(Event).filter_by(event_name="agent_created").all()

            for event in agent_created_events:
                agent_id = event.agent_id
                agent_name = event.json_property['name']

                model_type = event.json_property.get('model', 'Unknown')  # Assume 'model' key in json_property, provide default as 'Unknown'

                agent_details_dict[agent_id] = {
                    "name": agent_name,
                    "agent_id": agent_id,
                    "runs_completed": 0,
                    "total_calls": 0,
                    "total_tokens": 0
                }

                if model_type in models_used_dict:
                    models_used_dict[model_type] += 1  # increment the count for this model
                else:
                    models_used_dict[model_type] = 1  # first time seeing this model, initialize with 1

            run_completed_events = session.query(Event).filter_by(event_name="run_completed").all()

            for event in run_completed_events:
                agent_id = event.agent_id

                if agent_id in agent_details_dict:
                    agent_details_dict[agent_id]['runs_completed'] += 1

                    if 'tokens_consumed' in event.json_property:
                        agent_details_dict[agent_id]['total_tokens'] += event.json_property['tokens_consumed']

                    if 'calls' in event.json_property:
                        agent_details_dict[agent_id]['total_calls'] += event.json_property['calls']

            session.close()

        except SQLAlchemyError as e:
            print(str(e))

        agent_details = list(agent_details_dict.values())
        models_used = [{"model": model, "agents": count} for model, count in models_used_dict.items()]

        return {'agent_details':agent_details, 'model_info':models_used}

    @classmethod
    def fetch_agent_runs(cls, agent_id: int, session: Session) -> list:
        agent_runs = []
        try:
            query_result_completed = session.query(Event).filter_by(event_name="run_completed", agent_id=agent_id).all()
            query_result_created = session.query(Event).filter_by(event_name="run_created", agent_id=agent_id).all()

            # create a dictionary of created_at times for run_created events
            created_dict = {run.json_property['run_id']: run.created_at for run in query_result_created}

            for run in query_result_completed:

                run_id = run.json_property['run_id']

                run_data = {
                    'name': run.json_property['name'],
                    'tokens_consumed': run.json_property['tokens_consumed'],
                    'calls': run.json_property['calls'],
                    'created_at': created_dict.get(run_id, None),  # fallback to None if run_id doesn't exist in created_dict
                    'updated_at': run.updated_at
                }

                agent_runs.append(run_data)

        except SQLAlchemyError as e:
            print(str(e))

        session.close()

        return agent_runs

    @classmethod
    def get_active_runs(cls, session: Session) -> list:
        running_executions = []
        try:
            start_events = session.query(Event).filter_by(event_name="run_created").all()
            completed_events = session.query(Event).filter_by(event_name="run_completed").all()

            completed_run_ids = [event.json_property['run_id'] for event in completed_events]

            for event in start_events:
                if event.json_property['run_id'] not in completed_run_ids:
                    agent_event = session.query(Event).filter_by(agent_id=event.agent_id, event_name="agent_created").first()
                    agent_name = agent_event.json_property['name'] if agent_event else 'Unknown'
                    execution_data = {
                        'name': event.json_property['name'],
                        'created_at': event.created_at,
                        'agent_name': agent_name
                    }
                    running_executions.append(execution_data)

        except SQLAlchemyError as e:
            print(str(e))
            return {"error": str(e)}
        finally:
            session.close()

        return running_executions

    @classmethod
    def calculate_tool_usage(cls, session: Session) -> list:
        tool_usage_dict = {}

        try:
            tool_used_events = session.query(Event).filter_by(event_name="tool_used").all()

            for event in tool_used_events:
                tool_name = event.json_property['tool_name']
                agent_id = event.agent_id

                if tool_name not in tool_usage_dict:
                    tool_usage_dict[tool_name] = {
                        "unique_agents": set(),
                        "total_usage": 0,
                    }

                tool_usage_dict[tool_name]["unique_agents"].add(agent_id)
                tool_usage_dict[tool_name]["total_usage"] += 1

            session.close()

        except SQLAlchemyError as e:
            print(str(e))

        tool_usage_metrics = [ { 'tool_name' : tool_name, 'unique_agents' : len(tool_data["unique_agents"]), 'total_usage' : tool_data["total_usage"]} for tool_name, tool_data in tool_usage_dict.items()]

        return tool_usage_metrics
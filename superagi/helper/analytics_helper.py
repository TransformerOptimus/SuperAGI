from sqlalchemy.orm import Session
from superagi.models.events import Event
from sqlalchemy.exc import SQLAlchemyError


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
        session.close()
        return event

    @classmethod
    def calculate_run_completed_metrics(cls, session: Session) -> dict:
        result = {'total_tokens': 0, 'total_calls': 0, 'runs_completed': 0}

        try:
            query_result = session.query(Event).filter_by(event_name="RUN COMPLETED").all()

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
            agent_created_events = session.query(Event).filter_by(event_name="AGENT CREATED").all()

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

            run_completed_events = session.query(Event).filter_by(event_name="RUN COMPLETED").all()

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
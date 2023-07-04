from typing import List, Dict, Tuple, Optional, Iterator
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
from superagi.models.events import Event
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging


class AnalyticsHelper:

    def __init__(self, session: Session):
        self.session = session

    def _run_query(self, query: Query) -> Iterator:
        try:
            return iter(query.yield_per(100).all())
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return iter([])

    def create_event(self, event_name: str, event_value: int, json_property: dict, agent_id: int, org_id: int) -> Optional[Event]:
        event = Event(
            event_name=event_name,
            event_value=event_value,
            json_property=json_property,
            agent_id=agent_id,
            org_id=org_id,
        )
        self.session.add(event)
        self.session.commit()
        return event

    def calculate_run_completed_metrics(self) -> Dict[str, int]:
        query_result = self._run_query(self.session.query(Event).filter_by(event_name="run_completed"))

        result = {'total_tokens': 0, 'total_calls': 0, 'runs_completed': 0}
        for res in query_result:
            result['total_tokens'] += res.json_property.get('tokens_consumed', 0)
            result['total_calls'] += res.json_property.get('calls', 0)
            result['runs_completed'] += 1

        return result

    def fetch_agent_data(self) -> Dict[str, List[Dict[str, int]]]:
        agent_created_events = self._run_query(self.session.query(Event).filter_by(event_name="agent_created"))
        run_completed_events = self._run_query(self.session.query(Event).filter_by(event_name="run_completed"))

        agent_details_dict, models_used_dict = {}, {}
        for event in agent_created_events:
            agent_id = event.agent_id
            agent_details_dict[agent_id] = {
                "name": event.json_property['name'],
                "agent_id": agent_id,
                "runs_completed": 0,
                "total_calls": 0,
                "total_tokens": 0
            }

            model = event.json_property.get('model', 'Unknown')
            models_used_dict[model] = models_used_dict.get(model, 0) + 1

        for event in run_completed_events:
            agent_id = event.agent_id
            if agent_id in agent_details_dict:
                agent_details_dict[agent_id]['runs_completed'] += 1
                agent_details_dict[agent_id]['total_tokens'] += event.json_property.get('tokens_consumed', 0)
                agent_details_dict[agent_id]['total_calls'] += event.json_property.get('calls', 0)

        agent_details = list(agent_details_dict.values())
        models_used = [{"model": model, "agents": count} for model, count in models_used_dict.items()]

        return {'agent_details': agent_details, 'model_info': models_used}

    def fetch_agent_runs(self, agent_id: int) -> List[Dict[str, int]]:
        query_result_completed = self._run_query(self.session.query(Event).filter_by(event_name="run_completed", agent_id=agent_id))
        query_result_created = self._run_query(self.session.query(Event).filter_by(event_name="run_created", agent_id=agent_id))

        created_dict = {run.json_property['run_id']: run.created_at for run in query_result_created}

        agent_runs = []
        for run in query_result_completed:
            run_id = run.json_property['run_id']
            created_at = created_dict.get(run_id)

            if created_at is not None:
                agent_runs.append({'name': run.json_property['name'],
                                    'tokens_consumed': run.json_property['tokens_consumed'],
                                    'calls': run.json_property['calls'],
                                    'created_at': created_at,
                                    'updated_at': run.updated_at})

        return agent_runs

    def get_active_runs(self) -> List[Dict[str, str]]:
        start_events = self._run_query(self.session.query(Event).filter_by(event_name="run_created"))
        completed_events = self._run_query(self.session.query(Event).filter_by(event_name="run_completed"))
        completed_run_ids = [event.json_property['run_id'] for event in completed_events]

        running_executions = []
        for event in start_events:
            if event.json_property['run_id'] not in completed_run_ids:
                agent_event = next(self._run_query(self.session.query(Event).filter_by(agent_id=event.agent_id, event_name="agent_created")), None)
                agent_name = agent_event.json_property['name'] if agent_event else 'Unknown'
                running_executions.append({'name': event.json_property['name'],'created_at': event.created_at, 'agent_name': agent_name})

        return running_executions

    def calculate_tool_usage(self) -> List[Dict[str, int]]:
        tool_used_events = self._run_query(self.session.query(Event).filter_by(event_name="tool_used"))
        tool_usage_dict = {}

        for event in tool_used_events:
            tool_name = event.json_property['tool_name']
            if tool_name not in tool_usage_dict:
                tool_usage_dict[tool_name] = {"unique_agents": set(), "total_usage": 0}

            tool_usage_dict[tool_name]["unique_agents"].add(event.agent_id)
            tool_usage_dict[tool_name]["total_usage"] += 1

        return [{'tool_name': tool_name, 'unique_agents': len(tool_data["unique_agents"]), 'total_usage': tool_data["total_usage"]} for tool_name, tool_data in tool_usage_dict.items()]
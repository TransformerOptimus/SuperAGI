from typing import List, Dict, Tuple, Optional, Iterator
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
from superagi.models.events import Event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, func
import logging

class AnalyticsHelper:

    def __init__(self, session: Session):
        self.session = session

    def _run_query(self, query: Query) -> Iterator:
         try:
            return iter(query.yield_per(100).all())
         except SQLAlchemyError as err:
            logging.error(f"Database error: {str(err)}")
            return iter([])

    def create_event(self, event_name: str, event_value: int, json_property: dict, agent_id: int, org_id: int) -> Optional[Event]:
        try:
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
        except SQLAlchemyError as err:
            logging.error(f"Error while creating event: {str(err)}")
            return None

    def calculate_run_completed_metrics(self) -> Dict[str, int]:
        metrics = {'total_tokens': 0, 'total_calls': 0, 'runs_completed': 0}
        subquery = self.session.query(Event).filter_by(event_name="run_completed").subquery()
        query = self.session.query(
            func.sum(text("(json_property->>'tokens_consumed')::int")).label('total_tokens'),
            func.sum(text("(json_property->>'calls')::int")).label('total_calls'),
            func.count(subquery.c.id).label('runs_completed'),
        )
        result = query.one()

        metrics.update({
            'total_tokens': result.total_tokens or 0,
            'total_calls': result.total_calls or 0,
            'runs_completed': result.runs_completed
        })

        return metrics

    def fetch_agent_data(self) -> Dict[str, List[Dict[str, int]]]:
        agent_subquery = self.session.query(
            Event.agent_id,
            Event.json_property['agent_name'].label('agent_name'),
            Event.json_property['model'].label('model')
        ).filter_by(event_name="agent_created").subquery()

        run_subquery = self.session.query(
            Event.agent_id,
            func.sum(text("(json_property->>'tokens_consumed')::int")).label('total_tokens'),
            func.sum(text("(json_property->>'calls')::int")).label('total_calls'),
            func.count(Event.id).label('runs_completed'),
        ).filter_by(event_name="run_completed").group_by(Event.agent_id).subquery()

        query = self.session.query(
            agent_subquery.c.agent_id,
            agent_subquery.c.agent_name,
            agent_subquery.c.model,
            run_subquery.c.total_tokens,
            run_subquery.c.total_calls,
            run_subquery.c.runs_completed
        ).outerjoin(run_subquery, run_subquery.c.agent_id == agent_subquery.c.agent_id)

        result = query.all()

        agent_details = [{
            "name": row.agent_name,
            "agent_id": row.agent_id,
            "runs_completed": row.runs_completed if row.runs_completed else 0,
            "total_calls": row.total_calls if row.total_calls else 0,
            "total_tokens": row.total_tokens if row.total_tokens else 0,
        } for row in result]

        models_used = self.session.query(
            agent_subquery.c.model,
            func.count(agent_subquery.c.agent_id).label('agents')
        ).group_by(agent_subquery.c.model).all()

        model_info = [{"model": row.model, "agents": row.agents} for row in models_used]

        return {'agent_details': agent_details, 'model_info': model_info}

    def fetch_agent_runs(self, agent_id: int) -> List[Dict[str, int]]:
        agent_runs = []
        completed_subquery = self.session.query(
            Event.json_property['agent_execution_id'].label('completed_agent_execution_id'),
            Event.json_property['tokens_consumed'].label('tokens_consumed'),
            Event.json_property['calls'].label('calls'),
            Event.updated_at
        ).filter_by(event_name="run_completed", agent_id=agent_id).subquery()

        created_subquery = self.session.query(
            Event.json_property['agent_execution_id'].label('created_agent_execution_id'),
            Event.json_property['agent_execution_name'].label('agent_execution_name'),
            Event.created_at
        ).filter_by(event_name="run_created", agent_id=agent_id).subquery()

        query = self.session.query(
            created_subquery.c.agent_execution_name,
            completed_subquery.c.tokens_consumed,
            completed_subquery.c.calls,
            created_subquery.c.created_at,
            completed_subquery.c.updated_at
        ).join(completed_subquery, completed_subquery.c.completed_agent_execution_id == created_subquery.c.created_agent_execution_id)

        result = query.all()

        agent_runs = [{
            'name': row.agent_execution_name,
            'tokens_consumed': int(row.tokens_consumed) if row.tokens_consumed else 0,
            'calls': int(row.calls) if row.calls else 0,
            'created_at': row.created_at,
            'updated_at': row.updated_at
        } for row in result]

        return agent_runs


    def get_active_runs(self) -> List[Dict[str, str]]:
        running_executions = []
        completed_subquery = self.session.query(
            Event.json_property['agent_execution_id'].label('agent_execution_id'),
        ).filter_by(event_name="run_completed").subquery()

        start_subquery = self.session.query(
            Event.json_property['agent_execution_id'].label('agent_execution_id'),
            Event.json_property['agent_execution_name'].label('agent_execution_name'),
            Event.created_at,
            Event.agent_id
        ).filter_by(event_name="run_created").subquery()

        agent_created_subquery = self.session.query(
            Event.json_property['agent_name'].label('agent_name'),
            Event.agent_id
        ).filter_by(event_name="agent_created").subquery()

        query = self.session.query(
            start_subquery.c.agent_execution_name,
            start_subquery.c.created_at,
            agent_created_subquery.c.agent_name
        ).select_from(start_subquery)

        query = query.outerjoin(completed_subquery, start_subquery.c.agent_execution_id == completed_subquery.c.agent_execution_id).filter(completed_subquery.c.agent_execution_id == None)

        query = query.join(agent_created_subquery, start_subquery.c.agent_id == agent_created_subquery.c.agent_id)

        result = query.all()

        running_executions = [{
            'name': row.agent_execution_name,
            'created_at': row.created_at,
            'agent_name': row.agent_name or 'Unknown',
        } for row in result]

        return running_executions

    def calculate_tool_usage(self) -> List[Dict[str, int]]:
        tool_usage = []
        tool_used_subquery = self.session.query(
            Event.json_property['tool_name'].label('tool_name'),
            Event.agent_id
        ).filter_by(event_name="tool_used").subquery()

        agent_count = self.session.query(
            tool_used_subquery.c.tool_name,
            func.count(func.distinct(tool_used_subquery.c.agent_id)).label('unique_agents')
        ).group_by(tool_used_subquery.c.tool_name).subquery()

        total_usage = self.session.query(
            tool_used_subquery.c.tool_name,
            func.count(tool_used_subquery.c.tool_name).label('total_usage')
        ).group_by(tool_used_subquery.c.tool_name).subquery()

        query = self.session.query(
            agent_count.c.tool_name,
            agent_count.c.unique_agents,
            total_usage.c.total_usage
        ).join(total_usage, total_usage.c.tool_name == agent_count.c.tool_name)

        result = query.all()

        tool_usage = [{
            'tool_name': row.tool_name,
            'unique_agents': row.unique_agents,
            'total_usage': row.total_usage
        } for row in result]

        return tool_usage
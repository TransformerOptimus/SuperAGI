from typing import List, Dict, Union
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session
from sqlalchemy import Integer
from fastapi import HTTPException
from superagi.models.events import Event
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit
from sqlalchemy import or_
from sqlalchemy.sql import label
from superagi.models.agent_config import AgentConfiguration
import pytz

class ToolsHandler:
    def __init__(self, session: Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id

    def get_tool_and_toolkit(self):
        tools_and_toolkits = self.session.query(
            Tool.name.label('tool_name'), Toolkit.name.label('toolkit_name')).join(
            Toolkit, Tool.toolkit_id == Toolkit.id).all()

        return {item.tool_name: item.toolkit_name for item in tools_and_toolkits}

    def calculate_tool_usage(self) -> List[Dict[str, int]]:
        tool_usage = []
        tool_used_subquery = self.session.query(
            Event.event_property['tool_name'].label('tool_name'),
            Event.agent_id
        ).filter_by(event_name="tool_used", org_id=self.organisation_id).subquery()

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
            total_usage.c.total_usage,
        ).join(total_usage, total_usage.c.tool_name == agent_count.c.tool_name)

        tool_and_toolkit = self.get_tool_and_toolkit()

        result = query.all()

        tool_usage = [{
            'tool_name': row.tool_name,
            'unique_agents': row.unique_agents,
            'total_usage': row.total_usage,
            'toolkit': tool_and_toolkit.get(row.tool_name, None)
        } for row in result]

        return tool_usage
    
    def get_tool_usage_by_name(self, tool_name: str) -> Dict[str, Dict[str, int]]:
        is_tool_name_valid = self.session.query(Tool).filter_by(name=tool_name).first()

        if not is_tool_name_valid:
            raise HTTPException(status_code=404, detail="Tool not found")
        formatted_tool_name = tool_name.lower().replace(" ", "")

        tool_used_event = self.session.query(
            Event.event_property['tool_name'].label('tool_name'), 
            func.count(Event.id).label('tool_calls'),
            func.count(distinct(Event.agent_id)).label('tool_unique_agents')
        ).filter(
            Event.event_name == 'tool_used', 
            Event.org_id == self.organisation_id,
            Event.event_property['tool_name'].astext == formatted_tool_name
        ).group_by(
            Event.event_property['tool_name']
        ).first()

        if tool_used_event is None:
            return {}

        tool_data = {
                'tool_calls': tool_used_event.tool_calls,
                'tool_unique_agents': tool_used_event.tool_unique_agents
            }

        return tool_data

    def get_tool_events_by_name(self, tool_name: str) -> List[Dict[str, Union[str, int, List[str]]]]:    

        is_tool_name_valid = self.session.query(Tool).filter_by(name=tool_name).first()

        if not is_tool_name_valid:
            raise HTTPException(status_code=404, detail="Tool not found")

        formatted_tool_name = tool_name.lower().replace(" ", "")

        event_tool_used = self.session.query(
            Event.agent_id,
            label('created_at', func.max(Event.created_at)),
            label('event_name', func.max(Event.event_name))
        ).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'tool_used',
            Event.event_property['tool_name'].astext == formatted_tool_name
        ).group_by(Event.agent_id).subquery()

        event_run = self.session.query(
            Event.agent_id,
            label('tokens_consumed', func.sum(Event.event_property['tokens_consumed'].astext.cast(Integer))),
            label('calls', func.sum(Event.event_property['calls'].astext.cast(Integer)))
        ).filter(
            Event.org_id == self.organisation_id,
            or_(Event.event_name == 'run_completed', Event.event_name == 'run_iteration_limit_crossed')
        ).group_by(Event.agent_id).subquery()

        event_run_created = self.session.query(
            Event.agent_id,
            label('agent_execution_name', func.max(Event.event_property['agent_execution_name'].astext))
        ).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'run_created'
        ).group_by(Event.agent_id).subquery()

        event_agent_created = self.session.query(
            Event.agent_id,
            label('agent_name', func.max(Event.event_property['agent_name'].astext)),
            label('model', func.max(Event.event_property['model'].astext))
        ).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'agent_created'
        ).group_by(Event.agent_id).subquery()

        other_tools = self.session.query(
            Event.agent_id,
            func.array_agg(Event.event_property['tool_name'].astext).label('other_tools')
        ).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'tool_used',
            Event.event_property['tool_name'].astext != formatted_tool_name
        ).group_by(Event.agent_id).subquery()

        result = self.session.query(
            event_tool_used.c.agent_id,
            event_tool_used.c.created_at,
            event_tool_used.c.event_name,
            event_run.c.tokens_consumed,
            event_run.c.calls,
            event_run_created.c.agent_execution_name,
            event_agent_created.c.agent_name,
            event_agent_created.c.model,
            other_tools.c.other_tools
        ).join(
            event_run, event_tool_used.c.agent_id == event_run.c.agent_id
        ).join(
            event_run_created, event_tool_used.c.agent_id == event_run_created.c.agent_id
        ).join(
            event_agent_created, event_tool_used.c.agent_id == event_agent_created.c.agent_id
        ).join(
            other_tools, event_tool_used.c.agent_id == other_tools.c.agent_id, isouter=True
        ).all()

        user_timezone = AgentConfiguration.get_agent_config_by_key_and_agent_id(session= self.session,key= 'user_timezone', agent_id= Event.agent_id)
        if user_timezone.value is None:
            user_timezone.value = 'GMT'

        return [{
            'agent_id': row.agent_id,
            'created_at': row.created_at.astimezone(pytz.timezone(user_timezone.value)).strftime("%d %B %Y %H:%M"),
            'event_name': row.event_name,
            'tokens_consumed': row.tokens_consumed,
            'calls': row.calls,
            'agent_execution_name': row.agent_execution_name,
            'agent_name': row.agent_name,
            'model': row.model,
            'other_tools': row.other_tools
        } for row in result]
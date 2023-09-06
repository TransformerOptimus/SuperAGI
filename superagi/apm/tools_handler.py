from typing import List, Dict, Union
from sqlalchemy import func, distinct, and_
from sqlalchemy.orm import Session
from sqlalchemy import Integer
from fastapi import HTTPException
from superagi.models.events import Event
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit
from sqlalchemy import or_
from sqlalchemy.sql import label
from datetime import datetime
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

        tool_events = self.session.query(Event).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'tool_used',
            Event.event_property['tool_name'].astext == formatted_tool_name
        ).all()

        tool_events = [te for te in tool_events if 'agent_execution_id' in te.event_property]

        event_runs = self.session.query(Event).filter(
            Event.org_id == self.organisation_id,
            or_(Event.event_name == 'run_completed', Event.event_name == 'run_iteration_limit_crossed')
        ).all()

        agent_created_events = self.session.query(Event).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'agent_created'
        ).all()

        results = []

        for tool_event in tool_events:
            agent_execution_id = tool_event.event_property['agent_execution_id']

            event_run = next((er for er in event_runs if er.agent_id == tool_event.agent_id and er.event_property['agent_execution_id'] == agent_execution_id), None)
            agent_created_event = next((ace for ace in agent_created_events if ace.agent_id == tool_event.agent_id), None)
            try:
                user_timezone = AgentConfiguration.get_agent_config_by_key_and_agent_id(session=self.session, key='user_timezone', agent_id=tool_event.agent_id)
                if user_timezone and user_timezone.value != 'None':
                    tz = pytz.timezone(user_timezone.value)
                else:
                    tz = pytz.timezone('GMT')       
            except AttributeError:
                tz = pytz.timezone('GMT')

            if event_run and agent_created_event:
                actual_time = tool_event.created_at.astimezone(tz).strftime("%d %B %Y %H:%M")
                other_tools_events = self.session.query(
                    Event
                ).filter(
                    Event.org_id == self.organisation_id,
                    Event.event_name == 'tool_used',
                    Event.event_property['tool_name'].astext != formatted_tool_name,
                    Event.agent_id == tool_event.agent_id, 
                    Event.id.between(tool_event.id, event_run.id)
                ).all()

                other_tools = [ote.event_property['tool_name'] for ote in other_tools_events]

                result_dict = {
                    'created_at': actual_time,
                    'agent_execution_id': agent_execution_id,
                    'tokens_consumed': event_run.event_property['tokens_consumed'],
                    'calls': event_run.event_property['calls'],
                    'agent_execution_name': event_run.event_property['name'],
                    'other_tools': other_tools,
                    'agent_name': agent_created_event.event_property['agent_name'],
                    'model': agent_created_event.event_property['model']
                }

                if agent_execution_id not in [i['agent_execution_id'] for i in results]:
                    results.append(result_dict)

        results = sorted(results, key=lambda x: datetime.strptime(x['created_at'], '%d %B %Y %H:%M'), reverse=True)

        return results
    
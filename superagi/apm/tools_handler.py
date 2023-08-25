from typing import List, Dict
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import Integer
from collections import defaultdict
from fastapi import HTTPException
from superagi.models.events import Event
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit


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
    

    def get_tool_wise_usage(self) -> Dict[str, Dict[str, int]]:

        tool_agents = defaultdict(set)
        
        tool_used_events = self.session.query(
            Event.agent_id,
            Event.event_property['tool_name'].label('tool_name')
        ).filter(Event.event_name == 'tool_used', Event.org_id == self.organisation_id)
        
        agent_tool_map = defaultdict(list)
        tool_calls = defaultdict(int)
    
        for event in tool_used_events:
            agent_tool_map[event.agent_id].append(event.tool_name)
            tool_agents[event.tool_name].add(event.agent_id)
            tool_calls[event.tool_name] += 1
                
        tool_agents_count = {tool: len(agents) for tool, agents in tool_agents.items()}
        
        return {
            'tool_calls': dict(tool_calls),
            'tool_unique_agents': tool_agents_count
        }
    

    def get_tool_events_name(self, tool_name: str):

        is_tool_name_valid = self.session.query(Tool).filter_by(name=tool_name).first()

        if not is_tool_name_valid:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        formatted_tool_name = tool_name.lower().replace(" ", "")

        all_events = self.session.query(Event).filter(Event.org_id == self.organisation_id).all()
        unique_agent_ids = {event.agent_id for event in all_events if 'tool_name' in event.event_property and event.event_property['tool_name'] == formatted_tool_name}

        result_list = []

        for agent_id in unique_agent_ids:
            agent_specific_events = [event for event in all_events if event.agent_id == agent_id]
            agent_dict = {}

            for event in agent_specific_events:
                event_property = event.event_property

                if event.event_name == 'tool_used':
                    if 'tool_name' in event_property and event_property['tool_name'] != formatted_tool_name:
                        other_tools = agent_dict.get('other_tools', [])
                        other_tools.append(event_property['tool_name'])
                        agent_dict['other_tools'] = other_tools
                    elif event_property['tool_name'] == formatted_tool_name:
                        agent_dict['created_at'] = event.created_at
                        agent_dict['event_name'] = event.event_name

                elif event.event_name == 'run_completed' or event.event_name == 'run_iteration_limit_crossed':
                    agent_dict['tokens_consumed'] = agent_dict.get('tokens_consumed', 0) + event_property.get('tokens_consumed', 0)
                    agent_dict['calls'] = agent_dict.get('calls', 0) + event_property.get('calls', 0)
                    
                elif event.event_name == 'run_created':
                    agent_dict['agent_execution_name'] = event_property.get('agent_execution_name', '')
                    
                elif event.event_name == 'agent_created':
                    agent_dict['agent_name'] = event_property.get('agent_name', '')
                    agent_dict['model'] = event_property.get('model', '')

            result_list.append(agent_dict)

        return result_list

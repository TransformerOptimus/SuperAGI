from typing import List, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

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
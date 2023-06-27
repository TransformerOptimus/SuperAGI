from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from superagi.tools.jira.create_issue import CreateIssueTool
from superagi.tools.jira.edit_issue import EditIssueTool
from superagi.tools.jira.get_projects import GetProjectsTool
from superagi.tools.jira.search_issues import SearchJiraTool


class JiraToolkit(BaseToolkit, ABC):
    name: str = "Jira Toolkit"
    description: str = "Toolkit containing tools for Jira integration"

    def get_tools(self) -> List[BaseTool]:
        return [
            CreateIssueTool(),
            EditIssueTool(),
            GetProjectsTool(),
            SearchJiraTool(),
        ]

    def get_env_keys(self) -> List[str]:
        return [
            "JIRA_INSTANCE_URL",
            "JIRA_USERNAME",
            "JIRA_API_TOKEN",
        ]

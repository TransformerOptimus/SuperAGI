from typing import Type, List

from pydantic import BaseModel, Field

from superagi.tools.jira.tool import JiraIssueSchema, JiraTool

class GetProjectsSchema(BaseModel):
    pass


class GetProjectsTool(JiraTool):
    """
    Get Jira Projects tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "GetJiraProjects"
    description = "This tool is a wrapper around atlassian-python-api's Jira project API. Useful in fetching all the projects accessible to the user, discovering the total count of projects, or utilizing it as an interim step during project-based searches."
    args_schema: Type[GetProjectsSchema] = GetProjectsSchema

    def parse_projects(self, projects: List[dict]) -> List[dict]:
        parsed = []
        for project in projects:
            parsed.append({"id": project.id, "key": project.key, "name": project.name})
        return parsed

    def _execute(self) -> str:
        """
        Execute the get projects tool.

        Returns:
            Found <count> projects: <projects>
        """
        jira = self.build_jira_instance()
        projects = jira.projects()
        parsed_projects = self.parse_projects(projects)
        parsed_projects_str = (
                "Found " + str(len(parsed_projects)) + " projects:\n" + str(parsed_projects)
        )
        return parsed_projects_str
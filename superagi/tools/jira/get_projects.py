from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.jira.tool import JiraIssueSchema, JiraTool

class GetProjectsSchema(BaseModel):
    pass


class GetProjectsTool(JiraTool):
    name = "GetProjects"
    description = "This tool is a wrapper around atlassian-python-api's Jira project API. Useful in fetching all the projects accessible to the user, discovering the total count of projects, or utilizing it as an interim step during project-based searches."
    args_schema: Type[GetProjectsSchema] = GetProjectsSchema
    def project(self) -> str:
        projects = self.jira.projects()
        parsed_projects = self.parse_projects(projects)
        parsed_projects_str = (
                "Found " + str(len(parsed_projects)) + " projects:\n" + str(parsed_projects)
        )
        return parsed_projects_str
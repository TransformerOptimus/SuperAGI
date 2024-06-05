from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.jira.tool import JiraTool, JiraIssueSchema


class CreateIssueSchema(BaseModel):
    """
    Schema for creating Jira issues.

    Attributes:
        summary (str): A short, descriptive summary of the issue.
        project (str): The key of the project where the issue will be created.
        description (str): Detailed description of the issue.
        issuetype (str): Type of the issue (Epic, Story, Task, Sub-task).
        priority (str): Priority of the issue (default: "Low").
        epic_name (str): Name of the Epic (optional, applicable for Story, Task, and Sub-task).
        parent_key (str): Key of the parent issue (optional, applicable for Sub-task).

    Examples:
        An example payload to create a Task:
        {
            "summary": "Task for project X",
            "project": "PROJECTX",
            "description": "This task involves implementing feature Y.",
            "issuetype": "Task",
            "priority": "High"
        }

        An example payload to create a Sub-task:
        {
            "summary": "Sub-task for Task ABC-123",
            "project": "PROJECTX",
            "description": "This sub-task is part of the larger task ABC-123.",
            "issuetype": "Sub-task",
            "parent_key": "ABC-123"
        }
    """
    summary: str
    project: str
    description: str
    issuetype: str
    priority: str = "Low"
    epic_name: str = ""  # For Story, Task, and Sub-task issues
    parent_key: str = ""  # For Sub-task issues


class CreateIssueTool(JiraTool):
    """
    Create Jira Issue tool.

    Attributes:
        name (str): The name of the tool.
        description (str): Description of the tool.
        args_schema (Type): The argument schema for the tool.
    """
    name = "CreateJiraIssue"
    description = "Create a new Jira issue, supporting Epic, Story, Task, and Sub-task types."
    args_schema: Type[CreateIssueSchema] = CreateIssueSchema

    def _execute(self, summary: str, project: str, description: str, issuetype: str, priority: str = "Low", epic_name: str = "", parent_key: str = ""):
        """
        Execute the create issue tool.

        Args:
            summary (str): Summary of the issue.
            project (str): Project key.
            description (str): Description of the issue.
            issuetype (str): Issue type (Epic, Story, Task, Sub-task).
            priority (str): Priority of the issue (default: "Low").
            epic_name (str): Name of the Epic (optional, applicable for Story, Task, and Sub-task).
            parent_key (str): Key of the parent issue (optional, applicable for Sub-task).

        Returns:
            The success message mentioning the key of the created issue.
        """
        jira = self.build_jira_instance()

        if issuetype.lower() == "epic":
            # Create Epic
            fields = {"project": {"key": project}, "summary": summary, "description": description, "issuetype": {"name": "Epic"}, "priority": {"name": priority}}
            new_issue = jira.create_issue(fields=fields)
        elif issuetype.lower() == "story":
            # Create Story
            epic_link = self._get_epic_link_by_name(jira, epic_name)
            fields = {"project": {"key": project}, "summary": summary, "description": description, "issuetype": {"name": "Story"}, "priority": {"name": priority}, "customfield_10006": epic_link}
            new_issue = jira.create_issue(fields=fields)
        elif issuetype.lower() == "task":
            # Create Task
            fields = {"project": {"key": project}, "summary": summary, "description": description, "issuetype": {"name": "Task"}, "priority": {"name": priority}}
            new_issue = jira.create_issue(fields=fields)
        elif issuetype.lower() == "sub-task":
            # Create Sub-task
            parent_issue = jira.issue(parent_key)
            fields = {"project": {"key": project}, "summary": summary, "description": description, "issuetype": {"name": "Sub-task"}, "parent": {"key": parent_key}, "priority": {"name": priority}}
            new_issue = jira.create_issue(fields=fields)
        else:
            raise ValueError(f"Unsupported issue type: {issuetype}")

        return f"Issue '{new_issue.key}' created successfully!"

    def _get_epic_link_by_name(self, jira, epic_name):
        # Helper method to get Epic Link by Epic name
        # You can customize this method based on your Jira configuration
        # For example, you might use JQL to search for the Epic by name
        return None  # Replace with actual implementation


# The CreateEpicTool, CreateStoryTool, and CreateTaskTool remain unchanged.
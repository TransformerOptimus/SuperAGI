import json
from typing import Type, Dict, List

from pydantic import Field, BaseModel

from superagi.helper.token_counter import TokenCounter
from superagi.tools.jira.tool import JiraTool


class SearchIssueSchema(BaseModel):
    query: str = Field(
        ...,
        description="JQL query string to search issues. For example, to find all the issues in project \"Test\" assigned to the me, you would pass in the following string: project = Test AND assignee = currentUser() or to find issues with summaries that contain the word \"test\", you would pass in the following string: summary ~ 'test'.",
    )


class SearchJiraTool(JiraTool):
    """
    Search Jira Issues tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "SearchJiraIssues"
    description = "This tool is a wrapper around atlassian-python-api's Jira jql API, useful when you need to search for Jira issues."
    args_schema: Type[SearchIssueSchema] = SearchIssueSchema

    def _execute(self, query: str) -> str:
        """
        Execute the search issues tool.

        Args:
            query : JQL query string to search issues. For example, to find all the issues in project "Test"
        assigned to, you would pass in the following string: project = Test AND assignee = currentUser() or to
        find issues with summaries that contain the word "test", you would pass in the following string: summary ~
        'test'.

        Returns:
            The list of issues matching the query.
        """
        jira = self.build_jira_instance()
        issues = jira.search_issues(query)
        parsed_issues = self.parse_issues(issues)
        parsed_issues_str = (
                "Found " + str(len(parsed_issues)) + " issues:\n" + str(parsed_issues)
        )
        return parsed_issues_str

    def parse_issues(self, issues: Dict) -> List[dict]:
        """
        Parse the issues returned by the Jira API.

        Args:
            issues : Dictionary of issues returned by the Jira API.

        Returns:
            List of parsed issues.
        """
        parsed = []
        for issue in issues["issues"]:
            key = issue.key
            summary = issue.fields.summary
            created = issue.fields.created[0:10]
            priority = issue.fields.priority.name
            status = issue.fields.status.name
            try:
                assignee = issue.fields.assignee.displayName
            except Exception:
                assignee = "None"
            rel_issues = {}
            for related_issue in issue.fields.issuelinks:
                if "inwardIssue" in related_issue.keys():
                    rel_type = related_issue["type"]["inward"]
                    rel_key = related_issue["inwardIssue"]["key"]
                    rel_summary = related_issue["inwardIssue"]["fields"]["summary"]
                if "outwardIssue" in related_issue.keys():
                    rel_type = related_issue["type"]["outward"]
                    rel_key = related_issue["outwardIssue"]["key"]
                    rel_summary = related_issue["outwardIssue"]["fields"]["summary"]
                rel_issues = {"type": rel_type, "key": rel_key, "summary": rel_summary}
            parsed.append(
                {
                    "key": key,
                    "summary": summary,
                    "created": created,
                    "assignee": assignee,
                    "priority": priority,
                    "status": status,
                    "related_issues": rel_issues,
                }
            )
            if TokenCounter.count_text_tokens(json.dumps(parsed)) > self.max_token_limit:
                break
        return parsed

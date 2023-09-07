import ast
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.github_helper import GithubHelper
from superagi.helper.json_cleaner import JsonCleaner
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent import Agent
from superagi.tools.base_tool import BaseTool


class GithubReviewPullRequestSchema(BaseModel):
    repository_name: str = Field(
        ...,
        description="Repository name in which file hase to be added",
    )
    repository_owner: str = Field(
        ...,
        description="Owner of the github repository",
    )
    pull_request_number: int = Field(
        ...,
        description="Pull request number",
    )


class GithubReviewPullRequest(BaseTool):
    """
    Reviews the github pull request and adds comments inline

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name: str = "Github Review Pull Request"
    args_schema: Type[BaseModel] = GithubReviewPullRequestSchema
    description: str = "Add pull request for the github repository"
    agent_id: int = None
    agent_execution_id: int = None

    def _execute(self, repository_name: str, repository_owner: str, pull_request_number: int) -> str:
        """
        Execute the add file tool.

        Args:
            repository_name: The name of the repository to add file to.
            repository_owner: Owner of the GitHub repository.
            pull_request_number: pull request number

        Returns:
            Pull request success message if pull request is created successfully else error message.
        """
        try:
            github_access_token = self.get_tool_config("GITHUB_ACCESS_TOKEN")
            github_username = self.get_tool_config("GITHUB_USERNAME")
            github_helper = GithubHelper(github_access_token, github_username)

            pull_request_content = github_helper.get_pull_request_content(repository_owner, repository_name,
                                                                          pull_request_number)
            latest_commit_id = github_helper.get_latest_commit_id_of_pull_request(repository_owner, repository_name,
                                                                                  pull_request_number)

            pull_request_arr = pull_request_content.split("diff --git")
            organisation = Agent.find_org_by_agent_id(session=self.toolkit_config.session, agent_id=self.agent_id)

            model_token_limit = TokenCounter(session=self.toolkit_config.session,
                                       organisation_id=organisation.id).token_limit(self.llm.get_model())
            pull_request_arr_parts = self.split_pull_request_content_into_multiple_parts(model_token_limit, pull_request_arr)
            for content in pull_request_arr_parts:
                self.run_code_review(github_helper, content, latest_commit_id, organisation, pull_request_number,
                                     repository_name, repository_owner)
            return "Added comments to the pull request:" + str(pull_request_number)
        except Exception as err:
            return f"Error: Unable to add comments to the pull request {err}"

    def run_code_review(self, github_helper, content, latest_commit_id, organisation, pull_request_number,
                        repository_name, repository_owner):
        prompt = PromptReader.read_tools_prompt(__file__, "code_review.txt")
        prompt = prompt.replace("{{DIFF_CONTENT}}", content)
        messages = [{"role": "system", "content": prompt}]
        total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        token_limit = TokenCounter(session=self.toolkit_config.session,
                                   organisation_id=organisation.id).token_limit(self.llm.get_model())
        result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))
        response = result["content"]
        if response.startswith("```") and response.endswith("```"):
            response = "```".join(response.split("```")[1:-1])
        response = JsonCleaner.extract_json_section(response)
        comments = ast.literal_eval(response)

        # Add comments in the pull request
        for comment in comments['comments']:
            line_number = self.get_exact_line_number(content, comment["file_path"], comment["line"])
            github_helper.add_line_comment_to_pull_request(repository_owner, repository_name, pull_request_number,
                                                           latest_commit_id, comment["file_path"], line_number,
                                                           comment["comment"])

    def split_pull_request_content_into_multiple_parts(self, model_token_limit: int, pull_request_arr):
        pull_request_arr_parts = []
        current_part = ""
        for part in pull_request_arr:
            total_tokens = TokenCounter.count_message_tokens([{"role": "user", "content": current_part}],
                                                             self.llm.get_model())
            # we are using 60% of the model token limit
            if total_tokens >= model_token_limit * 0.6:
                # Add the current part to pull_request_arr_parts and reset current_sum and current_part
                pull_request_arr_parts.append(current_part)
                current_part = "diff --git" + part
            else:
                current_part += "diff --git" + part

        pull_request_arr_parts.append(current_part)
        return pull_request_arr_parts

    def get_exact_line_number(self, diff_content, file_path, line_number):
        last_content = diff_content[diff_content.index(file_path):]
        last_content = last_content[last_content.index('@@'):]
        return self.find_position_in_diff(last_content, line_number)

    def find_position_in_diff(self, diff_content, target_line):
        # Split the diff by lines and initialize variables
        diff_lines = diff_content.split('\n')
        position = 0
        current_file_line_number = 0

        # Loop through each line in the diff
        for line in diff_lines:
            position += 1  # Increment position for each line
            if line.startswith('@@'):
                # Reset the current file line number when encountering a new hunk
                current_file_line_number = int(line.split('+')[1].split(',')[0]) - 1
            elif not line.startswith('-'):
                # Increment the current file line number for lines that are not deletions
                current_file_line_number += 1
            if current_file_line_number >= target_line:
                # Return the position when the target line number is reached
                return position
        return position

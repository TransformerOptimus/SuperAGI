import time
from typing import Tuple, List

from superagi.config.config import get_config
from superagi.helper.token_counter import TokenCounter
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.types.common import BaseMessage
from superagi.models.agent import Agent


class AgentLlmMessageBuilder:
    """Agent message builder for LLM agent."""
    def __init__(self, session, llm_model: str, agent_id: int, agent_execution_id: int):
        self.session = session
        self.llm_model = llm_model
        self.agent_id = agent_id
        self.agent_execution_id = agent_execution_id
        self.organisation = Agent.find_org_by_agent_id(self.session, self.agent_id)

    def build_agent_messages(self, prompt: str, agent_feeds: list, history_enabled=False,
                             completion_prompt: str = None):
        """ Build agent messages for LLM agent.

        Args:
            prompt (str): The prompt to be used for generating the agent messages.
            agent_feeds (list): The list of agent feeds.
            history_enabled (bool): Whether to use history or not.
            completion_prompt (str): The completion prompt to be used for generating the agent messages.
        """
        print("88888888888888888888888888888888")
        token_limit = TokenCounter(session=self.session, organisation_id=self.organisation.id).token_limit(self.llm_model)
        max_output_token_limit = int(get_config("MAX_TOOL_TOKEN_LIMIT", 800))
        messages = [{"role": "system", "content": prompt}]
        print("88888888888888888888888888888888")
        if history_enabled:
            messages.append({"role": "system", "content": f"The current time and date is {time.strftime('%c')}"})
            base_token_limit = TokenCounter(session=self.session, organisation_id=self.organisation.id).count_message_tokens(messages, self.llm_model)
            full_message_history = [{'role': role, 'content': feed} for role, feed in agent_feeds]
            past_messages, current_messages = self._split_history(full_message_history,
                                                                token_limit - base_token_limit - max_output_token_limit)
            print("88888888888888888888888888888888")
            for history in current_messages:
                messages.append({"role": history["role"], "content": history["content"]})
            messages.append({"role": "user", "content": completion_prompt})

        # insert initial agent feeds
        self._add_initial_feeds(agent_feeds, messages)
        return messages

    def _split_history(self, history: List, pending_token_limit: int) -> Tuple[List[BaseMessage], List[BaseMessage]]:
        hist_token_count = 0
        i = len(history)
        for message in reversed(history):
            token_count = TokenCounter(session=self.session, organisation_id=self.organisation.id).count_message_tokens([{"role": message["role"], "content": message["content"]}],
                                                            self.llm_model)
            hist_token_count += token_count
            if hist_token_count > pending_token_limit:
                return history[:i], history[i:]
            i -= 1
        return [], history

    def _add_initial_feeds(self, agent_feeds: list, messages: list):
        if agent_feeds:
            return
        for message in messages:
            agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_execution_id,
                                                      agent_id=self.agent_id,
                                                      feed=message["content"],
                                                      role=message["role"],
                                                      feed_group_id="DEFAULT")
            self.session.add(agent_execution_feed)
            self.session.commit()

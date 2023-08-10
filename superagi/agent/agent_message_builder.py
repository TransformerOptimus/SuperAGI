import time
from typing import Tuple, List
from sqlalchemy import asc

from superagi.config.config import get_config
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.types.common import BaseMessage
from superagi.models.agent_execution_config import AgentExecutionConfiguration


class AgentLlmMessageBuilder:
    """Agent message builder for LLM agent."""
    def __init__(self, session, llm, agent_id: int, agent_execution_id: int):
        self.session = session
        self.llm = llm
        self.llm_model = llm.get_model()
        self.agent_id = agent_id
        self.agent_execution_id = agent_execution_id

    def build_agent_messages(self, prompt: str, agent_feeds: list, history_enabled=False,
                             completion_prompt: str = None):
        """ Build agent messages for LLM agent.

        Args:
            prompt (str): The prompt to be used for generating the agent messages.
            agent_feeds (list): The list of agent feeds.
            history_enabled (bool): Whether to use history or not.
            completion_prompt (str): The completion prompt to be used for generating the agent messages.
        """
        token_limit = TokenCounter.token_limit(self.llm_model)
        max_output_token_limit = int(get_config("MAX_TOOL_TOKEN_LIMIT", 800))
        messages = [{"role": "system", "content": prompt}]

        if history_enabled:
            messages.append({"role": "system", "content": f"The current time and date is {time.strftime('%c')}"})
            base_token_limit = TokenCounter.count_message_tokens(messages, self.llm_model)
            full_message_history = [{'role': agent_feed.role, 'content': agent_feed.feed, 'chat_id': agent_feed.id}
                                    for agent_feed in agent_feeds]
            past_messages, current_messages = self._split_history(full_message_history,
                                                  ((token_limit - base_token_limit - max_output_token_limit) // 4) * 3)
            if past_messages:
                ltm_summary = self._build_ltm_summary(past_messages=past_messages,
                                                                   output_token_limit=(token_limit - base_token_limit - max_output_token_limit) // 4)
                messages.append({"role": "assistant", "content": ltm_summary})

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
            token_count = TokenCounter.count_message_tokens([{"role": message["role"], "content": message["content"]}],
                                                            self.llm_model)
            hist_token_count += token_count
            if hist_token_count > pending_token_limit:
                self._add_or_update_last_agent_feed_ltm_summary_id(str(history[i-1]['chat_id']))
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

    def _add_or_update_last_agent_feed_ltm_summary_id(self, last_agent_feed_ltm_summary_id):
        execution = AgentExecution(id=self.agent_execution_id)
        agent_execution_configs = {"last_agent_feed_ltm_summary_id": last_agent_feed_ltm_summary_id}
        AgentExecutionConfiguration.add_or_update_agent_execution_config(self.session, execution,
                                                                         agent_execution_configs)


    def _build_ltm_summary(self, past_messages, output_token_limit) -> str:
        ltm_prompt = self._build_prompt_for_ltm_summary(past_messages=past_messages,
                                                        token_limit=output_token_limit)

        summary = AgentExecutionConfiguration.fetch_value(self.session, self.agent_execution_id, "ltm_summary")
        previous_ltm_summary = summary.value if summary is not None else ""

        ltm_summary_base_token_limit = 10
        if ((TokenCounter.count_text_tokens(ltm_prompt) + ltm_summary_base_token_limit + output_token_limit)
            - TokenCounter.token_limit()) > 0:
            last_agent_feed_ltm_summary_id = AgentExecutionConfiguration.fetch_value(self.session,
                                                       self.agent_execution_id, "last_agent_feed_ltm_summary_id")
            last_agent_feed_ltm_summary_id = int(last_agent_feed_ltm_summary_id.value)

            past_messages = self.session.query(AgentExecutionFeed.role, AgentExecutionFeed.feed,
                                               AgentExecutionFeed.id) \
                .filter(AgentExecutionFeed.agent_execution_id == self.agent_execution_id,
                        AgentExecutionFeed.id > last_agent_feed_ltm_summary_id) \
                .order_by(asc(AgentExecutionFeed.created_at)) \
                .all()

            past_messages = [
                {'role': past_message.role, 'content': past_message.feed, 'chat_id': past_message.id}
                for past_message in past_messages]

            ltm_prompt = self._build_prompt_for_recursive_ltm_summary_using_previous_ltm_summary(
                previous_ltm_summary=previous_ltm_summary, past_messages=past_messages, token_limit=output_token_limit)

        msgs = [{"role": "system", "content": "You are GPT Prompt writer"},
                {"role": "assistant", "content": ltm_prompt}]
        ltm_summary = self.llm.chat_completion(msgs)

        execution = AgentExecution(id=self.agent_execution_id)
        agent_execution_configs = {"ltm_summary": ltm_summary["content"]}
        AgentExecutionConfiguration.add_or_update_agent_execution_config(session=self.session, execution=execution,
                                                                 agent_execution_configs=agent_execution_configs)

        return ltm_summary["content"]

    def _build_prompt_for_ltm_summary(self, past_messages: List[BaseMessage], token_limit: int):
        ltm_summary_prompt = PromptReader.read_agent_prompt(__file__, "agent_summary.txt")

        past_messages_prompt = ""
        for past_message in past_messages:
            past_messages_prompt += past_message["role"] + ": " + past_message["content"] + "\n"
        ltm_summary_prompt = ltm_summary_prompt.replace("{past_messages}", past_messages_prompt)

        ltm_summary_prompt = ltm_summary_prompt.replace("{char_limit}", str(token_limit*4))

        return ltm_summary_prompt

    def _build_prompt_for_recursive_ltm_summary_using_previous_ltm_summary(self, previous_ltm_summary: str,
                                                                    past_messages: List[BaseMessage], token_limit: int):
        ltm_summary_prompt = PromptReader.read_agent_prompt(__file__, "agent_recursive_summary.txt")

        ltm_summary_prompt = ltm_summary_prompt.replace("{previous_ltm_summary}", previous_ltm_summary)

        past_messages_prompt = ""
        for past_message in past_messages:
            past_messages_prompt += past_message["role"] + ": " + past_message["content"] + "\n"
        ltm_summary_prompt = ltm_summary_prompt.replace("{past_messages}", past_messages_prompt)

        ltm_summary_prompt = ltm_summary_prompt.replace("{char_limit}", str(token_limit*4))

        return ltm_summary_prompt

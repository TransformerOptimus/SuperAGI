import time
from typing import Tuple, List
from sqlalchemy import asc

from superagi.config.config import get_config
from superagi.helper.token_counter import TokenCounter
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.types.common import BaseMessage
from superagi.models.agent_execution_config import AgentExecutionConfiguration


class AgentLlmMessageBuilder:
    """Agent message builder for LLM agent."""
    def __init__(self, session, llm_model: str, agent_id: int, agent_execution_id: int):
        self.session = session
        self.llm_model = llm_model
        self.agent_id = agent_id
        self.agent_execution_id = agent_execution_id

    def build_agent_messages(self, prompt: str, agent_feeds: list, history_enabled=False,
                             completion_prompt: str = None, llm=None):
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
            print("past_messages_printed: ", past_messages)
            print("token_limit_for_memory:", token_limit - base_token_limit - max_output_token_limit)
            if past_messages:
                long_term_memory_prompt = self._build_prompt_for_long_term_summary(past_messages=past_messages,
                                                                                   token_limit=(token_limit -
                                                                                                base_token_limit -
                                                                                                max_output_token_limit) // 4)

                # summary = query from DB
                summary = self.session.query(AgentExecutionConfiguration).filter(
                    AgentExecutionConfiguration.agent_execution_id == self.agent_execution_id,
                    AgentExecutionConfiguration.key == "long_term_summary").first()
                if summary is None:
                    past_summary = ""
                else:
                    past_summary = summary.value
                print("token count ............1", TokenCounter.count_text_tokens(long_term_memory_prompt))
                print("token count ............2", TokenCounter.token_limit())
                if TokenCounter.count_text_tokens(long_term_memory_prompt) - TokenCounter.token_limit() > 100:
                    last_agent_feed_long_term_summary_id = self.session.query(AgentExecutionConfiguration).filter(
                        AgentExecutionConfiguration.agent_execution_id == self.agent_execution_id,
                        AgentExecutionConfiguration.key == "last_agent_feed_long_term_summary_id").first()
                    last_agent_feed_long_term_summary_id = int(last_agent_feed_long_term_summary_id.value)

                    # parse past_messages accordingly
                    past_messages = self.session.query(AgentExecutionFeed.role, AgentExecutionFeed.feed,
                                                       AgentExecutionFeed.id) \
                        .filter(AgentExecutionFeed.agent_execution_id == self.agent_execution_id,
                                AgentExecutionFeed.id > last_agent_feed_long_term_summary_id) \
                        .order_by(asc(AgentExecutionFeed.created_at)) \
                        .all()

                    past_messages = [
                        {'role': past_message.role, 'content': past_message.feed, 'chat_id': past_message.id}
                        for past_message in past_messages]

                    long_term_memory_prompt = self._build_prompt_for_recursive_long_term_summary(summary=past_summary,
                                                                                                 past_messages=past_messages,
                                                                                                 token_limit=(
                                                                                                                     token_limit -
                                                                                                                     base_token_limit -
                                                                                                                     max_output_token_limit) // 4)

                print("long_term_memory_prompt: ", long_term_memory_prompt)
                msgs = [{"role": "system", "content": "You are GPT Prompt writer"},
                        {"role": "assistant", "content": long_term_memory_prompt}]
                long_term_memory_summary = llm.chat_completion(msgs)
                print("long_term_memory_summary :", long_term_memory_summary["content"])

                # upsert summary in DB
                if summary is not None:
                    summary.value = long_term_memory_summary["content"]
                else:
                    agent_execution_config = AgentExecutionConfiguration(
                        agent_execution_id=self.agent_execution_id,
                        key="long_term_summary",
                        value=long_term_memory_summary["content"])
                    self.session.add(agent_execution_config)
                self.session.commit()

                messages.append({"role": "assistant", "content": long_term_memory_summary["content"]})
            print("current_messages_printed: ", current_messages)
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
                last_agent_feed_long_term_summary_id = self.session.query(AgentExecutionConfiguration).filter(
                    AgentExecutionConfiguration.agent_execution_id == self.agent_execution_id,
                    AgentExecutionConfiguration.key == "last_agent_feed_long_term_summary_id").first()
                if last_agent_feed_long_term_summary_id is not None:
                    last_agent_feed_long_term_summary_id.value = str(history[i-1]['chat_id'])
                else:
                    agent_execution_config = AgentExecutionConfiguration(
                        agent_execution_id=self.agent_execution_id,
                        key="last_agent_feed_long_term_summary_id",
                        value=str(history[i-1]['chat_id']))
                    self.session.add(agent_execution_config)
                self.session.commit()
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

    def _build_prompt_for_long_term_summary(self, past_messages: List[BaseMessage], token_limit: int):
        print("Inside build prompt function")
        print("inside func past_messages :", past_messages)
        long_term_memory_prompt = "AI, your task is to generate a concise summary of the previous interactions " \
                                  "between the system, user, and assistant. The interactions are as follows:\n"

        for past_message in past_messages:
            long_term_memory_prompt += past_message["role"] + ": " + past_message["content"] + "\n"

        long_term_memory_prompt += "This summary should encapsulate the main points of the conversation, " \
                                   "highlighting the key issues discussed, decisions made, and any actions assigned. " \
                                   "It should serve as a recap of the past interaction, providing a clear " \
                                   "understanding of the conversation's context and outcomes. Please ensure that the " \
                                   "summary does not exceed '{char_limit}' characters.". \
            format(char_limit=token_limit * 4)

        return long_term_memory_prompt

    def _build_prompt_for_recursive_long_term_summary(self, summary: str, past_messages: List[BaseMessage],
                                                      token_limit: int):
        print("Inside build recursive prompt function")
        print("inside recursive func pabst_messages :", past_messages)
        long_term_memory_prompt = "AI, you are provided with a previous summary of interactions between the system, " \
                                  "user, and assistant, as well as additional conversations that were not included " \
                                  "in the original summary. If the previous summary is empty, your task is to create " \
                                  "a summary based solely on the new interactions.\n"

        if summary:
            long_term_memory_prompt += "Previous Summary: " + summary + "\n"

        for past_message in past_messages:
            long_term_memory_prompt += past_message["role"] + ": " + past_message["content"] + "\n"

        long_term_memory_prompt += "If the previous summary is not empty, your final summary should integrate the " \
                                   "new interactions into the existing summary to create a comprehensive recap of " \
                                   "all interactions. If the previous summary is empty, your summary should " \
                                   "encapsulate the main points of the new conversations. In both cases, highlight" \
                                   " the key issues discussed, decisions made, and any actions assigned. Please " \
                                   "ensure that the final summary does not exceed '{char_limit}' characters." \
            .format(char_limit=token_limit * 4)

        return long_term_memory_prompt

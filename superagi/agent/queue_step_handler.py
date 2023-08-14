import time

import numpy as np

from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.agent.task_queue import TaskQueue
from superagi.helper.json_cleaner import JsonCleaner
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_tool import AgentWorkflowStepTool
from superagi.types.queue_status import QueueStatus


class QueueStepHandler:
    """Handles the queue step of the agent workflow"""
    def __init__(self, session, llm, agent_id: int, agent_execution_id: int):
        self.session = session
        self.llm = llm
        self.agent_execution_id = agent_execution_id
        self.agent_id = agent_id

    def _queue_identifier(self, step_tool):
        return step_tool.unique_id + "_" + str(self.agent_execution_id)

    def _build_task_queue(self, step_tool):
        return TaskQueue(self._queue_identifier(step_tool))

    def execute_step(self):
        execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        workflow_step = AgentWorkflowStep.find_by_id(self.session, execution.current_agent_step_id)
        step_tool = AgentWorkflowStepTool.find_by_id(self.session, workflow_step.action_reference_id)
        task_queue = self._build_task_queue(step_tool)

        if not task_queue.get_status() or task_queue.get_status() == QueueStatus.COMPLETE.value:
            task_queue.set_status(QueueStatus.INITIATED.value)

        if task_queue.get_status() == QueueStatus.INITIATED.value:
            self._add_to_queue(task_queue, step_tool)
            execution.current_feed_group_id = "DEFAULT"
            task_queue.set_status(QueueStatus.PROCESSING.value)

        if not task_queue.get_tasks():
            task_queue.set_status(QueueStatus.COMPLETE.value)
            return "COMPLETE"
        self._consume_from_queue(task_queue)
        return "default"

    def _add_to_queue(self, task_queue: TaskQueue, step_tool: AgentWorkflowStepTool):
        assistant_reply = self._process_input_instruction(step_tool)
        self._process_reply(task_queue, assistant_reply)

    def _consume_from_queue(self, task_queue: TaskQueue):
        tasks = task_queue.get_tasks()
        agent_execution = AgentExecution.find_by_id(self.session, self.agent_execution_id)
        if tasks:
            task = task_queue.get_first_task()
            # generating the new feed group id
            agent_execution.current_feed_group_id = "GROUP_" + str(int(time.time()))
            self.session.commit()
            task_response_feed = AgentExecutionFeed(agent_execution_id=self.agent_execution_id,
                                                    agent_id=self.agent_id,
                                                    feed="Input: " + task,
                                                    role="assistant",
                                                    feed_group_id=agent_execution.current_feed_group_id)
            self.session.add(task_response_feed)
            self.session.commit()
            task_queue.complete_task("PROCESSED")

    def _process_reply(self, task_queue: TaskQueue, assistant_reply: str):
        assistant_reply = JsonCleaner.extract_json_array_section(assistant_reply)
        print("Queue reply:", assistant_reply)
        task_array = np.array(eval(assistant_reply)).flatten().tolist()
        for task in task_array:
            task_queue.add_task(str(task))
            logger.info("RAMRAM: Added task to queue: ", task)

    def _process_input_instruction(self, step_tool):
        prompt = self._build_queue_input_prompt(step_tool)
        logger.info("Prompt: ", prompt)
        agent_feeds = AgentExecutionFeed.fetch_agent_execution_feeds(self.session, self.agent_execution_id)
        messages = AgentLlmMessageBuilder(self.session, self.llm, self.agent_id, self.agent_execution_id) \
            .build_agent_messages(prompt, agent_feeds, history_enabled=step_tool.history_enabled,
                                  completion_prompt=step_tool.completion_prompt)
        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        response = self.llm.chat_completion(messages, TokenCounter.token_limit(self.llm.get_model()) - current_tokens)
        if 'content' not in response or response['content'] is None:
            raise RuntimeError(f"Failed to get response from llm")
        total_tokens = current_tokens + TokenCounter.count_message_tokens(response, self.llm.get_model())
        AgentExecution.update_tokens(self.session, self.agent_execution_id, total_tokens)
        assistant_reply = response['content']
        return assistant_reply

    def _build_queue_input_prompt(self, step_tool: AgentWorkflowStepTool):
        queue_input_prompt = PromptReader.read_agent_prompt(__file__, "agent_queue_input.txt")
        queue_input_prompt = queue_input_prompt.replace("{instruction}", step_tool.input_instruction)

        return queue_input_prompt

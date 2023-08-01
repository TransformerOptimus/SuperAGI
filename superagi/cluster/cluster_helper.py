from superagi.agent.task_queue import TaskQueue
from superagi.cluster.cluster_prompt_builder import ClusterPromptBuilder
from superagi.helper.token_counter import TokenCounter
from superagi.llms.openai import OpenAi
from superagi.models.cluster import Cluster
from superagi.models.cluster_agent import ClusterAgent
from superagi.models.cluster_agent_execution import ClusterAgentExecution
from superagi.models.cluster_configuration import ClusterConfiguration
from superagi.models.cluster_execution import ClusterExecution
from superagi.models.cluster_execution_feed import ClusterExecutionFeed
from superagi.models.configuration import Configuration
from superagi.models.organisation import Organisation


class ClusterHelper:
    @classmethod
    def get_tasks(cls, session, cluster_execution_id):
        cluster = Cluster.get_cluster_by_execution_id(
            session, cluster_execution_id)
        cluster_config = ClusterConfiguration.fetch_cluster_configuration(
            session, cluster)
        goals = cluster_config['goal']
        instructions = cluster_config['instruction']
        agents = ClusterAgent.get_cluster_agents_by_cluster_id(
            session, cluster.id)
        prompt_dict = ClusterPromptBuilder.initialize_tasks_prompt()
        prompt = ClusterPromptBuilder.replace_main_variables(
            prompt_dict["prompt"], goals, instructions, agents)
        tasks = cls._get_completion(
            session, prompt, cluster, cluster_execution_id)
        tasks = eval(tasks)
        return tasks

    @classmethod
    def get_agent_for_task(cls, session, cluster_execution_id, task):
        cluster = Cluster.get_cluster_by_execution_id(
            session, cluster_execution_id)
        agents = ClusterAgent.get_cluster_agents_by_cluster_id(
            session, cluster.id)
        cluster_config = ClusterConfiguration.fetch_cluster_configuration(
            session, cluster)
        prompt_dict = ClusterPromptBuilder.decide_agent_prompt()
        queue_name = "cluster_execution" + str(cluster_execution_id)
        tasks_queue = TaskQueue(queue_name)
        prompt = ClusterPromptBuilder.replace_main_variables(
            prompt_dict["prompt"],
            cluster_config['goal'],
            cluster_config['instruction'],
            agents,
            tasks_queue.get_completed_tasks()
        )
        prompt = ClusterPromptBuilder.replace_task_based_variables(
            prompt, task)
        response = cls._get_completion(
            session, prompt, cluster, cluster_execution_id)
        response = eval(response)
        result = None
        if response["agent"]:
            result = {"agent_id": agents[response["agent"]["index"] - 1].id}
        if response["instructions"]:
            result["instructions"] = response["instructions"]
        return result

    @classmethod
    def _get_completion(cls, session, prompt, cluster, cluster_execution_id):
        organisation = Organisation.get_organisation_by_project_id(
            session, cluster.project_id)
        cluster_config = ClusterConfiguration.fetch_cluster_configuration(
            session, cluster)
        model = cluster_config['model']
        messages = []
        message = {
            "role": "system",
            "content": prompt
        }
        messages.append(message)
        execution_feed = ClusterExecutionFeed(
            cluster_execution_id=cluster_execution_id,
            cluster_id=cluster.id,
            feed=message['content'],
            role=message['role'])
        session.add(execution_feed)
        base_token_limit = TokenCounter.count_message_tokens(messages, model)
        llm = OpenAi(
            model=model,
            api_key=Configuration.fetch_configuration(
                session,
                organisation.id,
                "model_api_key"))
        token_limit = TokenCounter.token_limit(model)
        completion = llm.chat_completion(
            messages, token_limit - base_token_limit)
        execution_feed = ClusterExecutionFeed(
            cluster_execution_id=cluster_execution_id,
            cluster_id=cluster.id,
            feed=completion['content'],
            role="user")
        session.add(execution_feed)
        return completion['content']

    @classmethod
    def handle_cluster_agent_completed(cls, session, agent_execution_id ):
        cluster_execution_id = ClusterAgentExecution.get_cluster_execution_id_by_agent_execution_id(session,
                                                                                                    agent_execution_id)
        if cluster_execution_id:
            queue_name = "cluster_execution" + str(cluster_execution_id)
            tasks_queue = TaskQueue(queue_name)
            tasks_queue.complete_task("COMPLETE")
            ClusterExecution.update_cluster_execution_status(session, cluster_execution_id, "READY")

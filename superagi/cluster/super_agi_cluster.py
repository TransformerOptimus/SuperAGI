from superagi.cluster.cluster_prompt_builder import ClusterPromptBuilder
from superagi.helper.token_counter import TokenCounter
from superagi.llms.openai import OpenAi
from superagi.models.cluster_agent import ClusterAgent
from superagi.models.cluster_configuration import ClusterConfiguration
from superagi.models.cluster_execution import ClusterExecution
from superagi.models.configuration import Configuration
from superagi.models.organisation import Organisation


class SuperAgiCluster:
    @classmethod
    def get_tasks(cls, cluster_execution_id):
        cluster = ClusterExecution.get_cluster_by_execution_id(cluster_execution_id)
        cluster_config = ClusterConfiguration.fetch_cluster_configuration(cluster.id)
        goals = cluster_config['goals']
        instructions = cluster_config['instructions']
        agents = ClusterAgent.get_cluster_agents_by_cluster_id(cluster.id)
        prompt_dict = ClusterPromptBuilder.initialize_tasks_prompt()
        prompt = ClusterPromptBuilder.replace_main_variables(prompt_dict["prompt"], goals, instructions, agents)
        tasks = cls._get_completion(prompt, cluster)
        tasks = eval(tasks)
        return tasks

    @classmethod
    def get_agent_for_task(cls, cluster_execution_id, task):
        cluster = ClusterExecution.get_cluster_by_execution_id(cluster_execution_id)
        agents = ClusterAgent.get_cluster_agents_by_cluster_id(cluster.id)
        cluster_config = ClusterConfiguration.fetch_cluster_configuration(cluster.id)
        prompt_dict = ClusterPromptBuilder.decide_agent_prompt()
        prompt = ClusterPromptBuilder.replace_main_variables(prompt_dict["prompt"], cluster_config['goals'],
                                                             cluster_config['instructions'], agents)
        prompt = ClusterPromptBuilder.replace_task_based_variables(prompt, task)
        response = cls._get_completion(prompt, cluster)
        response = eval(response)
        if response["agent"]:
            return agents[response["agent"]["index"] - 1].agent_id
        else:
            return None

    @classmethod
    def _get_completion(cls, prompt, cluster):
        organisation = Organisation.get_organisation_by_project_id(cluster.project_id)
        cluster_config = ClusterConfiguration.fetch_cluster_configuration(cluster.id)
        model = cluster_config['model']
        messages = []
        message = {
            "role": "system",
            "content": prompt
        }
        messages.append(message)
        base_token_limit = TokenCounter.count_message_tokens(messages, model)
        llm = OpenAi(model=model, api_key=Configuration.get_model_api_key(organisation.id))
        token_limit = TokenCounter.token_limit()
        completion = llm.chat_completion(prompt, token_limit=token_limit - base_token_limit, temperature=0.9,
                                         max_tokens=token_limit)
        return completion

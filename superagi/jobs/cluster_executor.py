import multiprocessing
from typing import List

from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from superagi.jobs.agent_executor import AgentExecutor
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent import Agent
from superagi.models.agent_cluster import AgentCluster
from superagi.models.agent_execution import AgentExecution
from superagi.models.cluster_agent_mapping import ClusterAgentMapping
from superagi.models.cluster_execution import ClusterExecution
from superagi.models.db import connect_db

engine = connect_db()
Session = sessionmaker(bind=engine)


class ClusterExecutor:
    def __init__(self, llm: BaseLlm):
        self.pool = multiprocessing.Pool()
        self.agent_executor = AgentExecutor()
        self.llm = llm

    def execute_next_action(self, cluster_execution_id: int):
        global engine
        # try:
        engine.dispose()
        session = Session()

        cluster_execution = session.query(ClusterExecution).filter(ClusterExecution.id == cluster_execution_id).first()
        if cluster_execution.created_at < datetime.utcnow() - timedelta(days=1):
            return

        cluster = session.query(AgentCluster).filter(AgentCluster.id == cluster_execution.cluster_id).first()
        agents = session.query(ClusterAgentMapping).filter(ClusterAgentMapping.cluster_id == cluster.id).all()

        # parallely execute all agents using multiprocessing
        tasks = []
        agents_to_use = self.get_agents_to_use(cluster_execution, agents)
        for agent in agents_to_use:
            agent_execution = AgentExecution(agent_id=agent.agent_id, cluster_execution_id=cluster_execution.id,
                                             status="QUEUED")
            session.add(agent_execution)
            session.commit()
            tasks.append(
                self.pool.apply_async(func=self.agent_executor.execute_next_action, args=(agent_execution.id,)))

        for task in tasks:
            task.get()
        session.close()
        self.pool.close()
        self.pool.join()

    def get_agents_to_use(self, cluster_execution: ClusterExecution, agents: List[Agent]):
        goal = cluster_execution.goal
        agents_string = ""
        messages = []
        for index, agent in enumerate(agents):
            agents_string += f"#{index}\n" \
                             f"Name: {agent.name}\n" \
                             f"Description: {agent.description}\n\n"
        prompt = f"You are a master agent and you have to select appropriate agents to overcome the goal given below. "\
                 f"You are given every agent's name and description about it's capabilities. You have to use sound " \
                 f"reasoning and logic to select the agents. Only the agents you select will be used to overcome the " \
                 f"goal. You can select as many agents as you want. You have to select distinct agents. You have to " \
                 f"select at least one agent. You have to return the indices of the agents (separated by a comma if " \
                 f"they are more than one)." \
                 f"/n/nGoal: {goal}" \
                 f"/n/n Agents: \n{agents_string}"
        messages.append({"role": "system", "content": prompt})
        response = self.llm.chat_completion(messages)["content"]
        if len(response) == 0:
            return
        response = response.split(",")
        response = [int(x) for x in response]
        agents_to_use = []
        for index in response:
            agents_to_use.append(agents[index - 1])

        return agents_to_use

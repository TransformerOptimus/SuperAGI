from datetime import datetime

from sqlalchemy.orm import sessionmaker

from superagi.agent.task_queue import TaskQueue
from superagi.cluster.super_agi_cluster import SuperAgiCluster
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.cluster_execution import ClusterExecution
from superagi.models.db import connect_db

engine = connect_db()
Session = sessionmaker(bind=engine)


class ClusterExecutor:
    session = None

    # def __init__(self):
    #     self.session = Session()

    @staticmethod
    def schedule_pending_executions():
        """
        Schedules pending executions for all clusters.
        """
        pending_cluster_executions = ClusterExecution.get_pending_cluster_executions()
        for cluster_execution in pending_cluster_executions:
            ClusterExecutor.schedule_execution(cluster_execution.id, cluster_execution.status)

    @staticmethod
    def schedule_execution(cluster_execution_id, status):
        """
        Schedules a cluster execution.

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be scheduled.
            status (str): The status of the cluster execution to be scheduled.
        """
        if status == 'CREATED':
            ClusterExecutor.handle_created_cluster_execution(cluster_execution_id)
        elif status == 'PICKED':
            ClusterExecutor.handle_picked_cluster_execution(cluster_execution_id)
        elif status == 'READY':
            ClusterExecutor.handle_ready_cluster_execution(cluster_execution_id)
        else:
            pass

    @staticmethod
    def handle_created_cluster_execution(cluster_execution_id):
        """
        Handles a created cluster execution.
        CREATE -> PICKED

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be handled.
        """
        ClusterExecution.update_cluster_status(cluster_execution_id, 'PICKED')

    @staticmethod
    def handle_picked_cluster_execution(cluster_execution_id):
        """
        Handles a picked cluster execution.
        PICKED -> READY

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be handled.
        """
        queue_name = "cluster_execution" + str(cluster_execution_id)
        tasks_queue = TaskQueue(queue_name)
        tasks_queue.clear_tasks()
        tasks = SuperAgiCluster.get_tasks(cluster_execution_id)
        reversed(tasks)
        tasks_queue.enqueue_tasks(tasks)
        ClusterExecution.update_cluster_status(cluster_execution_id, 'READY')

    @staticmethod
    def handle_ready_cluster_execution(cluster_execution_id):
        """
        Handles a ready cluster execution.
        READY -> WAITING

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be handled.
        """
        queue_name = "cluster_execution" + str(cluster_execution_id)
        tasks_queue = TaskQueue(queue_name)
        next_task = tasks_queue.get_first_task()
        if next_task is not None:
            next_agent_id = SuperAgiCluster.get_agent_for_task(cluster_execution_id, next_task)
            ClusterExecutor.spawn_agent(cluster_execution_id, next_agent_id, next_task)
            ClusterExecution.update_cluster_status(cluster_execution_id, 'WAITING')
        else:
            ClusterExecution.update_cluster_status(cluster_execution_id, 'COMPLETED')

    @staticmethod
    def spawn_agent(cluster_execution_id: int, agent_id: int, task: str):
        """
        Spawns an agent for the given cluster id and agent id and assigns the given task to it.

        Args:
            cluster_execution_id (int): The identifier of the cluster execution.
            agent_id (int): The identifier of the agent.
            task (str): The task to be assigned to the agent.
        """
        agent_execution = AgentExecution(cluster_execution_id=cluster_execution_id, agent_id=agent_id, status="CREATED",
                                         last_execution_time=datetime.utcnow(), num_of_calls=0, num_of_tokens=0)
        AgentConfiguration.update_agent_config_key(agent_id, 'goal', task)
        from superagi.worker.agent_worker import execute_agent
        execute_agent(agent_execution, datetime.utcnow())


    @staticmethod
    def get_last_agent_feed(cluster_execution_id):
        agent_execution = AgentExecution.get_last_agent_execution(cluster_execution_id)

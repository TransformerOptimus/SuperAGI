import sys
import traceback
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from superagi.agent.task_queue import TaskQueue
from superagi.cluster.cluster_helper import ClusterHelper
from superagi.lib.logger import logger
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.cluster import Cluster
from superagi.models.cluster_execution import ClusterExecution
from superagi.models.db import connect_db
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.iteration_workflow import IterationWorkflow

engine = connect_db()
Session = sessionmaker(bind=engine)


class ClusterExecutor:

    @staticmethod
    def schedule_pending_executions():
        """
        Schedules pending executions for all clusters.
        """

        global engine
        # try:
        session = Session()
        try:
            pending_cluster_executions = ClusterExecution.get_pending_cluster_executions(
                session)
            for cluster_execution in pending_cluster_executions:
                ClusterExecutor.schedule_execution(
                    session, cluster_execution.id, cluster_execution.status)
        except Exception as e:
            logger.error(
                "Error while scheduling pending cluster executions: " +
                str(e))
            traceback.print_exception(*sys.exc_info())
        finally:
            session.close()
            engine.dispose()

    @staticmethod
    def schedule_execution(session, cluster_execution_id, status):
        """
        Schedules a cluster execution.

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be scheduled.
            status (str): The status of the cluster execution to be scheduled.
        """
        if status == 'CREATED':
            ClusterExecutor.handle_created_cluster_execution(
                session, cluster_execution_id)
        elif status == 'PICKED':
            ClusterExecutor.handle_picked_cluster_execution(
                session, cluster_execution_id)
        elif status == 'READY':
            ClusterExecutor.handle_ready_cluster_execution(
                session, cluster_execution_id)

    @staticmethod
    def handle_created_cluster_execution(session, cluster_execution_id):
        """
        Handles a created cluster execution.
        CREATE -> PICKED

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be handled.
        """
        try:
            ClusterExecution.update_cluster_execution_status(
                session, cluster_execution_id, 'PICKED')
        except Exception as e:
            logger.error(
                "Error while handling created cluster execution: " +
                str(e))

    @staticmethod
    def handle_picked_cluster_execution(session, cluster_execution_id):
        """
        Handles a picked cluster execution.
        PICKED -> READY

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be handled.
        """

        queue_name = "cluster_execution" + str(cluster_execution_id)
        tasks_queue = TaskQueue(queue_name)
        tasks_queue.clear_tasks()
        tasks = ClusterHelper.get_tasks(
            session, cluster_execution_id)
        tasks = reversed(tasks)
        tasks_queue.enqueue_tasks(tasks)
        ClusterExecution.update_cluster_execution_status(
            session, cluster_execution_id, 'READY')

    @staticmethod
    def handle_ready_cluster_execution(session, cluster_execution_id):
        """
        Handles a ready cluster execution.
        READY -> WAITING

        Args:
            cluster_execution_id (int): The identifier of the cluster execution to be handled.
        """
        try:
            queue_name = "cluster_execution" + str(cluster_execution_id)
            cluster = Cluster.get_cluster_by_execution_id(
                session, cluster_execution_id)
            tasks_queue = TaskQueue(queue_name)
            next_task = tasks_queue.get_first_task()
            if next_task is not None:
                result = ClusterHelper.get_agent_for_task(session,
                                                          cluster_execution_id, next_task)
                next_agent_id = result["agent_id"]
                instructions = result["instructions"]
                ClusterExecutor.spawn_agent(
                    session,
                    cluster.id,
                    cluster_execution_id,
                    next_agent_id,
                    next_task,
                    instructions)
                ClusterExecution.update_cluster_execution_status(
                    session, cluster_execution_id, 'WAITING')
            else:
                ClusterExecution.update_cluster_execution_status(
                    session, cluster_execution_id, 'COMPLETED')
        except Exception as e:
            logger.error(
                "Error while handling ready cluster execution: " +
                str(e))

    @staticmethod
    def spawn_agent(
            session,
            cluster_id: int,
            cluster_execution_id: int,
            agent_id: int,
            task: str,
            instructions: str):
        """
        Spawns an agent for the given cluster id and agent id and assigns the given task to it.

        Args:
            cluster_id (int): The identifier of the cluster.
            cluster_execution_id (int): The identifier of the cluster execution.
            agent_id (int): The identifier of the agent.
            task (str): The task to be assigned to the agent.
            instructions (str): The instructions to be executed by the agent.
        """
        try:
            agent = Agent.get_agent_by_id(session, agent_id)

            start_step = AgentWorkflow.fetch_trigger_step_id(session, agent.agent_workflow_id)
            iteration_step_id = IterationWorkflow.fetch_trigger_step_id(session,
                                                                        start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1
            execution = AgentExecution(status='RUNNING', last_execution_time=datetime.now(), agent_id=agent.id,
                                       name="New Run", current_agent_step_id=start_step.id,
                                       iteration_workflow_step_id=iteration_step_id)

            session.add(execution)
            agent_execution_configs = {
                "goal": task,
                "instructions": instructions,
            }
            # todo add to cluster_agent_executions
            AgentExecutionConfiguration.add_or_update_agent_execution_config(
                session=session,
                execution=execution,
                agent_execution_configs=agent_execution_configs)
            print("Spawning agent " +
                  str(execution.id) +
                  " for task " +
                  task)
            session.commit()
            from superagi.worker import execute_agent
            execute_agent.delay(execution.id, datetime.now())
        except Exception as e:
            logger.error("Error while spawning agent: " + str(e))

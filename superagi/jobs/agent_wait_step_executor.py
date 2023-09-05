from datetime import datetime

from sqlalchemy.orm import sessionmaker

from superagi.agent.agent_workflow_step_wait_handler import AgentWaitStepHandler
from superagi.models.agent_execution import AgentExecution
from superagi.models.db import connect_db
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_wait import AgentWorkflowStepWait
from superagi.worker import execute_agent

engine = connect_db()
Session = sessionmaker(bind=engine)


class AgentWorkflowStepWaitExecutor:

    def execute_waiting_workflows(self):
        """Check if wait time of wait workflow step is over and can be resumed."""

        session = Session()
        waiting_agent_executions = session.query(AgentExecution).filter(
            AgentExecution.status == 'WAIT_STEP',
        ).all()
        for agent_execution in waiting_agent_executions:
            workflow_step = session.query(AgentWorkflowStep).filter(
                AgentWorkflowStep.id == agent_execution.current_agent_step_id).first()
            step_wait = AgentWorkflowStepWait.find_by_id(session, workflow_step.action_reference_id)
            if step_wait is not None:
                if step_wait.wait_begin_time is not None:
                    wait_time = step_wait.delay
                    if wait_time is None:
                        wait_time = 0
                    if ((datetime.now() - step_wait.wait_begin_time).total_seconds() > wait_time
                            and step_wait.status == "WAITING"):
                        agent_execution.status = "RUNNING"
                        # step_wait.wait_begin_time = None
                        step_wait.status = "COMPLETED"
                        session.commit()
                        session.flush()
                        AgentWaitStepHandler(session=session, agent_id=agent_execution.agent_id,
                                             agent_execution_id=agent_execution.id).handle_next_step()
                        execute_agent.delay(agent_execution.id, datetime.now())
        session.close()

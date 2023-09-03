from datetime import timedelta, datetime

from sqlalchemy.orm import sessionmaker

from superagi.models.agent_execution import AgentExecution
from superagi.models.db import connect_db
from superagi.models.workflows.agent_workflow_step_wait import AgentWorkflowStepWait
from superagi.worker import execute_agent

engine = connect_db()
Session = sessionmaker(bind=engine)


class AgentWorkflowStepWaitExecutor:

    def execute_waiting_workflows(self):
        """Check if wait time of wait workflow step is over and can be resumed."""

        session = Session()
        waiting_agent_executions = session.query(AgentExecution).filter(
            AgentExecution.status == 'WAITING_STEP',
        ).all()
        for agent_execution in waiting_agent_executions:
            workflow_step = agent_execution.current_agent_step
            step_wait = AgentWorkflowStepWait.find_by_id(session, workflow_step.action_reference_id)
            if step_wait is not None:
                if step_wait.wait_begin_time is not None:
                    wait_time = step_wait.delay
                    if wait_time is None:
                        wait_time = 0
                    if (datetime.now() - step_wait.wait_begin_time).total_seconds() > wait_time:
                        agent_execution.status = "RUNNING"
                        # step_wait.wait_begin_time = None
                        step_wait.status = "COMPLETED"
                        session.commit()
                        execute_agent.delay(agent_execution.id, datetime.now())
        session.close()


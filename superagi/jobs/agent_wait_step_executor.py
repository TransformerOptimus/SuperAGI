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
        print("_________________________Waiting Block Execute_________________________")
        print(waiting_agent_executions)
        for agent_execution in waiting_agent_executions:
            workflow_step = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.id == agent_execution.current_agent_step_id).first()
            # workflow_step = agent_execution.current_agent_step_id
            print("Workflow Step: ", workflow_step)
            step_wait = AgentWorkflowStepWait.find_by_id(session, workflow_step.action_reference_id)
            print("__________STEP WAIT STATUS CHECK__________")
            print("step_wait: ", step_wait)
            print(step_wait.status)
            if step_wait is not None:
                print("step_wait.wait_begin_time: ", step_wait.wait_begin_time)
                if step_wait.wait_begin_time is not None:
                    wait_time = step_wait.delay
                    if wait_time is None:
                        wait_time = 0
                    print("wait_time: ", wait_time)
                    print("Current Time: ", datetime.now())
                    print("Current Time in seconds : ", (datetime.now() - step_wait.wait_begin_time).total_seconds())
                    if (datetime.now() - step_wait.wait_begin_time).total_seconds() > wait_time and step_wait.status == "WAITING":
                        print("change status to running")
                        agent_execution.status = "RUNNING"
                        # step_wait.wait_begin_time = None
                        step_wait.status = "COMPLETED"
                        session.commit()
                        session.flush()
                        print("Executing Agent from waiting _____________________________")
                        print("Final logs : ",step_wait.status)
                        print("Going to execute agent : ",agent_execution.id)
                        print("Agent Execution Status : ",agent_execution.status)
                        AgentWaitStepHandler(session=session,agent_id=agent_execution.agent_id,
                                             agent_execution_id=agent_execution.id).handle_next_step()
                        execute_agent.delay(agent_execution.id, datetime.now())
        session.close()

    # def __handle_next_step(self, session,agent_execution):
    #     print("Handling Next Step_______________")
    #     # execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
    #     workflow_step = AgentWorkflowStep.find_by_id(session, agent_execution.current_agent_step_id)
    #     step_response = "default"
    #     next_step = AgentWorkflowStep.fetch_next_step(session, workflow_step.id, step_response)
    #     if str(next_step) == "COMPLETE":
    #         agent_execution = AgentExecution.get_agent_execution_from_id(session, agent_execution.id)
    #         agent_execution.current_agent_step_id = -1
    #         agent_execution.status = "COMPLETED"
    #     else:
    #         AgentExecution.assign_next_step_id(session, agent_execution.id, next_step.id)
    #     session.commit()
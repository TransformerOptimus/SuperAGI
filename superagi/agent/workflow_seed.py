from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.agent_prompt_template import AgentPromptTemplate
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.models.workflows.iteration_workflow_step import IterationWorkflowStep
from superagi.tools.code.write_code import CodingTool
from superagi.tools.code.write_spec import WriteSpecTool
from superagi.tools.code.write_test import WriteTestTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.searx.searx import SearxSearchTool


class AgentWorkflowSeed:
    @classmethod
    def build_sales_workflow(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Sales Research Workflow", "Sales Research Workflow")
        step1 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id, "step1",
                                                                    SearxSearchTool().name,
                                                                    "Convert goal into input",
                                                                    step_type="TRIGGER")

        step2 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id, "step2",
                                                                    ReadFileTool().name,
                                                                    "Get lead matching last record from leads.csv",
                                                                    "Return 'YES' if lead exists in file else return 'NO'")
        step3 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id, "step3",
                                                                    SearxSearchTool().name,
                                                                    "Research report about the lead")

        step4 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id, "step4",
                                                                    WriteFileTool().name,
                                                                    "Add the research and lead details to leads.csv")

        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step3.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step1.id, "YES")
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step3.id, "NO")
        AgentWorkflowStep.add_next_workflow_step(session, step3.id, step4.id)
        AgentWorkflowStep.add_next_workflow_step(session, step4.id, step1.id)
        session.commit()

    @classmethod
    def build_coding_workflow(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "SuperCoder", "SuperCoder")
        step1 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id, "step1",
                                                                    WriteSpecTool().name,
                                                                    "Spec description",
                                                                    step_type="TRIGGER")

        step2 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id, "step2",
                                                                    CodingTool().name,
                                                                    "Code description")
        step3 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id, "step3",
                                                                    WriteTestTool().name,
                                                                    "Test description")

        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step3.id)
        AgentWorkflowStep.add_next_workflow_step(session, step3.id, -1)
        # AgentWorkflowStep.add_next_workflow_step(session, step3.id, step3.id)

    @classmethod
    def build_goal_based_agent(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Goal Based Workflow", "Goal Based Workflow")
        step1 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id, "step1",
                                                                         "Goal Based Agent", step_type="TRIGGER")
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step1.id)
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, -1, "COMPLETE")

    @classmethod
    def build_task_based_agent(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Dynamic Task Workflow", "Dynamic Task Workflow")
        step1 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id, "step1",
                                                                         "Initialize Tasks", step_type="TRIGGER")
        step2 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id, "step1",
                                                                         "Dynamic Task Queue", step_type="NORMAL")
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, -1, "COMPLETE")

    @classmethod
    def build_fixed_task_based_agent(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Fixed Task Workflow", "Fixed Task Workflow")
        step1 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id, "step1",
                                                                         "Fixed Task Queue", step_type="TRIGGER")
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step1.id)
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, -1, "COMPLETE")


class IterationWorkflowSeed:
    @classmethod
    def build_single_step_agent(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Goal Based Agent", "Goal Based Agent")
        output = AgentPromptTemplate.get_super_agi_single_prompt()
        IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "gb1",
                                                  output["prompt"],
                                                  str(output["variables"]), "TRIGGER", "tools",
                                                  history_enabled=True,
                                                  completion_prompt="Determine which next tool to use, and respond using the format specified above:")

    @classmethod
    def build_task_based_agents(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Dynamic Task Queue",
                                                                      "Dynamic Task Queue", has_task_queue=True)

        output = AgentPromptTemplate.analyse_task()
        workflow_step1 = IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "tb1",
                                                                   output["prompt"],
                                                                   str(output["variables"]), "NORMAL", "tools")

        output = AgentPromptTemplate.create_tasks()
        workflow_step2 = IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "tb2",
                                                                   output["prompt"],
                                                                   str(output["variables"]), "TRIGGER", "tasks")

        output = AgentPromptTemplate.prioritize_tasks()
        workflow_step3 = IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "tb3",
                                                                   output["prompt"],
                                                                   str(output["variables"]), "NORMAL", "replace_tasks")

        workflow_step1.next_step_id = workflow_step2.id
        workflow_step2.next_step_id = workflow_step3.id

        session.commit()

    @classmethod
    def build_initialize_task_workflow(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Initialize Tasks", "Initialize Tasks",
                                                                      has_task_queue=True)
        output = AgentPromptTemplate.start_task_based()

        IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "init_task1",
                                                  output["prompt"], str(output["variables"]), "TRIGGER", "tasks")

    @classmethod
    def build_action_based_agents(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Fixed Task Queue", "Fixed Task Queue",
                                                                      has_task_queue=True)
        output = AgentPromptTemplate.analyse_task()
        IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "ab1",
                                                  output["prompt"], str(output["variables"]), "TRIGGER", "tools")

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.agent_prompt_template import AgentPromptTemplate
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.models.workflows.iteration_workflow_step import IterationWorkflowStep
from superagi.tools.apollo.apollo_search import ApolloSearchTool
from superagi.tools.code.write_code import CodingTool
from superagi.tools.code.write_spec import WriteSpecTool
from superagi.tools.code.write_test import WriteTestTool
from superagi.tools.email.read_email import ReadEmailTool
from superagi.tools.email.send_email import SendEmailTool
from superagi.tools.file.append_file import AppendFileTool
from superagi.tools.file.list_files import ListFileTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.github.add_file import GithubAddFileTool
from superagi.tools.google_calendar.create_calendar_event import CreateEventCalendarTool
from superagi.tools.google_calendar.google_calendar_toolkit import GoogleCalendarToolKit
from superagi.tools.google_search.google_search import GoogleSearchTool
from superagi.tools.jira.create_issue import CreateIssueTool
from superagi.tools.searx.searx import SearxSearchTool
from superagi.tools.slack.send_message import SlackMessageTool
from superagi.tools.thinking.tools import ThinkingTool
from superagi.tools.twitter.send_tweets import SendTweetsTool
from superagi.tools.webscaper.tools import WebScraperTool


class AgentWorkflowSeed:
    @classmethod
    def build_sales_workflow(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Sales Engagement Workflow",
                                                              "Sales Engagement Workflow")
        # step1 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
        #                                                             str(agent_workflow.id) + "_step1",
        #                                                             ApolloSearchTool().name,
        #                                                             "Search for leads based on the given goals",
        #                                                             step_type="TRIGGER")
        #
        # step2 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
        #                                                             str(agent_workflow.id) + "_step2",
        #                                                             WriteFileTool().name,
        #                                                             "Write the leads to a csv file")

        step3 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step3",
                                                                    ReadFileTool().name,
                                                                    "Read the leads from the file generated in the previous run",
                                                                    step_type="TRIGGER")

        # task queue ends when the elements gets over
        step4 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step4",
                                                                    "TASK_QUEUE",
                                                                    "Break the above response array of items",
                                                                    completion_prompt="Get array of items from the above response. Array should suitable utilization of JSON.parse().")

        step5 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step5",
                                                                    GoogleSearchTool().name,
                                                                    "Search about the company in which the lead is working")

        step6 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step6",
                                                                    "WAIT_FOR_PERMISSION",
                                                                    "Email will be based on this content. Do you want send the email?")

        step7 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step7",
                                                                    GoogleSearchTool().name,
                                                                    "Search about the company given in the high-end goal only")

        step8 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step8",
                                                                    SendEmailTool().name,
                                                                    "Customize the Email according to the company information in the mail")

        # AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        # AgentWorkflowStep.add_next_workflow_step(session, step2.id, step3.id)
        AgentWorkflowStep.add_next_workflow_step(session, step3.id, step4.id)
        AgentWorkflowStep.add_next_workflow_step(session, step4.id, -1, "COMPLETE")
        AgentWorkflowStep.add_next_workflow_step(session, step4.id, step5.id)
        AgentWorkflowStep.add_next_workflow_step(session, step5.id, step6.id)
        AgentWorkflowStep.add_next_workflow_step(session, step6.id, step7.id, "YES")
        AgentWorkflowStep.add_next_workflow_step(session, step6.id, step5.id, "NO")
        AgentWorkflowStep.add_next_workflow_step(session, step7.id, step8.id)
        AgentWorkflowStep.add_next_workflow_step(session, step8.id, step4.id)
        session.commit()

    @classmethod
    def build_recruitment_workflow(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Recruitment Workflow",
                                                              "Recruitment Workflow")
        step1 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step1",
                                                                    ListFileTool().name,
                                                                    "Read files from the resource manager",
                                                                    step_type="TRIGGER")

        # task queue ends when the elements gets over
        step2 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step2",
                                                                    "TASK_QUEUE",
                                                                    "Break the above response array of items",
                                                                    completion_prompt="Get array of items from the above response. Array should suitable utilization of JSON.parse().")

        step3 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step3",
                                                                    ReadFileTool().name,
                                                                    "Read the resume from above input")

        step4 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step4",
                                                                    ReadFileTool().name,
                                                                    "Read the job description from job description file",
                                                                    "Check if the resume matches the job description in goal")

        step5 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step4",
                                                                    SendEmailTool().name,
                                                                    "Write a custom Email the candidates for job profile based on their experience")

        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step3.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, -1, "COMPLETE")
        AgentWorkflowStep.add_next_workflow_step(session, step3.id, step4.id)
        AgentWorkflowStep.add_next_workflow_step(session, step4.id, step5.id)
        AgentWorkflowStep.add_next_workflow_step(session, step5.id, step2.id)
        session.commit()


    @classmethod
    def build_coding_workflow(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "SuperCoder", "SuperCoder")
        step1 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step1",
                                                                    WriteSpecTool().name,
                                                                    "Spec description",
                                                                    step_type="TRIGGER")

        step2 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step2",
                                                                    WriteTestTool().name,
                                                                    "Test description")

        step3 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step3",
                                                                    CodingTool().name,
                                                                    "Code description")


        step4 = AgentWorkflowStep.find_or_create_tool_workflow_step(session, agent_workflow.id,
                                                                    str(agent_workflow.id) + "_step4",
                                                                    "WAIT_FOR_PERMISSION",
                                                                    "Your code is ready. Do you want end?")

        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step3.id)
        AgentWorkflowStep.add_next_workflow_step(session, step3.id, step4.id)
        AgentWorkflowStep.add_next_workflow_step(session, step4.id, -1, "YES")
        AgentWorkflowStep.add_next_workflow_step(session, step4.id, step3.id, "NO")


    @classmethod
    def build_goal_based_agent(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Goal Based Workflow", "Goal Based Workflow")
        step1 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id,
                                                                         str(agent_workflow.id) + "_step1",
                                                                         "Goal Based Agent-I", step_type="TRIGGER")
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step1.id)
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, -1, "COMPLETE")

    @classmethod
    def build_task_based_agent(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Dynamic Task Workflow", "Dynamic Task Workflow")
        step1 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id,
                                                                         str(agent_workflow.id) + "_step1",
                                                                         "Initialize Tasks-I", step_type="TRIGGER")
        step2 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id,
                                                                         str(agent_workflow.id) + "_step2",
                                                                         "Dynamic Task Queue-I", step_type="NORMAL")
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, -1, "COMPLETE")

    @classmethod
    def build_fixed_task_based_agent(cls, session):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Fixed Task Workflow", "Fixed Task Workflow")
        step1 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id,
                                                                         str(agent_workflow.id) + "_step1",
                                                                         "Initialize Tasks-I", step_type="TRIGGER")
        step2 = AgentWorkflowStep.find_or_create_iteration_workflow_step(session, agent_workflow.id,
                                                                         str(agent_workflow.id) + "_step2",
                                                                         "Fixed Task Queue-I", step_type="NORMAL")
        AgentWorkflowStep.add_next_workflow_step(session, step1.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, step2.id)
        AgentWorkflowStep.add_next_workflow_step(session, step2.id, -1, "COMPLETE")


class IterationWorkflowSeed:
    @classmethod
    def build_single_step_agent(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Goal Based Agent-I", "Goal Based Agent")
        output = AgentPromptTemplate.get_super_agi_single_prompt()
        IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "gb1",
                                                  output["prompt"],
                                                  str(output["variables"]), "TRIGGER", "tools",
                                                  history_enabled=True,
                                                  completion_prompt="Determine which next tool to use, and respond using the format specified above:")

    @classmethod
    def build_task_based_agents(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Dynamic Task Queue-I",
                                                                      "Dynamic Task Queue", has_task_queue=True)

        output = AgentPromptTemplate.analyse_task()
        workflow_step1 = IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "tb1",
                                                                   output["prompt"],
                                                                   str(output["variables"]), "TRIGGER", "tools")

        output = AgentPromptTemplate.create_tasks()
        workflow_step2 = IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "tb2",
                                                                   output["prompt"],
                                                                   str(output["variables"]), "NORMAL", "tasks")

        output = AgentPromptTemplate.prioritize_tasks()
        workflow_step3 = IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "tb3",
                                                                   output["prompt"],
                                                                   str(output["variables"]), "NORMAL", "replace_tasks")

        workflow_step1.next_step_id = workflow_step2.id
        workflow_step2.next_step_id = workflow_step3.id

        session.commit()

    @classmethod
    def build_initialize_task_workflow(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Initialize Tasks-I", "Initialize Tasks",
                                                                      has_task_queue=True)
        output = AgentPromptTemplate.start_task_based()

        IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "init_task1",
                                                  output["prompt"], str(output["variables"]), "TRIGGER", "tasks")

    @classmethod
    def build_action_based_agents(cls, session):
        iteration_workflow = IterationWorkflow.find_or_create_by_name(session, "Fixed Task Queue-I", "Fixed Task Queue",
                                                                      has_task_queue=True)
        output = AgentPromptTemplate.analyse_task()
        IterationWorkflowStep.find_or_create_step(session, iteration_workflow.id, "ab1",
                                                  output["prompt"], str(output["variables"]), "TRIGGER", "tools")

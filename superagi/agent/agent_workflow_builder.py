import queue
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from superagi.config.config import get_config
from superagi.models.db import connect_db
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.agent.agent_workflow_validator import AgentWorkflowValidator


class AgentWorkflowBuilder:
    """AgentWorkflowBuilder class is responsible for building agent workflows from .yaml based workflows."""

    def __init__(self, session, agent_workflow):
        self.session = session
        self.agent_workflow = agent_workflow

    def build_workflow_from_yaml(self, workflow_yaml):
        """Build agent workflow from .yaml file content.

        Args:
            workflow_yaml (str): The workflow content in .yaml format.

        Returns:
            AgentWorkflow: The agent workflow.
        """
        print("BUILDING WORKFLOW FROM YAML")
        # get parsed workflow yaml as dict
        agent_workflow = workflow_yaml

        AgentWorkflowValidator(self.session).validate_workflow_steps(agent_workflow)

        trigger_workflow_yaml_step = self.find_trigger_step(agent_workflow)
        if trigger_workflow_yaml_step is None:
            raise Exception("Trigger step not found in workflow")
        step_queue = queue.Queue()
        step_queue.put({
            "step_to_be_processed": trigger_workflow_yaml_step,
            "previous_workflow_step": None,
            "previous_workflow_step_output": None
        })

        current_loop_step = None
        visited_steps = set()
        # visited_steps.add(trigger_workflow_yaml_step["name"])
        counter = 0
        while not step_queue.empty():
            counter = counter + 1
            print(f"___________________________Queue not empty : {counter}___________________________")
            print(step_queue.queue)
            print("size: ", step_queue.qsize())
            current_step = step_queue.get()
            # if current_step.get("step_to_be_processed").get("name") in visited_steps:
            #     continue
            print("Current Step :", current_step)
            print(f"Processing step: {current_step.get('step_to_be_processed').get('name')}")
            # Write logic to build Workflow step
            workflow_step_obj = self.build_step(current_step.get("step_to_be_processed"))
            print("Built Workflow Step : ", workflow_step_obj)
            # nested loop check
            self.check_nested_loop(current_loop_step, current_step, workflow_step_obj)

            # Connecting workflow steps
            print("________________Connecting workflow steps")
            print("Current Step : ", current_step)
            print("Workflow Step : ", workflow_step_obj)

            self.connect_workflow_step(current_step, workflow_step_obj)

            # Adding steps to the queue
            print("Visited Steps : ", visited_steps)
            if current_step.get("step_to_be_processed").get("name") not in visited_steps:
                print("_____________Adding to queue")
                print("Current Step : ", current_step.get("step_to_be_processed"))
                visited_steps.add(current_step.get("step_to_be_processed").get("name"))
                print(current_step.get("step_to_be_processed").get("next"))
                if current_step.get("step_to_be_processed").get("next") is not None:
                    self.add_next_steps_to_queue(agent_workflow, current_step, step_queue, workflow_step_obj)
                else:
                    print("No next step")
                    AgentWorkflowStep.add_next_workflow_step(self.session,
                                                             workflow_step_obj.id,
                                                             -1, "default" if current_step.get("step_to_be_processed")
                                                             .get("type") == "LOOP" else "COMPLETE")

            workflow_steps = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.agent_workflow_id == self.agent_workflow.id).all()
            sorted_workflow_steps = sorted(workflow_steps, key=lambda x: x.id)
            print("_______________________Workflow Steps : ")
            for step in sorted_workflow_steps:
                print(step)

    def connect_workflow_step(self, current_step, workflow_step):
        if current_step.get("previous_workflow_step") is not None:
            print(f"Connecting {current_step.get('previous_workflow_step')} to {workflow_step}")
            resp = AgentWorkflowStep.add_next_workflow_step(self.session, current_step.get("previous_workflow_step").id,
                                                     workflow_step.id,
                                                     current_step.get("previous_workflow_step_output"))
            print("Response : ", resp)
    def check_nested_loop(self, current_loop_step, current_step, workflow_step):
        if current_step.get("step_to_be_processed").get("type") == "LOOP":
            if current_loop_step is not None and current_loop_step != workflow_step:
                raise Exception("Nested loop not allowed")
        else:
            current_loop_step = workflow_step

    def add_next_steps_to_queue(self, agent_workflow, current_step, step_queue, workflow_step):
        print("Adding next steps to queue")
        next_steps = current_step.get("step_to_be_processed").get("next")
        print("Next Step : ", next_steps)
        branched_step_types = ["CONDITION", "WAIT_FOR_PERMISSION", "LOOP"]
        if current_step.get("step_to_be_processed").get("type") in branched_step_types:
            # handling loop steps next step
            print('handling loop steps next step')
            print(current_step.get("step_to_be_processed").get("type"))
            if current_step.get("step_to_be_processed").get("type") == "LOOP":
                print("Loop step")
                if next_steps.get("next_step") is not None:
                    step_queue.put({
                        "step_to_be_processed": self.get_step_by_name(agent_workflow, next_steps.get("next_step")),
                        "previous_workflow_step": workflow_step,
                        "previous_workflow_step_output": "default"
                    })
                else:
                    raise Exception("Loop step must have next")
                # handling exit step
                exit_loop_step = next_steps.get("exit_step") if next_steps.get("exit_step") else -1
                step_queue.put({
                    "step_to_be_processed": self.get_step_by_name(agent_workflow, exit_loop_step),
                    "previous_workflow_step": workflow_step,
                    "previous_workflow_step_output": "COMPLETE"
                })
            else:
                # Handling branched steps i.e. condition, wait for permission
                for next_step_info in next_steps:
                    next_step_name = next_step_info.get("step")
                    next_steps = self.get_step_by_name(agent_workflow, next_step_name)
                    if next_steps:
                        step_queue.put({
                            "step_to_be_processed": next_steps,
                            "previous_workflow_step": workflow_step,
                            "previous_workflow_step_output": next_step_info.get("output")
                        })
        else:
            # Handling next linear step i.e. tool step
            step_queue.put({
                "step_to_be_processed": self.get_step_by_name(agent_workflow, next_steps),
                "previous_workflow_step": workflow_step,
                "previous_workflow_step_output": "default"
            })

    # def parse_workflow_yaml(self, workflow_yaml):
    #     """Parse the workflow yaml content.
    #
    #     Args:
    #         workflow_yaml (str): The workflow content in .yaml format.
    #
    #     Returns:
    #         dict: The parsed workflow yaml content.
    #     """
    #
    #     workflow = []
    #
    #     for step_data in workflow_yaml:
    #         step = {
    #             "name": step_data["name"],
    #             "type": step_data["type"]
    #         }
    #
    #         if "trigger_step" in step_data:
    #             step["trigger_step"] = step_data["trigger_step"]
    #
    #         if "tool" in step_data:
    #             step["tool"] = step_data["tool"]
    #             step["instruction"] = step_data["instruction"]
    #
    #         if "next" in step_data:
    #             next_steps = []
    #
    #             if "next_step" in step_data["next"]:
    #                 next_steps.append({"output": "next_step", "step": step_data["next"]["next_step"]})
    #
    #             if "exit_step" in step_data["next"]:
    #                 next_steps.append({"output": "exit_step", "step": step_data["next"]["exit_step"]})
    #
    #             step["next"] = next_steps
    #
    #         workflow.append(step)
    #
    #     return workflow

    def find_trigger_step(self, workflow):
        """Find the trigger step in the workflow."""
        for step in workflow:
            if step.get("trigger_step"):
                return step
        raise Exception("Trigger step not found in workflow")

    def get_step_by_name(self, workflow, step_name):
        """Get the next step for the given step name."""
        print('get_step_by_name ', step_name)
        for step in workflow:
            if step["name"] == step_name:
                return step
        raise Exception(f"Step not found: {step_name}")

    def build_step(self, step):
        """Build agent workflow step."""
        # TODO: Add support for iteration workflow step, conditional workflow step

        agent_workflow_step = None
        if step["type"] == "TOOL":
            agent_workflow_step = AgentWorkflowStep.find_or_create_tool_workflow_step(session=self.session,
                                                                       agent_workflow_id=self.agent_workflow.id,
                                                                       unique_id=str(self.agent_workflow.id) + "_" +
                                                                                 step["name"],
                                                                       tool_name=step["tool"],
                                                                       input_instruction=step["instruction"])
        elif step["type"] == "LOOP":
            agent_workflow_step = AgentWorkflowStep.find_or_create_tool_workflow_step(session=self.session,
                                                                       agent_workflow_id=self.agent_workflow.id,
                                                                       unique_id=str(self.agent_workflow.id) + "_" +
                                                                                 step["name"],
                                                                       tool_name="TASK_QUEUE",
                                                                       input_instruction="Break the above response array of items",
                                                                       completion_prompt="Get array of items from the above response. Array should suitable utilization of JSON.parse().")
        elif step["type"] == "WAIT_FOR_PERMISSION":
            agent_workflow_step = AgentWorkflowStep.find_or_create_tool_workflow_step(session=self.session,
                                                                       agent_workflow_id=self.agent_workflow.id,
                                                                       unique_id=str(self.agent_workflow.id) + "_" +
                                                                                 step["name"],
                                                                       tool_name="WAIT_FOR_PERMISSION",
                                                                       input_instruction=step["instruction"])
        elif step["type"] == "WAIT":
            agent_workflow_step = AgentWorkflowStep.find_or_create_wait_workflow_step(session=self.session,
                                                                       agent_workflow_id=self.agent_workflow.id,
                                                                       unique_id=str(self.agent_workflow.id) + "_" +
                                                                                 step["name"],
                                                                       delay=step["duration"],
                                                                       wait_description=step["instruction"])
        elif step["type"] == "CONDITION":
            agent_workflow_step = AgentWorkflowStep.find_or_create_condition_workflow_step(session=self.session,
                                                                        agent_workflow_id=self.agent_workflow.id,
                                                                        unique_id=str(self.agent_workflow.id) + "_" +
                                                                                    step["name"],
                                                                        instruction=step["instruction"])



        if agent_workflow_step["trigger_step"] is True:
            agent_workflow_step.step_type = "TRIGGER"

        return agent_workflow_step


# def parse_workflow_yaml(workflow_yaml):
#     """Parse the workflow yaml content.
#
#     Args:
#         workflow_yaml (str): The workflow content in .yaml format.
#
#     Returns:
#         dict: The parsed workflow yaml content.
#     """
#
#     workflow = []
#
#     for step_data in workflow_yaml:
#         print("step_data :")
#         print(step_data)
#         step = {
#             "name": step_data["name"],
#             "type": step_data["type"]
#         }
#
#         if "trigger_step" in step_data:
#             step["trigger_step"] = step_data["trigger_step"]
#
#         if "tool" in step_data:
#             step["tool"] = step_data["tool"]
#             step["instruction"] = step_data["instruction"]
#
#         if "next" in step_data:
#             next_steps = []
#
#             if "next_step" in step_data["next"]:
#                 next_steps.append({"output": "next_step", "step": step_data["next"]["next_step"]})
#
#             if "exit_step" in step_data["next"]:
#                 next_steps.append({"output": "exit_step", "step": step_data["next"]["exit_step"]})
#
#             step["next"] = next_steps
#
#         workflow.append(step)
#
#     return workflow
def read_yaml_file(file_path):
    print("file_path :")
    print(file_path)
    try:
        with open(file_path, 'r') as yaml_file:
            yaml_content = yaml.load(yaml_file, Loader=yaml.FullLoader)
        return yaml_content
    except FileNotFoundError:
        raise Exception(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading YAML file: {str(e)}")


# run above methods write main
import yaml

if __name__ == "__main__":
    test_yaml = read_yaml_file(
        "/Users/abhijeetsinha/abhijeet/Code/SuperAGI/SuperAGI/superagi/agent/agent_workflow.yaml")
    print("YAML :")
    print(test_yaml)
    for data in test_yaml["steps"]:
        print("data :")
        print(data)

    engine = connect_db()
    # db_host = get_config('DB_HOST', 'super__postgres')
    # db_url = get_config('DB_URL', None)
    # db_username = get_config('DB_USERNAME')
    # db_password = get_config('DB_PASSWORD')
    # db_name = get_config('DB_NAME')
    # env = get_config('ENV', "DEV")
    #
    # if db_url is None:
    #     if db_username is None:
    #         db_url = f'postgresql://{db_host}/{db_name}'
    #     else:
    #         db_url = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
    # else:
    #     db_url = urlparse(db_url)
    #     db_url = db_url.scheme + "://" + db_url.netloc + db_url.path
    #
    # engine = create_engine(db_url,
    #                        pool_size=20,  # Maximum number of database connections in the pool
    #                        max_overflow=50,  # Maximum number of connections that can be created beyond the pool_size
    #                        pool_timeout=30,  # Timeout value in seconds for acquiring a connection from the pool
    #                        pool_recycle=1800,  # Recycle connections after this number of seconds (optional)
    #                        pool_pre_ping=False,  # Enable connection health checks (optional)
    #                        )
    print("We got engine : ", engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    print("Session : ", session)
    agent_workflow = AgentWorkflow.find_or_create_by_name(session, "Test-Yaml-Workflow-Sales",
                                                          "Testing Sales Yaml to workflow")
    print("Agent Workflow here: ", agent_workflow)
    AgentWorkflowBuilder(session, agent_workflow).build_workflow_from_yaml(test_yaml["steps"])
    # session.close()
    # engine.dispose()
    # response = parse_workflow_yaml(test_yaml["steps"])
    # print("Response :")
    # print(response)

# Exceptions, validation and assumptions
# -------------------------
# All steps except the loop end and terminal step must have next
# tool step : if it is a tool step it must have tool, instruction and next
# loop step : if it is a loop step it must have next containing next_step and exit_step
#             if exit step is not provided it will be considered as terminal step and workflow will terminate once loop is completed
# condition step : if it is a condition step it must have next containing output and step
#                  if output is not provided it will be considered as terminal step and workflow will terminate once condition is completed
# wait step: if it is a wait step it must have duration and next
#            if next is not provided it will be considered as terminal step and workflow will terminate once wait is completed
# wait for permission step: if it is a wait for permission step it must have next, output can be only YES and NO as action console just support them

#Need to add validation on valid types

#To Discuss:
#what will happen if we have multiple trigger steps?
#Can we end on wait for permission step?
#Can we end on wait step?
#Can we end on condition step?
#Do we need prompting in types and iteration workflow and wait for permission step in fronetnd?
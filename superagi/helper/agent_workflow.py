import yaml

from fastapi import HTTPException

from fastapi_sqlalchemy import db

from superagi.agent.agent_workflow_validator import AgentWorkflowValidator
from superagi.models.workflows.agent_workflow import AgentWorkflow


class AgentWorkflowHelper:
    @staticmethod
    def list_agent_workflows(organisation_id: int):
        agent_workflows = AgentWorkflow.find_by_organisation_id(session=db.session, organisation_id=1)
        output = []
        for agent_workflow in agent_workflows:
            output.append(agent_workflow.to_dict())
        return output

    @staticmethod
    def create_agent_workflow(name: str, description: str, organisation_id: int):
        agent_workflow = AgentWorkflow.find_or_create_by_name(session=db.session,
                                                        name=name,
                                                        description=description,
                                                        organisation_id=1)
        if agent_workflow is None:
            raise HTTPException(status_code=500, detail=f"Agent workflow: {name} not created")

        return {"success": True, "agent_workflow_id": agent_workflow.id}

    @staticmethod
    def get_agent_workflow(agent_workflow_id: int):
        agent_workflow = AgentWorkflow.find_by_id(session=db.session, id=agent_workflow_id)

        if agent_workflow is None:
            raise HTTPException(status_code=404, detail="Agent Workflow not found")
        return {"agent_workflow_name": agent_workflow.name,
                "agent_workflow_description": agent_workflow.description,
                "agent_workflow_code": agent_workflow.code_yaml if agent_workflow.code_yaml is not None else ""}

    @staticmethod
    def add_or_update_agent_workflow_code(agent_workflow_id: int, agent_workflow_code_yaml: str, organisation_id: int):
        sample_yaml_str = """
            #comment testing
            steps:
              - name: "Step1"
                trigger_step: true
                type: "TOOL"
                tool: "List File"
                instruction: "List the files from the resource manager"
                next: "Step2"
            
              - name: "Step2"
                type: "LOOP"
                next:
                  next_step: "Step3"
                  exit_step: "Step6"
            
              - name: "Step3"
                type: "TOOL"
                tool: "Read File"
                instruction: "Read the resume from above input"
                next: "Step4"
            
              - name: "Step4"
                type: "CONDITION"
                instruction: "Check if the resume matches High-Level GOAL"
                next:
                  - output: "NO"
                    step: "Step2"
                  - output: "YES"
                    step: "Step5"
            
              - name: "Step5"
                type: "TOOL"
                tool: "Send Email"
                instruction: "Write a custom Email the candidates for job profile based on their experience"
                next: "Step2"
            
              - name: "Step6"
                type: "TOOL"
                tool: "Write File"
                instruction: "Write a summary about the work done so far in a file named workflow_summary.txt"
                next: "Step2"
        """
        print("agent_workflow_code_yaml test print", sample_yaml_str)
        print(type(sample_yaml_str))
        yaml_content = yaml.load(sample_yaml_str, Loader=yaml.FullLoader)
        print("agent_workflow_code_yaml test print after yaml", yaml_content)
        print(type(yaml_content))
        AgentWorkflowValidator(db.session, organisation_id).validate_workflow_steps(workflow_steps=
                                                                                    yaml_content)
        agent_workflow = AgentWorkflow.add_or_update_agent_workflow_code_yaml(session=db.session, id=agent_workflow_id,
                                                             agent_workflow_code_yaml=sample_yaml_str)
        if agent_workflow is None:
            raise HTTPException(status_code=404, detail="Agent Workflow not found")

        return {"success": True}
from sqlalchemy import Column, Integer, String, Text

from superagi.models.base_model import DBBaseModel

import ast
import json
from superagi.models.knowledges import Knowledges

from superagi.models.tool import Tool
from superagi.models.workflows.agent_workflow import AgentWorkflow


class AgentExecutionConfiguration(DBBaseModel):
    """
    Agent Execution related configurations like goals, instructions are stored here

    Attributes:
        id (int): The unique identifier of the agent execution config.
        agent_execution_id (int): The identifier of the associated agent execution.
        key (str): The key of the configuration setting.
        value (str): The value of the configuration setting.
    """

    __tablename__ = 'agent_execution_configs'

    id = Column(Integer, primary_key=True)
    agent_execution_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the AgentExecutionConfig object.

        Returns:
            str: String representation of the AgentTemplateConfig.
        """

        return f"AgentExecutionConfig(id={self.id}, agent_execution_id='{self.agent_execution_id}', " \
               f"key='{self.key}', value='{self.value}')"

    @classmethod
    def add_or_update_agent_execution_config(cls, session, execution, agent_execution_configs):
        agent_execution_configurations = [
            AgentExecutionConfiguration(agent_execution_id=execution.id, key=key, value=str(value))
            for key, value in agent_execution_configs.items()
        ]
        for agent_execution in agent_execution_configurations:
            agent_execution_config = (
                session.query(AgentExecutionConfiguration)
                .filter(
                    AgentExecutionConfiguration.agent_execution_id == execution.id,
                    AgentExecutionConfiguration.key == agent_execution.key
                )
                .first()
            )

            if agent_execution_config:
                agent_execution_config.value = str(agent_execution.value)
            else:
                agent_execution_config = AgentExecutionConfiguration(
                    agent_execution_id=execution.id,
                    key=agent_execution.key,
                    value=str(agent_execution.value)
                )
                session.add(agent_execution_config)
            session.commit()

    @classmethod
    def fetch_configuration(cls, session, execution_id):
        """
        Fetches the execution configuration of an agent.

        Args:
            session: The database session object.
            execution (AgentExecution): The AgentExecution of the agent.

        Returns:
            dict: Parsed agent configuration.

        """
        agent_configurations = session.query(AgentExecutionConfiguration).filter_by(
            agent_execution_id=execution_id).all()
        parsed_config = {
            "goal": [],
            "instruction": [],
        }
        if not agent_configurations:
            return parsed_config
        for item in agent_configurations:
            parsed_config[item.key] = cls.eval_agent_config(item.key, item.value)
        return parsed_config

    @classmethod
    def eval_agent_config(cls, key, value):
        """
        Evaluates the value of an agent execution configuration setting based on its key.

        Args:
            key (str): The key of the execution configuration setting.
            value (str): The value of execution configuration setting.

        Returns:
            object: The evaluated value of the execution configuration setting.

        """

        if key == "goal" or key == "instruction":
            return eval(value)

    @classmethod
    def build_agent_execution_config(cls, session, agent, results_agent, results_agent_execution, total_calls, total_tokens):
        results_agent_dict = {result.key: result.value for result in results_agent}
        results_agent_execution_dict = {result.key: result.value for result in results_agent_execution}

        for key, value in results_agent_execution_dict.items():
            if key in results_agent_dict and value is not None:
                results_agent_dict[key] = value

        # Construct the response
        if 'goal' in results_agent_dict:
            results_agent_dict['goal'] = eval(results_agent_dict['goal'])

        if "toolkits" in results_agent_dict:
            results_agent_dict["toolkits"] = list(ast.literal_eval(results_agent_dict["toolkits"]))

        if 'tools' in results_agent_dict:
            results_agent_dict["tools"] = list(ast.literal_eval(results_agent_dict["tools"]))
            tools = session.query(Tool).filter(Tool.id.in_(results_agent_dict["tools"])).all()
            results_agent_dict["tools"] = tools
        if 'instruction' in results_agent_dict:
            results_agent_dict['instruction'] = eval(results_agent_dict['instruction'])

        if 'constraints' in results_agent_dict:
            results_agent_dict['constraints'] = eval(results_agent_dict['constraints'])

        results_agent_dict["name"] = agent.name
        agent_workflow = AgentWorkflow.find_by_id(session, agent.agent_workflow_id)
        results_agent_dict["agent_workflow"] = agent_workflow.name
        results_agent_dict["description"] = agent.description
        results_agent_dict["calls"] = total_calls
        results_agent_dict["tokens"] = total_tokens

        knowledge_name = ""
        if 'knowledge' in results_agent_dict and results_agent_dict['knowledge'] != 'None':
            if type(results_agent_dict['knowledge'])==int:
                results_agent_dict['knowledge'] = int(results_agent_dict['knowledge'])
            knowledge = session.query(Knowledges).filter(Knowledges.id == results_agent_dict['knowledge']).first()
            knowledge_name = knowledge.name if knowledge is not None else ""
        results_agent_dict['knowledge_name'] = knowledge_name

        return results_agent_dict

    @classmethod
    def build_scheduled_agent_execution_config(cls, session, agent, results_agent, total_calls, total_tokens):
        results_agent_dict = {result.key: result.value for result in results_agent}
            
        # Construct the response
        if 'goal' in results_agent_dict:
            results_agent_dict['goal'] = eval(results_agent_dict['goal'])

        if "toolkits" in results_agent_dict:
            results_agent_dict["toolkits"] = list(ast.literal_eval(results_agent_dict["toolkits"]))

        if 'tools' in results_agent_dict:
            results_agent_dict["tools"] = list(ast.literal_eval(results_agent_dict["tools"]))
            tools = session.query(Tool).filter(Tool.id.in_(results_agent_dict["tools"])).all()
            results_agent_dict["tools"] = tools
        if 'instruction' in results_agent_dict:
            results_agent_dict['instruction'] = eval(results_agent_dict['instruction'])

        if 'constraints' in results_agent_dict:
            results_agent_dict['constraints'] = eval(results_agent_dict['constraints'])

        results_agent_dict["name"] = agent.name
        agent_workflow = AgentWorkflow.find_by_id(session, agent.agent_workflow_id)
        results_agent_dict["agent_workflow"] = agent_workflow.name
        results_agent_dict["description"] = agent.description
        results_agent_dict["calls"] = total_calls
        results_agent_dict["tokens"] = total_tokens

        knowledge_name = ""
        if 'knowledge' in results_agent_dict and results_agent_dict['knowledge'] != 'None':
            if type(results_agent_dict['knowledge'])==int:
                results_agent_dict['knowledge'] = int(results_agent_dict['knowledge'])
            knowledge = session.query(Knowledges).filter(Knowledges.id == results_agent_dict['knowledge']).first()
            knowledge_name = knowledge.name if knowledge is not None else ""
        results_agent_dict['knowledge_name'] = knowledge_name 

        return results_agent_dict
    
    @classmethod
    def fetch_value(cls, session, execution_id: int, key: str):
        """
           Fetches the value of a specific execution configuration setting for an agent.

           Args:
               session: The database session object.
               execution_id (int): The ID of the agent execution.
               key (str): The key of the execution configuration setting.

           Returns:
               AgentExecutionConfiguration: The execution configuration setting object if found, else None.

       """

        return session.query(AgentExecutionConfiguration).filter(
            AgentExecutionConfiguration.agent_execution_id == execution_id,
            AgentExecutionConfiguration.key == key).first()
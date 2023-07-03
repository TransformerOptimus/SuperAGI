from sqlalchemy import Column, Integer, String, Text

from superagi.models.base_model import DBBaseModel


class AgentExecutionConfig(DBBaseModel):
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

        return f"AgentExecutionConfig(id={self.id}, agent_execution_id='{self.agent_template_id}', " \
               f"key='{self.key}', value='{self.value}')"

    @classmethod
    def add_or_update_agent_execution_config(cls, session, execution, agent_execution_config_request):
        agent_config_values = {
            "goal": agent_execution_config_request.goal,
            "instruction": agent_execution_config_request.instruction
        }

        agent_execution_configurations = [
            AgentExecutionConfig(agent_execution_id=execution.id, key=key, value=str(value))
            for key, value in agent_config_values.items()
        ]

        for key, value in agent_execution_configurations.items():
            agent_execution_config = (
                session.query(AgentExecutionConfig)
                .filter(
                    AgentExecutionConfig.agent_execution_id == execution.id,
                    AgentExecutionConfig.key == key
                )
                .first()
            )

            if agent_execution_config:
                agent_execution_config.value = str(value)
            else:
                agent_execution_config = AgentExecutionConfig(
                    agent_execution_id=execution.id,
                    key=key,
                    value=str(value)
                )
                session.add(agent_execution_config)

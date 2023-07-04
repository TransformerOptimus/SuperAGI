from sqlalchemy import Column, Integer, String, Text

from superagi.models.base_model import DBBaseModel


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
    def fetch_configuration(cls, session, execution):
        """
        Fetches the execution configuration of an agent.

        Args:
            session: The database session object.
            execution (AgentExecution): The AgentExecution of the agent.

        Returns:
            dict: Parsed agent configuration.

        """
        agent_configurations = session.query(AgentExecutionConfiguration).filter_by(
            agent_execution_id=execution.id).all()
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

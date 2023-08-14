from fastapi import HTTPException
from sqlalchemy import Column, Integer, String,Text

from superagi.helper.encyption_helper import decrypt_data
from superagi.models.base_model import DBBaseModel
from superagi.models.organisation import Organisation
from superagi.models.project import Project


class Configuration(DBBaseModel):
    """
    General org level configurations are stored here

    Attributes:
        id (Integer): The primary key of the configuration.
        organisation_id (Integer): The ID of the organization associated with the configuration.
        key (String): The configuration key.
        value (Text): The configuration value.
    """

    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    organisation_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the Configuration object.

        Returns:
            str: String representation of the Configuration object.
        """

        return f"Config(id={self.id}, organisation_id={self.organisation_id}, key={self.key}, value={self.value})"


    @classmethod
    def fetch_configuration(cls, session, organisation_id: int, key: str, default_value=None) -> str:
        """
        Fetches the configuration of an agent.

        Args:
            session: The database session object.
            organisation_id (int): The ID of the organisation.
            key (str): The key of the configuration.
            default_value (str): The default value of the configuration.

        Returns:
            dict: Parsed configuration.

        """

        configuration = session.query(Configuration).filter_by(organisation_id=organisation_id, key=key).first()
        if key == "model_api_key":
            return decrypt_data(configuration.value) if configuration else default_value
        else:
            return configuration.value if configuration else default_value

    @classmethod
    def fetch_value_by_agent_id(cls, session, agent_id: int, key: str):
        """
        Fetches the configuration of an agent.

        Args:
            session: The database session object.
            agent_id (int): The ID of the agent.
            key (str): The key of the configuration.

        Returns:
            dict: Parsed configuration.

        """
        from superagi.models.agent import Agent
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        project = session.query(Project).filter(Project.id == agent.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        organisation = session.query(Organisation).filter(Organisation.id == project.organisation_id).first()
        if not organisation:
            raise HTTPException(status_code=404, detail="Organisation not found")
        config = session.query(Configuration).filter(Configuration.organisation_id == organisation.id,
                                                     Configuration.key == key).first()
        if not config:
            return None
        return config.value if config else None

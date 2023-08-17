from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel
from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.models import Models
from superagi.helper.encyption_helper import decrypt_data

class ModelsConfig(DBBaseModel):
    """
    Represents a Model Config record in the database.

    Attributes:
        id (Integer): The unique identifier of the event.
        source_name (String): The name of the model provider.
        api_key (String): The api_key for individual model providers for every Organisation
        org_id (Integer): The ID of the organisation.
    """

    __tablename__ = 'models_config'

    id = Column(Integer, primary_key=True)
    source_name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    org_id = Column(Integer, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the ModelsConfig instance.
        """
        return f"ModelsConfig(id={self.id}, source_name={self.source_name}, " \
               f"org_id={self.org_id})"

    @classmethod
    def fetch_value_by_agent_id(cls, session, agent_id: int, model: str):
        """
        Fetches the configuration of an agent.

        Args:
            session: The database session object.
            agent_id (int): The ID of the agent.
            model (str): The model of the configuration.

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

        model_provider = session.query(Models).filter(Models.org_id == organisation.id, Models.model_name == model).first()
        if not model_provider:
            raise HTTPException(status_code=404, detail="Model provider not found")

        config = session.query(ModelsConfig.source_name, ModelsConfig.api_key).filter(ModelsConfig.org_id == organisation.id, ModelsConfig.id == model_provider.model_provider_id).first()

        if not config:
            return None

        return {"source_name": config.source_name, "api_key": decrypt_data(config.api_key)} if config else None
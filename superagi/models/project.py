from sqlalchemy import Column, Integer, String,ForeignKey
from superagi.models.base_model import DBBaseModel


class Project(DBBaseModel):
    """
    Model representing a project.

    Attributes:
        id (Integer): The primary key of the project.
        name (String): The name of the project.
        organisation_id (Integer): The ID of the organization to which the project belongs.
        description (String): The description of the project.
    """

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organisation_id = Column(Integer)
    description = Column(String)

    def __repr__(self):
        """
        Returns a string representation of the Project object.

        Returns:
            str: String representation of the Project object.
        """

        return f"Project(id={self.id}, name='{self.name}')"

    @classmethod
    def find_or_create_default_project(cls, session, organisation_id):
        """
            Finds or creates the default project for the given organization.

            Args:
                session: The database session.
                organisation_id (int): The ID of the organization.

            Returns:
                Project: The found or created default project.
        """
        project = session.query(Project).filter(Project.organisation_id == organisation_id, Project.name == "Default Project").first()
        if project is None:
            default_project = Project(
                name="Default Project",
                organisation_id=organisation_id,
                description="New Default Project"
            )
            session.add(default_project)
            session.commit()
            session.flush()
        else:
            default_project = project
        return default_project

    @classmethod
    def find_by_org_id(cls, session, org_id: int):
        project = session.query(Project).filter(Project.organisation_id == org_id).first()
        return project
    
    @classmethod
    def find_by_id(cls, session, project_id: int):
        project = session.query(Project).filter(Project.id == project_id).first()
        return project
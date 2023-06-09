from sqlalchemy import Column, Integer, String,ForeignKey
from superagi.models.base_model import DBBaseModel


class Project(DBBaseModel):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organisation_id = Column(Integer)
    description = Column(String)

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}')"

    @classmethod
    def find_or_create_default_project(cls, session, organisation_id):
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

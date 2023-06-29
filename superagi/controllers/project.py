from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from superagi.models.project import Project
from superagi.models.organisation import Organisation
from fastapi import APIRouter
from superagi.helper.auth import check_auth
from superagi.lib.logger import logger
# from superagi.types.db import ProjectIn, ProjectOut

router = APIRouter()


class ProjectOut(BaseModel):
    id: int
    name: str
    organisation_id: int
    description: str

    class Config:
        orm_mode = True


class ProjectIn(BaseModel):
    name: str
    organisation_id: int
    description: str

    class Config:
        orm_mode = True

# CRUD Operations
@router.post("/add", response_model=ProjectOut, status_code=201)
def create_project(project: ProjectIn,
                   Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new project.

    Args:
        project (Project): Project data.

    Returns:
        dict: Dictionary containing the created project.

    Raises:
        HTTPException (status_code=404): If the organization with the specified ID is not found.

    """

    logger.info("Organisation_id : ", project.organisation_id)
    organisation = db.session.query(Organisation).get(project.organisation_id)

    if not organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    project = Project(
        name=project.name,
        organisation_id=organisation.id,
        description=project.description
    )

    db.session.add(project)
    db.session.commit()

    return project


@router.get("/get/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, Authorize: AuthJWT = Depends(check_auth)):
    """
    Get project details by project_id.

    Args:
        project_id (int): ID of the project.

    Returns:
        dict: Dictionary containing the project details.

    Raises:
        HTTPException (status_code=404): If the project with the specified ID is not found.

    """

    db_project = db.session.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="project not found")
    return db_project


@router.put("/update/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project: ProjectIn,
                   Authorize: AuthJWT = Depends(check_auth)):
    """
    Update a project detail by project_id.

    Args:
        project_id (int): ID of the project.
        project (Project): Updated project data.

    Returns:
        dict: Dictionary containing the updated project details.

    Raises:
        HTTPException (status_code=404): If the project with the specified ID is not found.
        HTTPException (status_code=404): If the organization with the specified ID is not found.

    """

    db_project = db.session.query(Project).get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.organisation_id:
        organisation = db.session.query(Organisation).get(project.organisation_id)
        if not organisation:
            raise HTTPException(status_code=404, detail="Organisation not found")
        db_project.organisation_id = organisation.id
    db_project.name = project.name
    db_project.description = project.description
    db.session.add(db_project)
    db.session.commit()
    return db_project


@router.get("/get/organisation/{organisation_id}")
def get_projects_organisation(organisation_id: int,
                              Authorize: AuthJWT = Depends(check_auth)):
    """
    Get all projects by organisation_id and create default if no project.

    Args:
        organisation_id (int): ID of the organisation.

    Returns:
        List[Project]: List of projects belonging to the organisation.

    Raises:
        HTTPException (status_code=404): If the organization with the specified ID is not found.

    """

    Project.find_or_create_default_project(db.session, organisation_id)
    projects = db.session.query(Project).filter(Project.organisation_id == organisation_id).all()
    if len(projects) <= 0:
        default_project = Project.find_or_create_default_project(db.session, organisation_id)
        projects.append(default_project)

    return projects

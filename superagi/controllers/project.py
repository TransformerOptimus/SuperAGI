from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from superagi.models.project import Project
from superagi.models.organisation import Organisation
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.helper.auth import check_auth

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Project), status_code=201)
def create_project(project: sqlalchemy_to_pydantic(Project, exclude=["id"]),
                   Authorize: AuthJWT = Depends(check_auth)):

    """Create a new project"""

    print("Organisation_id : ", project.organisation_id)
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


@router.get("/get/{project_id}", response_model=sqlalchemy_to_pydantic(Project))
def get_project(project_id: int, Authorize: AuthJWT = Depends(check_auth)):

    """Get Project details by project_id"""

    db_project = db.session.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="project not found")
    return db_project


@router.put("/update/{project_id}", response_model=sqlalchemy_to_pydantic(Project))
def update_project(project_id: int, project: sqlalchemy_to_pydantic(Project, exclude=["id"]),
                   Authorize: AuthJWT = Depends(check_auth)):

    """Update a project detail by project_id"""

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

    """Get all projects by organisation_id and create default if no project"""

    projects = db.session.query(Project).filter(Project.organisation_id == organisation_id).all()
    if not projects:
        default_project = Project(
            name="Default Project",
            organisation_id=organisation_id,
            description="New Default Project"
        )
        db.session.add(default_project)
        db.session.commit()
        db.session.flush()
        projects.append(default_project)

    return projects

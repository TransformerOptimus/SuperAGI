from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from superagi.models.project import Project
from superagi.models.project import Organisation
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Project), status_code=201)
def create_project(project: sqlalchemy_to_pydantic(Project, exclude=["id"]), Authorize: AuthJWT = Depends()):
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
def get_project(project_id: int, Authorize: AuthJWT = Depends()):
    db_project = db.session.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="project not found")
    return db_project


@router.put("/update/{project_id}", response_model=sqlalchemy_to_pydantic(Project))
def update_project(project_id: int, project: sqlalchemy_to_pydantic(Project, exclude=["id"]),
                   Authorize: AuthJWT = Depends()):
    print("New Project")
    print(project)
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
def get_projects_organisation(organisation_id: int):
    projects = db.session.query(Project).filter(Project.organisation_id == organisation_id).all()
    return projects

from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from superagi.models.budget import Budget
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Budget), status_code=201)
def create_budget(budget: sqlalchemy_to_pydantic(Budget, exclude=["id"]), Authorize: AuthJWT = Depends()):
    new_budget = Budget(
        budget=budget.budget,
        cycle=budget.cycle
    )
    db.session.add(new_budget)
    db.session.commit()

    return new_budget


@router.get("/get/{budget_id}", response_model=sqlalchemy_to_pydantic(Budget))
def get_budget(budget_id: int, Authorize: AuthJWT = Depends()):
    db_budget = db.session.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="budget not found")
    return db_budget


@router.put("/update/{budget_id}", response_model=sqlalchemy_to_pydantic(Budget))
def update_budget(budget_id: int, budget: sqlalchemy_to_pydantic(Budget, exclude=["id"]),
                  Authorize: AuthJWT = Depends()):
    db_budget = db.session.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="budget not found")

    db_budget.budget = budget.budget
    db_budget.cycle = budget.cycle
    db.session.commit()

    return db_budget

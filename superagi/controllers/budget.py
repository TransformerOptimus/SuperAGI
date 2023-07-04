from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from superagi.helper.auth import check_auth
from superagi.models.budget import Budget
# from superagi.types.db import BudgetIn, BudgetOut

router = APIRouter()


class BudgetOut(BaseModel):
    id: int
    budget: float
    cycle: str

    class Config:
        orm_mode = True


class BudgetIn(BaseModel):
    budget: float
    cycle: str

    class Config:
        orm_mode = True

@router.post("/add", response_model=BudgetOut, status_code=201)
def create_budget(budget: BudgetIn,
                  Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new budget.

    Args:
        budget: Budget details.

    Returns:
        Budget: Created budget.

    """

    new_budget = Budget(
        budget=budget.budget,
        cycle=budget.cycle
    )
    db.session.add(new_budget)
    db.session.commit()

    return new_budget


@router.get("/get/{budget_id}", response_model=BudgetOut)
def get_budget(budget_id: int,
               Authorize: AuthJWT = Depends(check_auth)):
    """
    Get a budget by budget_id.

    Args:
        budget_id: Budget ID.

    Returns:
        Budget: Retrieved budget.

    """

    db_budget = db.session.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="budget not found")
    return db_budget


@router.put("/update/{budget_id}", response_model=BudgetOut)
def update_budget(budget_id: int, budget: BudgetIn,
                  Authorize: AuthJWT = Depends(check_auth)):
    """
    Update budget details by budget_id.

    Args:
        budget_id: Budget ID.
        budget: Updated budget details.

    Returns:
        Budget: Updated budget.

    """

    db_budget = db.session.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="budget not found")

    db_budget.budget = budget.budget
    db_budget.cycle = budget.cycle
    db.session.commit()

    return db_budget

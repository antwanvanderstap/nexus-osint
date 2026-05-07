from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.models.case import Case, CaseCreate, create_case, delete_case, get_case, list_cases

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/", response_model=Case)
def new_case(data: CaseCreate, session: Session = Depends(get_session)) -> Case:
    return create_case(data, session)


@router.get("/", response_model=list[Case])
def all_cases(session: Session = Depends(get_session)) -> list[Case]:
    return list_cases(session)


@router.get("/{case_id}", response_model=Case)
def fetch_case(case_id: str, session: Session = Depends(get_session)) -> Case:
    case = get_case(case_id, session)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.delete("/{case_id}")
def remove_case(case_id: str, session: Session = Depends(get_session)) -> dict:
    if not delete_case(case_id, session):
        raise HTTPException(status_code=404, detail="Case not found")
    return {"deleted": case_id}

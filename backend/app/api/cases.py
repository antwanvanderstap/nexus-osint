from fastapi import APIRouter, HTTPException
from app.models.case import Case, CaseCreate, create_case, get_case, list_cases

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/", response_model=Case)
def new_case(data: CaseCreate) -> Case:
    return create_case(data)


@router.get("/", response_model=list[Case])
def all_cases() -> list[Case]:
    return list_cases()


@router.get("/{case_id}", response_model=Case)
def fetch_case(case_id: str) -> Case:
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

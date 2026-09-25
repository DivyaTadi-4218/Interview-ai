from fastapi import APIRouter

from data.companies import COMPANIES

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("")
def list_companies():
    return {"companies": COMPANIES}

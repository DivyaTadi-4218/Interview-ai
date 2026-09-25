from fastapi import APIRouter

from data.companies import DOMAINS, ROLES, EXPERIENCE_LEVELS, INTERVIEW_TYPES

router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("")
def list_domains():
    return {
        "domains": DOMAINS,
        "roles": ROLES,
        "experience_levels": EXPERIENCE_LEVELS,
        "interview_types": INTERVIEW_TYPES,
    }

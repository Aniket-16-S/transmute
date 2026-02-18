from fastapi import APIRouter

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.get("/")
def list_conversions():
    return {"conversions": []}

from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/")
def list_files():
    return {"files": []}

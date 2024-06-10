from fastapi import APIRouter


router = APIRouter(prefix="/v1/users", tags=["Users"])


@router.get("/")
def get_users():
    return []
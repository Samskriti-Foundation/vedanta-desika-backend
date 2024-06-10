from fastapi import APIRouter


router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.get("/")
def get_nodes_list():
    return []
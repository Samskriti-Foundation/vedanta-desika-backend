from fastapi import APIRouter


router = APIRouter(prefix="/v1/nodes", tags=["Nodes"])


@router.get("/")
def get_nodes_list():
    return []
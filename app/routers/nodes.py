from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import schemas, models, oauth2

router = APIRouter(prefix="/v1/nodes", tags=["Nodes"])


@router.get("/{project_id}")
def get_tree_list(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    is_project_member = db.query(models.UserProjectAssociation).filter(models.UserProjectAssociation.user_id == current_user.id, models.UserProjectAssociation.project_id == project_id).first()
    
    if not (current_user.is_superuser or is_project_member):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    root = db.query(models.Node).filter(models.Node.project_id == project_id, models.Node.left == 1).first()
    
    if not root:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Root node not found")
    
    def build_tree(node: models.Node):
        children = db.query(models.Node).filter(
            models.Node.project_id == project_id,
            models.Node.left > node.left,
            models.Node.right < node.right
        ).all()
        children_nodes = []
        i = node.left + 1
        while i < node.right:
            child = next((child for child in children if child.left == i), None)
            if child:
                children_nodes.append(build_tree(child))
                i = child.right + 1
            else:
                i += 1
        return {
            "id": node.id,
            "name": node.name,
            "children": children_nodes
        }
    
    tree = build_tree(root)
    
    return tree


@router.post("/")
def insert_node(node: schemas.NodeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == node.project_id).first()
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    is_project_member = db.query(models.UserProjectAssociation).filter(models.UserProjectAssociation.user_id == current_user.id, models.UserProjectAssociation.project_id == node.parent_id).first()
    
    if not (current_user.is_superuser or is_project_member):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    if node.parent_id == 0:
        if db.query(models.Node).filter(models.Node.project_id == node.project_id).count() == 0:
            root = models.Node(
                left=1,
                right=2,
                name=node.name,
                project_id=node.project_id
            )
            db.add(root)
            db.commit()
            return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": root.id})
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Root node already exists")
    
    if node.parent_id not in [node.id  for node in db.query(models.Node).all()]:
        # Parent node does not exist, throw error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent node does not exist")
    
    parent_node = db.query(models.Node).filter(models.Node.id == node.parent_id).first()
    
    db.query(models.Node).filter(models.Node.right > parent_node.left).update({models.Node.right: models.Node.right + 2}, synchronize_session=False)
    
    db.query(models.Node).filter(models.Node.left > parent_node.left).update({models.Node.left: models.Node.left + 2}, synchronize_session=False)

    new_node = models.Node(
        name=node.name,
        left=parent_node.left + 1,
        right=parent_node.left + 2,
        project_id=node.project_id
    )
    
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": new_node.id})
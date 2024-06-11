from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from app import schemas, models, oauth2
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/v1/projects", tags=["Projects"])


@router.get("/")
def get_projects(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.is_superuser:
        projects = db.query(models.Project).all()

    else:
        project_ids = db.query(models.UserProjectAssociation.project_id).filter(models.UserProjectAssociation.user_id == current_user.id).all()
        projects = db.query(models.Project).filter(models.Project.id.in_(project_ids)).all()

    return projects


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    owner = db.query(models.UserProjectAssociation).filter(models.UserProjectAssociation.project_id == project_id, models.UserProjectAssociation.role == "OWNER").first()
    
    if current_user.is_superuser or owner and owner.user_id == current_user.id:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
        return project

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")


@router.post("/")
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    project = models.Project(name=project.name, description=project.description)

    db.add(project)
    db.commit()
    db.refresh(project)

    owner = models.UserProjectAssociation(project_id=project.id, user_id=current_user.id, role="OWNER")
    db.add(owner)
    db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": project.id})
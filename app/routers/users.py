from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app import schemas, models, oauth2
from app.utils import utils
from typing import List

router = APIRouter(prefix="/v1/users", tags=["Users"])


@router.get("/", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    db_users = db.query(models.User).all()
    return db_users


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.post("/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.is_superuser == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email {user.email} already exists")
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password.decode('utf-8')
    
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=user.password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": db_user.id})
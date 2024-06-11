from fastapi import APIRouter

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import schemas, models, oauth2
from app.database import get_db
from app.utils import utils

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
    )

@router.post('/login',response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    if not utils.verify(user_credentials.password, user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={'email': user.email, 'id': user.id})
    refresh_token = oauth2.create_refresh_token(data={'email': user.email, 'id': user.id})
    
    return {'access_token':access_token, 'refresh_token':refresh_token,'token_type':'bearer'}


# @router.post("/refresh")
# def refresh(refresh_token: schemas.RefreshToken, db: Session = Depends(get_db)):
#     """
#     This function refreshes the access token using the provided refresh token.
#     It verifies the access token and retrieves the associated DBManager from the database.
#     If the DBManager does not exist, it raises an HTTPException with a 404 status code.
#     It then creates a new access token based on the retrieved data and returns it.
    
#     Parameters:
#         - refresh_token (schemas.RefreshToken): The refresh token used to generate a new access token.
#         - db (Session): The database session object.

#     Returns:
#         - dict: A dictionary containing the new access token and the token type 'bearer'.
#     """
#     data = oauth2.verify_access_token(refresh_token.refresh_token, credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}))
    
#     db_manager = db.query(models.DBManager).filter(models.DBManager.email == data.email).first()

#     if not db_manager:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
#     access_token = oauth2.create_access_token(data={'email': data.email, 'role': data.role, 'access': data.access})
#     return {'access_token':access_token, 'token_type':'bearer'}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_superuser(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email {user.email} already exists")
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password.decode('utf-8')
    
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=user.password,
        is_superuser=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": db_user.id})
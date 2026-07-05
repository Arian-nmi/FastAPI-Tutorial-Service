from fastapi import APIRouter, Path, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from users.models import UserModel
from users.schemas import *
from sqlalchemy.orm import Session
from core.database import get_db
from auth.jwt_auth import generate_access_token, generate_refresh_token, decode_refresh_token


router = APIRouter(tags=["users"], prefix="/users")

@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(username=request.username.lower()).first()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user doesn't exists")

    if not user_obj.verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password or username")
    
    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)
    return JSONResponse(content={"detail": "user logged in successfully", "access_token": access_token, "refresh_token": refresh_token})


@router.post("/register")
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=request.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists")
    
    user_obj = UserModel(username=request.username.lower())
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "user registered successfully"})


@router.post("/refresh-token")
async def user_refresh_token(request: UserRefreshTokenSchema, db: Session = Depends(get_db)):
    user_id = decode_refresh_token(request.refresh_token)
    access_token = generate_access_token(user_id)
    
    return JSONResponse(content={"access_token": access_token})



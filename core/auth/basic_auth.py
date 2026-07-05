from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from users.models import UserModel
from core.database import get_db
from sqlalchemy.orm import Session


security = HTTPBasic()

def get_authenticate_username(
        credential: HTTPBasicCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
    user_obj = db.query(UserModel).filter_by(username=credential.username).one_or_none()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password or username",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if not user_obj.verify_password(credential.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password or username",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user_obj


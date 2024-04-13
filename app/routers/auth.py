from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import session
from ..database import get_db
from .. import utils, schemas, models, oauth2

router = APIRouter(
    tags = ['Authentication']
)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db: session = Depends(get_db)):
    user= db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Credentials") 
    plain_pword = user_credentials.password
    hashed_pword = user.password.encode('utf-8')
    password_check = utils.verify_password(plain_password=plain_pword, hashed_password=hashed_pword)
    if not password_check:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Credentials") 
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}   
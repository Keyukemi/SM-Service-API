from sqlalchemy import and_
from typing import List, Optional
from fastapi import HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from app import oauth2
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/messages", 
    tags= ['Messages']
)

#creating a message
@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.MessageResponse)
def create_message(message: schemas.Message, db: Session = Depends(get_db), 
                 current_user: int = Depends(oauth2.get_current_user)):
    recipient = db.query(models.User).filter(models.User.id == message.receiver_id).first()
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    new_message = models.Messages(sender_id=current_user.id, receiver_id=message.receiver_id, content=message.content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

#getting messages
@router.get("/", response_model= List[schemas.MessageResponse])
def get_messages(db: Session = Depends(get_db), 
              current_user: int = Depends(oauth2.get_current_user),
              limit:int = 10, skip:int = 0, search: Optional[str] = ""):
    
    filter_conditions = [models.Messages.sender_id == current_user.id]
    if search:
        filter_conditions.append(models.Messages.content.contains(f"%{search}%"))
    combined_filter_condition = and_(*filter_conditions)

    messages = db.query(models.Messages).filter(combined_filter_condition).limit(limit).offset(skip).all()

    return messages  


#deleting a Message
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    message_query = db.query(models.Messages).filter(models.Messages.id == id)
    deleted_message = message_query.first()
    if  deleted_message == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"Message with id: {id} was not found")
    if deleted_message.sender_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")

    message_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
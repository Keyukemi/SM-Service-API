from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session

from app import oauth2
from .. import models, schemas, utils
from ..database import get_db


router = APIRouter(
    prefix="/users",
    tags= ['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.UserResponse)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db), ):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    hashed_password= utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  
    return new_user

@router.get("/{id}", response_model= schemas.UserResponse)
def get_user(id:int, db: Session = Depends(get_db), ):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found")
    return user


#ROUTER FOR FRIENDSHIP (since it's a user activity)
# 1. send friend request 
@router.post("/send_request/{friend_id}")
def send_friend_request(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):

    friend = db.query(models.User).filter(models.User.id == friend_id).first()
    if not friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {friend_id} not found")

    existing_request = db.query(models.Friendlist).filter(
        (models.Friendlist.user_id == current_user.id) &
        (models.Friendlist.friend_id == friend_id)
    ).first()
    if existing_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request already sent")
    if (current_user.id == friend_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't send friend request to self")

    friendship = models.Friendlist(user_id=current_user.id, friend_id=friend_id)
    db.add(friendship)
    db.commit()
    return {"message": "Friend request sent successfully"}

# 2. Respond to friend request  response_model= schemas.FriendshipResponse
@router.put("/respond_request/{request_id}", response_model= schemas.FriendshipResponse)
def friend_request_response(
    request_id: int,
    decision_response: schemas.FriendshipRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
  
    friendship_query = db.query(models.Friendlist).filter(
        (models.Friendlist.id == request_id) &
        (models.Friendlist.friend_id == current_user.id) &
        (models.Friendlist.status == "pending")
    )
    
    friendship_update = friendship_query.first()

    if friendship_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    
    # if friendship_update.id != request_id:
    #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid request ID")
    
    if friendship_update.friend_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to respond to this request")
    
    if friendship_update.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request already responded")
    
    if decision_response.status not in schemas.FriendshipStatus:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid friendship status. Kindly pass in accepted or rejected as a valid status")

    friendship_update.status = decision_response.status
    friendship_update.updated_at = datetime.now(timezone.utc)

    db.commit()
    return friendship_update


#note that user_id is the person sending the request and friend_id is the one who recieved it

# 3. Get all friends
@router.get("/friends/", response_model=List[schemas.UserResponse])
def get_friends(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):

    query = db.query(models.Friendlist).filter(models.Friendlist.user_id == current_user.id)
    if status:
        query = query.filter(models.Friendlist.status == status)
    friend_entries = query.all()
    
    friend_ids = [entry.friend_id for entry in friend_entries]
    
    friends = db.query(models.User).filter(models.User.id.in_(friend_ids)).all()
    
    return friends
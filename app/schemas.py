from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, conint
from typing import Optional

#pydantic model for defining the shape of the request

class CreateUser(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    

class CreatePost(PostBase):
    pass

class PostResponse(PostBase):
    user_id: int
    created_at: datetime
    owner: UserResponse
    class Config:
        from_attributes = True


class UserLogin (BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token:str
    token_type: str

class TokenData (BaseModel):
    id: Optional[str]

class LikePost (BaseModel):
    post_id: int
    dir: bool

class PostLikes (BaseModel):
    Post: PostResponse
    likes_count: int
    class Config:
        from_attributes = True


class FriendshipStatus(str, Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'

class Friendship(BaseModel):
    user_id: int
    friend_id: int
    status: FriendshipStatus

class FriendshipRequest (BaseModel):
    status: FriendshipStatus

class FriendshipResponse(BaseModel):
    id: int
    status: str
    updated_at: datetime
    class Config:
        from_attributes = True

class Comment(BaseModel):
    post_id: int
    content: str

class CommentResponse(Comment):
    post_owner: str
    commenter: str
    created_at: datetime
    class Config:
        from_attributes = True

class Message(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(Message):
    id: int 
    sender_id: int
    created_at: datetime
    class Config:
        from_attributes = True
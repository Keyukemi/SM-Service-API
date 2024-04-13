from datetime import datetime
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
    email: EmailStr
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

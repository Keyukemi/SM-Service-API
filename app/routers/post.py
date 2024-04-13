
from sqlalchemy import and_
from typing import List, Optional
from fastapi import HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import oauth2
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/posts", 
    tags= ['Post']
)

#getting all posts in the database (as long as user is logged in)
#@router.get("/all")
@router.get("/feed", response_model= List[schemas.PostLikes])
def get_posts(db: Session = Depends(get_db), 
            current_user: int = Depends(oauth2.get_current_user),
            limit:int = 10, skip:int = 0, search: Optional[str] = ""):
    
    # posts = db.query(models.Post).filter(models.Post.content.contains(search)).limit(limit).offset(skip).all()

    post_likes = db.query(models.Post, func.count(models.Likes.post_id).label("likes_count")).join(
        models.Likes, models.Likes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.content.contains(search)).limit(limit).offset(skip).all()
    return post_likes 

#getting all posts from a user
@router.get("/", response_model= List[schemas.PostLikes])
def get_posts(db: Session = Depends(get_db), 
              current_user: int = Depends(oauth2.get_current_user),
              limit:int = 10, skip:int = 0, search: Optional[str] = ""):
    
    filter_conditions = [models.Post.user_id == current_user.id]
    if search:
        filter_conditions.append(models.Post.content.contains(f"%{search}%"))
    combined_filter_condition = and_(*filter_conditions)

    posts = db.query(models.Post, func.count(models.Likes.post_id).label("likes_count")).join(
        models.Likes, models.Likes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(combined_filter_condition).limit(limit).offset(skip).all()

    return posts  

#creating a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.PostResponse)
def create_posts(post: schemas.CreatePost, db: Session = Depends(get_db), 
                 current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(user_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

  
#retrieving a single post
@router.get("/{id}", response_model= schemas.PostLikes)
def get_post(id:int, db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user) ):
    
    #post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Likes.post_id).label("likes_count")).join(
        models.Likes, models.Likes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found")
    if post.Post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")
    return post 


#updating a post
@router.put("/{id}", response_model= schemas.PostResponse)
def update_post(id:int, post: schemas.PostBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    if updated_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")
    
    post_query.update(post.model_dump(),synchronize_session=False )
    db.commit()
    return  post_query.first()

#deleting a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = post_query.first()
    if  deleted_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    if deleted_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
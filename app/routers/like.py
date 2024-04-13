from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session

from app import oauth2
from .. import models, schemas
from ..database import get_db

router = APIRouter( 
    prefix="/like",
    tags= ['Like']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def like_posts(like: schemas.LikePost, db: Session = Depends(get_db), 
                 current_user: int = Depends(oauth2.get_current_user)):
    existing_post = db.query(models.Post).filter(models.Post.id == like.post_id).first()
    if not existing_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"post {like.post_id} does not exist")
 
    like_query = db.query(models.Likes).filter(models.Likes.post_id == like.post_id, 
                                            models.Likes.user_id == current_user.id)
    found_like = like_query.first()
    if(like.dir == True):
        if found_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"user {current_user.id} already liked the post {like.post_id}")
        new_like = models.Likes(post_id = like.post_id, user_id = current_user.id)
        db.add(new_like)
        db.commit()
        return{"message":"successfully liked post"}
    else:
        if not found_like:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"post {like.post_id} not found")
        like_query.delete(synchronize_session=False)
        db.commit()
    return {}
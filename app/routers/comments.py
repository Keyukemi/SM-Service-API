from sqlalchemy import and_
from typing import Optional
from fastapi import HTTPException, Response, status, Depends, APIRouter
from sqlalchemy.orm import Session
from app import oauth2
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/comments", 
    tags= ['Comments']
)

#creating a comment
@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.CommentResponse)
def create_message(comment: schemas.Comment, db: Session = Depends(get_db), 
                 current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    owner_name = db.query(models.User.name).filter(models.User.id == post.user_id).scalar()
    comment_owner = db.query(models.User.name).filter(models.User.id == current_user.id).scalar()

    new_comment = models.Comments(user_id=current_user.id, post_id=comment.post_id, content=comment.content)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    response = {
        "post_id": new_comment.post_id,
        "content": new_comment.content,
        "commenter": comment_owner,
        "post_owner": owner_name,
        "created_at": new_comment.created_at
    }
    return response

#getting comments
@router.get("/{id}",)
def get_comments(id:int, db: Session = Depends(get_db), 
              current_user: int = Depends(oauth2.get_current_user),
              limit:int = 10, skip:int = 0, search: Optional[str] = ""):
    
    filter_conditions = [models.Comments.post_id == id]
    if search:
        filter_conditions.append(models.Comments.content.contains(f"%{search}%"))
    combined_filter_condition = and_(*filter_conditions)

    comments = db.query(models.Comments).filter(combined_filter_condition).limit(limit).offset(skip).all()

    return comments  


#deleting a Message
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comments).filter(models.Comments.id == id)
    deleted_comment = comment_query.first()
    if  deleted_comment == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"Comment with id: {id} was not found")
    if deleted_comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")

    comment_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
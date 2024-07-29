from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, auth
from .database import SessionLocal, engine
from .auth import get_current_user, create_access_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/search/", response_model=List[schemas.User])
def search_users(name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.search_users(db, name=name, skip=skip, limit=limit)
    return users

@app.post("/discussions/", response_model=schemas.Discussion)
def create_discussion(
    discussion: schemas.DiscussionCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.create_discussion(db=db, discussion=discussion, user_id=current_user.id)

@app.get("/discussions/", response_model=List[schemas.Discussion])
def read_discussions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    discussions = crud.get_discussions(db, skip=skip, limit=limit)
    return discussions

@app.get("/discussions/{discussion_id}", response_model=schemas.Discussion)
def read_discussion(discussion_id: int, db: Session = Depends(get_db)):
    db_discussion = crud.get_discussion(db, discussion_id=discussion_id)
    if db_discussion is None:
        raise HTTPException(status_code=404, detail="Discussion not found")
    return db_discussion

@app.put("/discussions/{discussion_id}", response_model=schemas.Discussion)
def update_discussion(
    discussion_id: int, 
    discussion: schemas.DiscussionCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_user)
):
    db_discussion = crud.get_discussion(db, discussion_id=discussion_id)
    if db_discussion is None:
        raise HTTPException(status_code=404, detail="Discussion not found")
    if db_discussion.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this discussion")
    return crud.update_discussion(db=db, discussion_id=discussion_id, discussion_update=discussion)

@app.delete("/discussions/{discussion_id}", response_model=bool)
def delete_discussion(
    discussion_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(get_current_user)
):
    db_discussion = crud.get_discussion(db, discussion_id=discussion_id)
    if db_discussion is None:
        raise HTTPException(status_code=404, detail="Discussion not found")
    if db_discussion.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this discussion")
    return crud.delete_discussion(db=db, discussion_id=discussion_id)

@app.get("/discussions/hashtag/{hashtag}", response_model=List[schemas.Discussion])
def read_discussions_by_hashtag(
    hashtag: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    discussions = crud.get_discussions_by_hashtag(db, hashtag=hashtag, skip=skip, limit=limit)
    return discussions

@app.post("/discussions/{discussion_id}/comments/", response_model=schemas.Comment)
def create_comment(
    discussion_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.create_comment(db=db, comment=comment, user_id=current_user.id, discussion_id=discussion_id)

@app.get("/discussions/{discussion_id}/comments/", response_model=List[schemas.Comment])
def read_comments(discussion_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_comments(db, discussion_id=discussion_id, skip=skip, limit=limit)

@app.post("/discussions/{discussion_id}/like", response_model=dict)
def like_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    crud.like_discussion(db=db, user_id=current_user.id, discussion_id=discussion_id)
    return {"message": "Discussion liked successfully"}

@app.delete("/discussions/{discussion_id}/like", response_model=dict)
def unlike_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    crud.unlike_discussion(db=db, user_id=current_user.id, discussion_id=discussion_id)
    return {"message": "Discussion unliked successfully"}

@app.post("/discussions/{discussion_id}/view", response_model=schemas.Discussion)
def view_discussion(discussion_id: int, db: Session = Depends(get_db)):
    return crud.increment_view_count(db=db, discussion_id=discussion_id)

@app.post("/users/{user_id}/follow/{target_id}", response_model=schemas.User)
def follow_user(
    user_id: int,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    return crud.follow_user(db=db, follower_id=user_id, followed_id=target_id)

@app.post("/users/{user_id}/unfollow/{target_id}", response_model=schemas.User)
def unfollow_user(
    user_id: int,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    return crud.unfollow_user(db=db, follower_id=user_id, followed_id=target_id)

@app.post("/comments/{comment_id}/reply", response_model=schemas.Comment)
def create_comment_reply(
    comment_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    parent_comment = crud.get_comment(db, comment_id)
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return crud.create_comment_reply(db=db, comment=comment, user_id=current_user.id, discussion_id=parent_comment.discussion_id, parent_id=comment_id)

@app.post("/comments/{comment_id}/like", response_model=dict)
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    crud.like_comment(db=db, user_id=current_user.id, comment_id=comment_id)
    return {"message": "Comment liked successfully"}

@app.delete("/comments/{comment_id}/like", response_model=dict)
def unlike_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    crud.unlike_comment(db=db, user_id=current_user.id, comment_id=comment_id)
    return {"message": "Comment unliked successfully"}

@app.put("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(
    comment_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    return crud.update_comment(db=db, comment_id=comment_id, comment_update=comment)

@app.delete("/comments/{comment_id}", response_model=bool)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    return crud.delete_comment(db=db, comment_id=comment_id)
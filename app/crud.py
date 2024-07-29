from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    if get_user_by_email(db, email=user.email):
        raise ValueError("Email already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(name=user.name, email=user.email, mobile_no=user.mobile_no, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def search_users(db: Session, name: str, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.name.ilike(f"%{name}%")).offset(skip).limit(limit).all()

def create_discussion(db: Session, discussion: schemas.DiscussionCreate, user_id: int):
    db_discussion = models.Discussion(text=discussion.text, image=discussion.image, user_id=user_id)
    db.add(db_discussion)
    db.commit()
    db.refresh(db_discussion)

    for hashtag_name in discussion.hashtags:
        hashtag = get_or_create_hashtag(db, hashtag_name)
        db_discussion.hashtags.append(hashtag)

    db.commit()
    db.refresh(db_discussion)
    return db_discussion

def get_or_create_hashtag(db: Session, hashtag_name: str):
    hashtag = db.query(models.Hashtag).filter(models.Hashtag.name == hashtag_name).first()
    if not hashtag:
        hashtag = models.Hashtag(name=hashtag_name)
        db.add(hashtag)
        db.commit()
        db.refresh(hashtag)
    return hashtag

def get_discussion(db: Session, discussion_id: int):
    return db.query(models.Discussion).filter(models.Discussion.id == discussion_id).first()

def get_discussions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Discussion).offset(skip).limit(limit).all()

def update_discussion(db: Session, discussion_id: int, discussion_update: schemas.DiscussionCreate):
    db_discussion = get_discussion(db, discussion_id)
    if db_discussion:
        update_data = discussion_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key != "hashtags":
                setattr(db_discussion, key, value)
        
        db_discussion.hashtags.clear()
        for hashtag_name in discussion_update.hashtags:
            hashtag = get_or_create_hashtag(db, hashtag_name)
            db_discussion.hashtags.append(hashtag)

        db.commit()
        db.refresh(db_discussion)
    return db_discussion

def delete_discussion(db: Session, discussion_id: int):
    db_discussion = get_discussion(db, discussion_id)
    if db_discussion:
        db.delete(db_discussion)
        db.commit()
        return True
    return False

def get_discussions_by_hashtag(db: Session, hashtag: str, skip: int = 0, limit: int = 100):
    return db.query(models.Discussion).join(models.Discussion.hashtags).filter(models.Hashtag.name == hashtag).offset(skip).limit(limit).all()

def create_comment(db: Session, comment: schemas.CommentCreate, user_id: int, discussion_id: int):
    db_comment = models.Comment(**comment.dict(), user_id=user_id, discussion_id=discussion_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def get_comments(db: Session, discussion_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Comment).filter(models.Comment.discussion_id == discussion_id).offset(skip).limit(limit).all()

def like_discussion(db: Session, user_id: int, discussion_id: int):
    db_like = models.Like(user_id=user_id, discussion_id=discussion_id)
    db.add(db_like)
    db.commit()
    return db_like

def unlike_discussion(db: Session, user_id: int, discussion_id: int):
    db.query(models.Like).filter(
        models.Like.user_id == user_id,
        models.Like.discussion_id == discussion_id
    ).delete()
    db.commit()

def increment_view_count(db: Session, discussion_id: int):
    db_discussion = db.query(models.Discussion).filter(models.Discussion.id == discussion_id).first()
    if db_discussion:
        db_discussion.view_count += 1
        db.commit()
    return db_discussion

def follow_user(db: Session, follower_id: int, followed_id: int):
    follower = get_user(db, user_id=follower_id)
    followed = get_user(db, user_id=followed_id)
    if follower and followed:
        follower.follow(followed)
        db.commit()
    return follower

def unfollow_user(db: Session, follower_id: int, followed_id: int):
    follower = get_user(db, user_id=follower_id)
    followed = get_user(db, user_id=followed_id)
    if follower and followed:
        follower.unfollow(followed)
        db.commit()
    return follower

def create_comment_reply(db: Session, comment: schemas.CommentCreate, user_id: int, discussion_id: int, parent_id: int):
    db_comment = models.Comment(**comment.dict(), user_id=user_id, discussion_id=discussion_id, parent_id=parent_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def like_comment(db: Session, user_id: int, comment_id: int):
    db_like = models.CommentLike(user_id=user_id, comment_id=comment_id)
    db.add(db_like)
    db.commit()
    return db_like

def unlike_comment(db: Session, user_id: int, comment_id: int):
    db.query(models.CommentLike).filter(
        models.CommentLike.user_id == user_id,
        models.CommentLike.comment_id == comment_id
    ).delete()
    db.commit()

def update_comment(db: Session, comment_id: int, comment_update: schemas.CommentCreate):
    db_comment = get_comment(db, comment_id)
    if db_comment:
        update_data = comment_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_comment, key, value)
        db.commit()
        db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = get_comment(db, comment_id)
    if db_comment:
        db.delete(db_comment)
        db.commit()
        return True
    return False
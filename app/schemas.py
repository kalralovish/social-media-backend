from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    mobile_no: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    discussions: List['Discussion'] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class HashtagBase(BaseModel):
    name: str

class HashtagCreate(HashtagBase):
    pass

class Hashtag(HashtagBase):
    id: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    created_on: datetime
    user_id: int
    discussion_id: int
    parent_id: Optional[int] = None
    replies: List['Comment'] = []
    likes: List['CommentLike'] = []

    class Config:
        from_attributes = True

class DiscussionBase(BaseModel):
    text: str
    image: Optional[str] = None

class DiscussionCreate(DiscussionBase):
    hashtags: List[str] = []

class Discussion(DiscussionBase):
    id: int
    created_on: datetime
    user_id: int
    hashtags: List[Hashtag] = []
    comments: List[Comment] = []
    view_count: int

    class Config:
        from_attributes = True

class LikeBase(BaseModel):
    discussion_id: int

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class CommentLikeBase(BaseModel):
    comment_id: int

class CommentLikeCreate(CommentLikeBase):
    pass

class CommentLike(CommentLikeBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

User.model_rebuild()
Discussion.model_rebuild()
Comment.model_rebuild()
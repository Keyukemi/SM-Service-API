from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime,ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Post (Base):
    __tablename__= "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default = 'TRUE', nullable=False )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    owner = relationship ("User")


class User(Base):
    __tablename__= "users"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Likes (Base): 
    __tablename__= "liked"

    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)


class Messages(Base):
    __tablename__= "messages"
    
    id = Column(Integer, primary_key=True, nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sender = relationship('User', foreign_keys=[sender_id])
    receiver = relationship('User', foreign_keys=[receiver_id])

class Comments(Base):
    __tablename__= "comments"

    id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Friendlist(Base):
    __tablename__= "friendlist"

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    friend_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    status = Column(Enum('pending', 'accepted', 'rejected', name='friend_status_enum'), server_default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship('User', foreign_keys=[user_id])
    friend = relationship('User', foreign_keys=[friend_id])
    
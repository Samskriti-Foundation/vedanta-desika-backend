from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Table
from datetime import datetime, timezone
from .database import Base


user_project_association = Table(
    "user_project_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("role", Enum("OWNER","ADMIN", "MEMBER", name="role"), default="MEMBER", nullable=False),
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    left = Column(Integer, nullable=False)
    right = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
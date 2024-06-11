from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    last_name: str | None
    password: str


class UserOut(UserBase):
    id: int

class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    id: int


class NodeBase(BaseModel):
    name: str
    project_id: int


class NodeCreate(NodeBase):
    parent_id: int


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    id: int
    email: EmailStr
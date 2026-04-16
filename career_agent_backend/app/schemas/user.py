from pydantic import BaseModel
from typing import Optional

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str   # 新增
    role: Optional[str] = "student"
    studentId: Optional[int] = None

class UserResponse(BaseModel):
    username: str
    role: str
    studentId: Optional[int] = None

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    token: Optional[str] = None
    message: Optional[str] = None
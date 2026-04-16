"""
用户认证 API 路由模块

提供用户登录和注册接口，使用 JWT 进行身份验证。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.auth import create_access_token
from app.schemas.user import UserLoginRequest, UserRegisterRequest, LoginResponse
from app.services.auth import authenticate_user, create_user, build_user_response
from pydantic import BaseModel
from app.database import get_db
from app.core.auth import get_password_hash
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    request: UserLoginRequest,
    db: Session = Depends(deps.get_db),
) -> LoginResponse:
    """
    用户登录接口。

    验证用户名和密码，如果成功则返回用户信息和 JWT 访问令牌。

    Args:
        request (UserLoginRequest): 包含 username 和 password 的请求体。
        db (Session): 数据库会话，由依赖注入提供。

    Returns:
        LoginResponse: 包含成功标志、用户信息和 JWT 令牌的响应对象。

    Raises:
        HTTPException: 用户名或密码错误时返回 401 状态码。
    """
    # 调用服务层进行用户认证
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成 JWT 访问令牌（payload 中包含用户名和学生 ID）
    token = create_access_token(data={"sub": user.username, "student_id": user.student_id})

    return LoginResponse(
        success=True,
        user=build_user_response(user),
        token=token,
    )


@router.post("/register", response_model=LoginResponse)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(deps.get_db),
) -> LoginResponse:
    """
    用户注册接口。

    创建新用户账户，并返回用户信息和 JWT 访问令牌。

    Args:
        request (UserRegisterRequest): 包含 username、password、student_id 等信息的请求体。
        db (Session): 数据库会话，由依赖注入提供。

    Returns:
        LoginResponse: 包含成功标志、用户信息和 JWT 令牌的响应对象。

    Raises:
        HTTPException:
            - 400: 用户名已存在或其他业务层错误（ValueError）。
            - 500: 注册失败的其他异常。
    """
    try:
        # 调用服务层创建用户
        user = create_user(db, request)

        # 生成 JWT 访问令牌
        token = create_access_token(data={"sub": user.username, "student_id": user.student_id})

        return LoginResponse(
            success=True,
            user=build_user_response(user),
            token=token,
        )
    except ValueError as e:
        # 业务层抛出的值错误（如用户名已存在）转换为 400
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 其他未预期的错误转换为 500
        raise HTTPException(status_code=500, detail="注册失败")


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(deps.get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="邮箱未注册")
    user.password = get_password_hash(req.new_password)   # 修改这里
    db.commit()
    return {"message": "密码重置成功"}
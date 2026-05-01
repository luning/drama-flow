from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefresh
from app.services import auth_service
from app.services.auth_service import decode_token
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_user(db, data)
    except ValueError as e:
        if str(e) == "EMAIL_EXISTS":
            raise HTTPException(status_code=409, detail="邮箱已被注册")
        raise
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate_user(db, data.email, data.password)
    except ValueError:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    access_token = auth_service.create_token(
        user.id, "access", settings.jwt_access_expire_minutes
    )
    refresh_token = auth_service.create_token(
        user.id, "refresh", settings.jwt_refresh_expire_days * 24 * 60
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: TokenRefresh, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token 无效")

    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = auth_service.create_token(user.id, "access", settings.jwt_access_expire_minutes)
    new_refresh = auth_service.create_token(user.id, "refresh", settings.jwt_refresh_expire_days * 24 * 60)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh, user=user)


@router.post("/logout")
def logout(user=Depends(get_current_user)):
    return {"message": "已登出"}

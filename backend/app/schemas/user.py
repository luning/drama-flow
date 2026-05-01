from pydantic import BaseModel, field_validator, EmailStr
import re


class UserCreate(BaseModel):
    nickname: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少 8 位")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码需包含字母")
        if not re.search(r"\d", v):
            raise ValueError("密码需包含数字")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    nickname: str
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str

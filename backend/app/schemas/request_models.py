from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@mail.com",
                "username": "user",
                "password": "**********",
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "user@mail.com", "password": "**********"}
        }


class PasswordResetRequest(BaseModel):
    email: EmailStr

    class Config:
        json_schema_extra = {"example": {"email": "user@mail.com"}}

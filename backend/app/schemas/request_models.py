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
                "password": "123456"
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "user@mail.com", "password": "123456"}
        }

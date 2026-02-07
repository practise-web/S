from pydantic import BaseModel


class LoginSuccess(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    token_type: str

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "access_token": "**********",
                "expires_in": 3600,
                "refresh_token": "**********",
                "refresh_expires_in": 7200,
                "token_type": "Bearer",
            }
        }


class LoginError(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Example error message during login",
            }
        }


class SignupSuccess(BaseModel):
    message: str
    user_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "User registered successfully",
                "user_id": "**********",
            }
        }


class SignupError(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Example error message during signup",
            }
        }

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
                "message": "Login successful",
                "session_id": "************-****-****-****-************"
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

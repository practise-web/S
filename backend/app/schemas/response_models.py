from pydantic import BaseModel


class LoginSuccess(BaseModel):
    message: str
    session_id: str

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "message": "Login successful",
                "session_id": "************-****-****-****-************",
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

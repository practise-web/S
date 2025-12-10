from pydantic import BaseModel


class ParseRequest(BaseModel):
    path: str

    class Config:
        json_schema_extra = {
            "example": {
                "path": "https://arxiv.org/pdf/2408.09869",
            }
        }

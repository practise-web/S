from pydantic import BaseModel, Field
from typing import List, Optional


class UserInternal(BaseModel):
    sub: str
    email_verified: bool
    name: Optional[str] = None
    username: str = Field(..., alias="preferred_username")
    email: str
    realm_access: dict = {}

    @property
    def roles(self) -> List[str]:
        return self.realm_access.get("roles", [])

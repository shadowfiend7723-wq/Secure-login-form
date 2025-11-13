from pydantic import BaseModel, Field
from typing import Optional

class Users(BaseModel):
    id: Optional[str] = Field(None, alias="_id") 
    username: str
    hashed_password: str

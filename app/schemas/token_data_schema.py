from pydantic import BaseModel, ConfigDict
from typing import Optional

class TokenData(BaseModel):
    username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

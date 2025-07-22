from pydantic import BaseModel
from typing import List, Optional

class AgentRequest(BaseModel):
    tasks: List[str]
    message: Optional[str] = None

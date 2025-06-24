from datetime import datetime
import socket
from typing import Any, Literal
from pydantic import BaseModel

#--------------------------------------------------------
class StatusMessage(BaseModel):
    timestamp: datetime | None = None
    message: str
    method: Literal["GET", "POST", "PUT", "DELETE"]
    hostname: str | None = socket.gethostname()
    request_url: str | None = None

    #-------------
    def model_post_init(self, __context: Any) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now()

#-------------------- 
class ChatItem(BaseModel):
    role: Literal["user", "assistant" ]
    content: str
    thinking: str | None = None
    images: list[str] | None = None
    tool_calls: list[dict] | None = None

#-------------------- 
class FileItem(BaseModel):
    name: str
    size: int
    created: datetime
    modified: datetime
    type: str | None = None

#-------------------- 
class VectorDbPayload(BaseModel):
    text_hash: str
    doc_name: str 
    doc_index: int
    text: str
            
#-------------------- 
class Docs2DbList(BaseModel):
    exclude: list[str] | None = []

#-------------------- 
class VectorSearch(BaseModel):
    query_text: str
    limit: int | None = 3

#-------------------- 

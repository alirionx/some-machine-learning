from datetime import datetime
import socket
from uuid import UUID
from typing import Any, Literal
from pydantic import BaseModel

import settings

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
class LlmList(BaseModel):
    models: list[str] | None = ["mistral", "avr/sfr-embedding-mistral"]
    stream: bool | None = False

class LlmTask(BaseModel):
    id: UUID
    model: str
    completed: int | None = None
    total: int | None = None
    status: str | None = None
    digest: str | None = None

#-------------------- 
class ChatItem(BaseModel):
    role: Literal["user", "assistant" ]
    content: str
    model: str | None = settings.LLMMODEL_DEFAULT_CHAT

    # thinking: str | None = None
    # images: list[str] | None = None
    # tool_calls: list[dict] | None = None

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
class VectorCollection(BaseModel):
    collection_name: str
    vector_size: int | None = 4096

#-------------------- 
class Doc2Collection(BaseModel):
    doc_name: str
    collection_name: str
    model: str | None = settings.LLMMODEL_DEFAULT_EMBED

#-------------------- 
class VectorSearch(BaseModel):
    collection_name: str
    query_text: str
    limit: int | None = 3
    model: str | None = settings.LLMMODEL_DEFAULT_EMBED

#-------------------- 

import os
import json
from uuid import uuid4, UUID
import redis

import settings
from models import ChatItem


class MemoryBackend:
    def __init__(self):
        self.client = None
        self.create_redis_client()
        self.check_memory_backend()
    #----
    def create_redis_client(self):
        self.client = redis.Redis(
            host=settings.MEMORY_REDIS_HOST, 
            port=settings.MEMORY_REDIS_PORT, 
            decode_responses=True)

    #----
    def check_memory_backend(self):
        self.client.ping()

    #---
    def list_task_ids(self) -> list[UUID]:
        res = []
        for key in self.client.scan_iter(f"{settings.MEMORY_REDIS_TASK_SET}:*"):
            try: 
                res.append(UUID(key.split(":")[1]))
            except:
                pass
        return res

    #----
    def write_task_memory_by_id(self, id:UUID, data:dict):
        key = f"{settings.MEMORY_REDIS_TASK_SET}:{str(id)}"
        jdata = json.dumps(data, default=str)
        self.client.set(name=key, value=jdata)
    
    #----
    def get_task_memory_by_id(self, id:UUID) -> dict:
        key = f"{settings.MEMORY_REDIS_TASK_SET}:{str(id)}"
        if not self.client.exists(key):
            return {}
        rq = self.client.get(name=key)
        data = json.loads(rq)
        return data
    
    #----
    def delete_task_memory_by_id(self, id:UUID) -> UUID:
        key = f"{settings.MEMORY_REDIS_TASK_SET}:{str(id)}"
        if not self.client.exists(key):
            raise Exception(f"Entry with key: '{id}' does not exist.")
        self.client.unlink(key)
        return UUID


    #---
    def list_chat_ids(self) -> list[UUID]:
        res = []
        for key in self.client.scan_iter(f"{settings.MEMORY_REDIS_CHAT_SET}:*"):
            try: 
                res.append(UUID(key.split(":")[1]))
            except:
                pass
        return res

    #----
    def write_chat_memory_by_id(self, id:UUID, data:list[ChatItem]):
        key = f"{settings.MEMORY_REDIS_CHAT_SET}:{str(id)}"
        jdata = json.dumps(
            obj=[ item.model_dump() for item in data ],
            default=str
        )
        self.client.set(
            name=key,
            value=jdata
        )

    #----
    def get_chat_memory_by_id(self, id:UUID) -> list[ChatItem]:
        key = f"{settings.MEMORY_REDIS_CHAT_SET}:{str(id)}"
        if not self.client.exists(key):
            return []
        rq = self.client.get(name=key)
        data = json.loads(rq)
        res = [ ChatItem(**item) for item in data ]
        return res

    #----
    def delete_chat_memory_by_id(self, id:UUID) -> UUID:
        key = f"{settings.MEMORY_REDIS_CHAT_SET}:{str(id)}"
        if not self.client.exists(key):
            raise Exception(f"Entry with key: '{id}' does not exist.")
        self.client.unlink(key)
        return UUID
    
    #---
    #---
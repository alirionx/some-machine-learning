import os
import json
from uuid import uuid4, UUID

import settings
from models import ChatItem


class MemoryBackend:
    def __init__(self):
        self.check_memory_backend()
    
    #----
    def check_memory_backend(self):
        if not os.path.isdir(settings.MEMORY_PATH):
            os.makedirs(settings.MEMORY_PATH)
    
    #----
    def list_chat_ids(self) -> list[UUID]:
        res = []
        file_list = os.listdir(settings.MEMORY_PATH) 
        for filename in file_list:
            try: 
                res.append(UUID(filename))
            except:
                pass
        return res

    #----
    def write_chat_memory_by_id(self, id:UUID, data:list[ChatItem]):
        file_path = os.path.join(settings.MEMORY_PATH, str(id))
        with open(file=file_path, mode="w") as fl:
            fl.write(
                json.dumps(
                    obj=[ item.model_dump() for item in data ],
                    indent=2,
                    default=str
                )
            )
    
    #----
    def get_chat_memory_by_id(self, id:UUID) -> list[ChatItem]:
        file_path = os.path.join(settings.MEMORY_PATH, str(id))
        if not os.path.isfile(file_path):
            return []
        with open(file=file_path, mode="r") as fl:
            data = json.loads(fl.read())
        res = [ ChatItem(**item) for item in data ]
        return res

    #----
    def delete_chat_memory_by_id(self, id:UUID) -> UUID:
        file_path = os.path.join(settings.MEMORY_PATH, str(id))
        os.unlink(path=file_path)
        return UUID
    
    #----
   
   
    #----
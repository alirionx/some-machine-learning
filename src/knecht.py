import redis
import settings
from uuid import uuid4

# r = redis.Redis(
#     host=settings.MEMORY_REDIS_HOST, 
#     port=settings.MEMORY_REDIS_PORT, 
#     decode_responses=True)

# r.flushdb()

# for i in range(5):
#     r.set(f"{settings.MEMORY_REDIS_CHAT_HISTORY_SET}:{str(uuid4())}", "palim palim")
    
# for key in r.scan_iter(f"{settings.MEMORY_REDIS_CHAT_HISTORY_SET}:*"):
#     print(key.split(":")[1])

import tools
# res = tools.list_collections()  
# print(res)


# from ollama import Client
# from time import sleep

# client = Client(host="http://localhost:11434")
# progress = client.pull(model="mistral", stream=True)
# for update in progress:
#     print(update)
#     sleep(1)

res = tools.list_llm_models()  
print(res)
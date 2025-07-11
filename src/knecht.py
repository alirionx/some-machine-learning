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

# res = tools.list_llm_models()  
# print(res)

from ollama import Client
from time import sleep

test_model = "mistral:latest"
client = Client(host="http://localhost:11434")

items = client.list()
models = [item.model for item in items.models]
if test_model in models:
    client.delete(model=test_model)


# progress = client.pull(model=test_model, stream=False)
# print(progress.model_dump())

progress = client.pull(model=test_model, stream=True)
for update in progress:
    if update.completed and update.completed == update.total:
        break
    print(update.model_dump())
    sleep(5)



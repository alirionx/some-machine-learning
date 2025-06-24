import redis
import settings
from uuid import uuid4

r = redis.Redis(
    host=settings.MEMORY_REDIS_HOST, 
    port=settings.MEMORY_REDIS_PORT, 
    decode_responses=True)

r.flushdb()

# for i in range(5):
#     r.set(f"{settings.MEMORY_REDIS_CHAT_HISTORY_SET}:{str(uuid4())}", "palim palim")
    
# for key in r.scan_iter(f"{settings.MEMORY_REDIS_CHAT_HISTORY_SET}:*"):
#     print(key.split(":")[1])

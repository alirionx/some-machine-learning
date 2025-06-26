import os

### App config 
API_PORT = int(os.environ.get("API_PORT", "5000"))
APP_MODE = os.environ.get("APP_MODE", "prod")

### Vector DB 
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int((os.environ.get("DB_PORT", "6333")))
DB_COLLECTION = os.environ.get("DB_COLLECTION", "ollama_collection")

### LLM Runtime 
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

### Large Language model 
LLMMODEL_CHAT = os.environ.get("LLMMODEL_CHAT", "mistral")
LLMMODEL_EMBED = os.environ.get("LLMMODEL_EMBED", "avr/sfr-embedding-mistral")
LLMMODEL_CHUNK_SPLITTER = os.environ.get("LLMMODEL_CHUNK_SPLITTER", "---")
LLMMODEL_CHUNK_SIZE = int(os.environ.get("LLMMODEL_CHUNK_SIZE", "250"))

### Content management
CONTENT_BACKEND = os.environ.get("CONTENT_BACKEND", "filesystem") # filesystem or minio
CONTENT_PATH = os.environ.get("CONTENT_PATH", "./data/content") # for filesystem
CONTENT_MINIO_ENDPOINT = os.environ.get("CONTENT_MINIO_ENDPOINT", "localhost:9000") # for minio
CONTENT_MINIO_SECURE = bool(os.environ.get("CONTENT_MINIO_SECURE", "")) # for minio
CONTENT_MINIO_ACCESSKEY = os.environ.get("CONTENT_MINIO_ACCESSKEY", "minio") # for minio
CONTENT_MINIO_SECRETKEY = os.environ.get("CONTENT_MINIO_SECRETKEY", "minio123") # for minio
CONTENT_MINIO_BUCKET = os.environ.get("CONTENT_MINIO_BUCKET", "llm-content") # for minio

### Memory management
MEMORY_BACKEND = os.environ.get("MEMORY_BACKEND", "filesystem") # filesystem or redis
MEMORY_PATH_CHAT = os.environ.get("MEMORY_PATH_CHAT", "./data/memory/chat") # for filesystem
MEMORY_PATH_TASKS = os.environ.get("MEMORY_PATH_TASKS", "./data/memory/tasks") # for filesystem
MEMORY_REDIS_HOST = os.environ.get("MEMORY_REDIS_HOST", "localhost") # for redis
MEMORY_REDIS_PORT = int(os.environ.get("MEMORY_REDIS_PORT", 6379)) # for redis
MEMORY_REDIS_CHAT_SET = os.environ.get("MEMORY_REDIS_CHAT_SET", "chat-history") # for redis
MEMORY_REDIS_TASK_SET = os.environ.get("MEMORY_REDIS_TASK_SET", "background-tasks") # for redis

### Static
CONTENT_ALLOWED_MIMES = ["application/pdf", "text/plain"]
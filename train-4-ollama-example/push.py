import os
from huggingface_hub import HfApi, HfFolder

hf_token = os.environ.get("HF_TOKEN", "GehHeim!")
HfFolder.save_token(hf_token)  

repo_id = "alirionx/mistral-gguf-dq"
source_gguf = "./results/gguf/merged-mistral-dq.gguf"
source_modelfile = "./results/gguf/Modelfile"

api = HfApi()

if not api.repo_exists(repo_id=repo_id, repo_type="model"):
    api.create_repo(repo_id=repo_id, repo_type="model", private=False)

api.upload_file(
    path_or_fileobj=source_gguf,
    path_in_repo="mistral-gguf-dq.gguf",
    repo_id=repo_id,
    repo_type="model"
)
api.upload_file(
    path_or_fileobj=source_modelfile,
    path_in_repo="Modelfile",
    repo_id=repo_id,
    repo_type="model"
)

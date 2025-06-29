### How to Train and publish 4 OLLAMA- Example

__Install aaaaaaaaaalllll the packages (Blackwell - for RTX 5080 (state July 25))__
```
# Order is important !!!!
pip install -r requirements.txt
pip install -r requirements-torch-rtx5080.txt 

```

<br>

__Step-by-step__
```
export HF_TOKEN=<YOUR_HUGGINGFACE_TOKEN>

python fine-tune.py
python merge.py

docker run \
  --rm \
  -v "$PWD/results/merged-mistral-dq":/repo ghcr.io/ggerganov/llama.cpp:full \
  --convert "/repo" \
  --outtype q8_0

mkdir -p ./results/gguf
mv ./results/merged-mistral-dq/Repo-7.2B-Q8_0.gguf ./results/gguf/merged-mistral-dq.gguf
cp Modelfile ./results/gguf/

python push.py

```
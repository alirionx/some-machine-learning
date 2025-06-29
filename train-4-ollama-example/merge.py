from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    torch_dtype=torch.float16,
    device_map="auto"
)

output_dir = "./results/merged-mistral-dq"

merged_model = PeftModel.from_pretrained(base_model, "./results/finetuned-mistral-dq")
merged_model = merged_model.merge_and_unload()

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
tokenizer.pad_token = tokenizer.eos_token

merged_model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)


# docker run --rm -v "$PWD/./merged-mistral-dq":/repo ghcr.io/ggerganov/llama.cpp:full --convert "/repo" --outtype q8_0


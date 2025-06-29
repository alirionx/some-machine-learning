from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

model_path = "./results/mistral-finetuned-dq"
tokenizer = AutoTokenizer.from_pretrained(model_path, legacy=False, use_fast=False)
tokenizer.pad_token = tokenizer.eos_token

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=False,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    quantization_config=bnb_config,
    offload_folder="./offload",
    trust_remote_code=True
)
model.eval()

# prompt = "Based on the profile of Daniel Quilitzsch from Korb, Germany, please answer: Summarize Daniel Quilitzsch's professional experience in three sentences."
# prompt = "Based on the profile of Daniel Quilitzsch from Korb, Germany, please answer: What programming languages does Daniel know?"
# prompt = "Summarize Daniel Quilitzsch's professional experience in three sentences."
prompt = "What programming languages does Daniel Quilitzsch know?"
# prompt = "Did Daniel Quilitzsch work for MHP?"
# prompt = "to which country does Germany belong to?"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=120,
        do_sample=False,
        # temperature=0.7,
        # top_p=0.9
    )

print(tokenizer.decode(output[0], skip_special_tokens=True))
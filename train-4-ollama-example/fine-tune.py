import os
import json
from datasets import load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    BitsAndBytesConfig,
    Trainer
)
from peft import get_peft_model, LoraConfig, TaskType, prepare_model_for_kbit_training
import torch

#-LLM Hub Access------------------------------------------
from huggingface_hub import login
hf_token = os.environ.get("HF_TOKEN", "GehHeim!")
login(hf_token) 


#-Preparation---------------------------------------------
base_model = "mistralai/Mistral-7B-v0.1"
tuned_model = "finetuned-mistral-dq"

tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token


dataset = load_dataset("json", data_files="cv_data.jsonl", split="train")
def tokenize(example):
    prompt = f"### Input:\n{example['input']}\n\n### Output:\n{example['output']}"
    tokenized = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized
tokenized_dataset = dataset.map(tokenize)


#-Training Config-----------------------------------------
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    # bnb_4bit_use_double_quant=True,
    bnb_4bit_use_double_quant=False,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_config, 
    device_map="auto",
    trust_remote_code=True
)

peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    # r=8,
    r=64,
    lora_alpha=16,
    lora_dropout=0.1,
    bias="none"
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, peft_config)
model.config.use_cache = False
model.gradient_checkpointing_enable()

training_args = TrainingArguments(
    output_dir=f"./results/{tuned_model}",
    num_train_epochs=5,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    optim="adamw_8bit",
    save_steps=25,
    logging_steps=25,
    learning_rate=2e-4,
    weight_decay=0.01,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    max_grad_norm=0.3,
    max_steps=-1,
    warmup_steps=10,
    warmup_ratio=0.03,
    group_by_length=True,
    lr_scheduler_type="linear",
    seed=3407,
    save_strategy="epoch",
    save_total_limit=2,
    dataloader_pin_memory=False,
    remove_unused_columns=False,
    label_names=["labels"],
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)

trainer.train()

model.save_pretrained(f"./results/{tuned_model}")
tokenizer.save_pretrained(f"./results/{tuned_model}")
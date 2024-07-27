import fire, os
import torch
import datasets
from trl import DataCollatorForCompletionOnlyLM
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from unsloth.unsloth import FastLanguageModel
import wandb

# Reference to this practical tips: https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms
# https://lightning.ai/pages/community/lora-insights/

def load_model(model_name_or_path, max_seq_length):
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        use_fast=True,
        padding_side='right'
    )
    try:
        local_rank = os.environ["LOCAL_RANK"]
    except:
        local_rank = 0
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name_or_path,
        max_seq_length=max_seq_length,
        dtype=None,
        device_map=f"cuda:{local_rank}",
        load_in_4bit=True,
        use_cache=False,
    )
    
    model = FastLanguageModel.get_peft_model(
        model,
        r=32, 
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=64,
        lora_dropout=0, # Supports any, but = 0 is optimized
        bias="none",    # Supports any, but = "none" is optimized
        use_gradient_checkpointing=True,
        random_state=3407,
        use_rslora=False,  # We support rank stabilized LoRA
        loftq_config=None, # And LoftQ,
        modules_to_save= ["embed_tokens", "lm_head"],
    )

     #Typing weight
    model.lm_head.modules_to_save.default.weight  = model.base_model.model.model.embed_tokens.modules_to_save.default.weight 
        
    return tokenizer, model

def load_dataset(tokenizer: AutoTokenizer, dataset_name_or_path: str, max_seq_length: int):

    def convert_conversation_to_input(examples):
        input_ids = []
        for quote, topic in zip(examples["quote"], examples["topic"]):
            example = {"quote": quote, "topic": topic}
            input_id = tokenizer.apply_chat_template(example, tokenize=True)[: max_seq_length]
            input_ids.append(input_id)
        return {"input_ids": input_ids}
    
    dataset = datasets.load_dataset(dataset_name_or_path, split='train[:]')
    dataset = dataset.map(convert_conversation_to_input, remove_columns=list(dataset.features), batched=True)
    
    dataset = dataset.train_test_split(test_size=2876, shuffle=True)
    return dataset['train'], dataset['test']


def train(
    model_name_or_path: str = '../gemma-2b',
    train_batch_size: int = 4,
    max_seq_length: int = 8192,
):
    dataset_name = 'dinhlnd1610/Vietnamese_Quote_Dataset_100K'
    output_dir = "../unsloth-lora-checkpoints"
    
    # Load model and tokenizer
    tokenizer, model = load_model(model_name_or_path, max_seq_length)
    
    # Load dataset
    train_dataset, eval_dataset = load_dataset(tokenizer=tokenizer, dataset_name_or_path=dataset_name, max_seq_length=max_seq_length)
    collator = DataCollatorForCompletionOnlyLM(
        instruction_template="<bos>",
        response_template="<sep>",
        tokenizer=tokenizer,
        mlm=False,
    )
    run = wandb.init(project='mle-m1', job_type="training", name = "unsloth-lora-14-7" )

    # Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size = train_batch_size,
        bf16=True,
        eval_strategy = "steps",
        learning_rate=2e-5,
        optim="adamw_8bit",
        lr_scheduler_type='cosine',
        warmup_ratio=0.1,
        logging_steps=5,
        eval_steps= 500,
        save_steps=500,
        save_total_limit=3,
        num_train_epochs=3,
        group_by_length=True,
        ddp_find_unused_parameters=False,
        report_to = "wandb",
        load_best_model_at_end= True,
        gradient_accumulation_steps = 1
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=collator,
    )
    trainer.train()
    
    if trainer.is_fsdp_enabled:
        trainer.accelerator.state.fsdp_plugin.set_state_dict_type("FULL_STATE_DICT")

    trainer.save_model("../trainer_model")

if __name__ == "__main__":
    # fire.Fire(train)
    fire.Fire(train)

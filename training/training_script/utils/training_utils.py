import os

import fire
import numpy as np
import torch
from tokenizers import AddedToken
from transformers import AutoModelForCausalLM, AutoTokenizer


def download_model(model_name_or_path, output_dir):
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path, use_fast=True, token=os.environ.get("hf_token")
    )
    tokenizer.add_tokens([AddedToken("<sep>")])
    tokenizer.chat_template = "{{ '<bos>' + messages['topic'] + '<sep>' + messages['quote'] }}{% if messages['quote'] != '' %}{{ '<eos>' }}{% endif %}"
    tokenizer.save_pretrained(output_dir)

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path, torch_dtype=torch.bfloat16, token=os.environ.get("hf_token")
    )
    model.resize_token_embeddings(len(tokenizer))
    model.save_pretrained(output_dir)

    print(f"Model and tokenizer are saved to {output_dir}")


def merge_lora(
    base_model_path: str = "../../gemma-2b",
    lora_path: str = "../../unsloth-lora-checkpoints/checkpoint-82500",
    output_path: str = "../../gemma-2b-quote-generator",
):

    from peft import PeftModel

    base = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch.bfloat16,
    )
    lora_model = PeftModel.from_pretrained(base, lora_path)
    model = lora_model.merge_and_unload()
    model.save_pretrained(output_path)
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
    tokenizer.save_pretrained(output_path)


def test_chat_template():
    tokenizer = AutoTokenizer.from_pretrained("../../gemma-2b")
    conversation = {
        "quote": "Tôi luôn cho rằng thay đổi chỉ trở nên căng thẳng và quá sức chịu đựng khi bạn đánh mất cảm giác về sự kiên định trong cuộc sống của mình. Bạn cần một nền đất vững chắc để đứng lên. Từ đó, bạn có thể đối phó với sự thay đổi đó.",
        "topic": "Life and Insprirational",
    }
    text = tokenizer.apply_chat_template(conversation, tokenize=False)
    ids = tokenizer.apply_chat_template(conversation, return_tensors="pt")
    print(ids)
    print(text)


if __name__ == "__main__":
    fire.Fire()

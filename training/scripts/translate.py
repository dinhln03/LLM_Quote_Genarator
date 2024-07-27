from training.scripts.utils.translation_utils import translate_and_save_data
from datasets import load_dataset
import google.generativeai as genai
import os
import fire

def main(data_path, sample_length,start_batch, end_batch, num_thread):
    genai.configure(api_key=os.environ.get("gg_key"))

    model = genai.GenerativeModel('gemini-1.5-pro')

    quote_dataset = load_dataset("csv", data_files=data_path, delimiter=",")

    quote_sample = quote_dataset["train"].shuffle(seed=42).select(range(sample_length))

    translate_and_save_data(model, start_batch, end_batch, quote_sample,num_thread)

if __name__ == "__main__":
    fire.Fire(main)







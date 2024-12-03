import os

import fire
import google.generativeai as genai
from datasets import load_dataset
from translator import QuoteTranslator  # Import the QuoteTranslator class


def main(data_path, sample_length, start_batch, end_batch, num_thread):
    """
    Run the translation process for the quotes dataset.
    Args:
        data_path: str, path to the English dataset file.
        sample_length: int, number of samples to translate.
        start_batch: int, the starting batch index.
        end_batch: int, the ending batch index.
        num_thread: int, number of threads to use.
    Note: 1 batch = 5 quotes.
    """

    # Configure the Generative AI API with the key from the environment variable
    genai.configure(api_key=os.environ.get("gg_key"))

    # Initialize the Generative Model
    model = genai.GenerativeModel("gemini-1.5-pro")

    # Load the dataset
    quote_dataset = load_dataset("csv", data_files=data_path, delimiter=",")

    # Shuffle and select a sample of the dataset
    quote_sample = quote_dataset["train"].shuffle(seed=42).select(range(sample_length))

    # Create an instance of QuoteTranslator and call translate_and_save_data
    translator = QuoteTranslator(model)  # Create an instance of QuoteTranslator
    translator.translate_and_save_data(start_batch, end_batch, quote_sample, num_thread)


if __name__ == "__main__":
    fire.Fire(main)

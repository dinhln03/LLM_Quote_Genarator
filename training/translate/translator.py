import concurrent.futures
import json
import re
import time

import google.generativeai as genai
from constant import Constant
from google.api_core.exceptions import ResourceExhausted
from loguru import logger


class QuoteTranslator:
    def __init__(self, model, log_file="logs/quote_translated.log"):
        self.model = model
        self.safe = Constant.safe
        self.topic = Constant.topic
        self.prompt_template = Constant.prompt_template
        self.logger_id = logger.add(log_file)

    def get_quote(self, quotes, suggest_topics, batch_index):
        """
        *Get the model's generation response

        *Parameters:
        - quotes: a list of quotes
        - suggest_topics: a list of suggested topics
        - batch_index: the index of the batch
        """
        prompt = self.prompt_template.format(
            TOPIC_LIST=self.topic,
            QUOTE_LIST=[
                {"original_quote": x, "suggested_topic": y}
                for x, y in zip(quotes, suggest_topics)
            ],
        )
        print(prompt, batch_index)
        start_time = time.time()

        while True:
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=0.6),
                    safety_settings=self.safe,
                )
                return response.text
            except ResourceExhausted:
                logger.error(
                    f"Batch {batch_index}: Resource exhausted. Retrying in 5s..."
                )
                time.sleep(5)
            except Exception as e:
                logger.error(f"Batch {batch_index} Error: {e}")
                return None

            if time.time() - start_time >= 300:  # Timeout after 5 minutes
                logger.critical(f"Batch {batch_index}: Timeout")
                return None

    def process_batch(self, batch_quote, batch_index):
        """
        *Process a batch of quotes. Calls get_quote and parses the response to JSON.
        Retries on error. Skips the batch after 2 retries.

        *Parameters:
        - batch_quote: a list of quotes in the batch
        - batch_index: the index of the batch
        """

        logger.info(f"Start batch {batch_index}...")

        response = self.get_quote(
            batch_quote["quote"], batch_quote["category"], batch_index
        )
        if response:
            try:
                response = re.findall(r"\[.*\]", response)[0]
                json_response = json.loads(response)
                logger.success(f"Batch {batch_index} done.")
                return json_response
            except:
                logger.error(
                    f"Batch {batch_index}: Error in parsing response. Retrying..."
                )
                response = self.retry_batch(batch_quote, batch_index)
                return response
        else:
            logger.critical(f"Cannot process anymore. Skipping batch {batch_index}...")
            return []

    def retry_batch(self, batch_quote, batch_index):
        """Retry fetching and parsing the batch response."""
        logger.error(f"Batch {batch_index}: Retrying...")
        response = self.get_quote(
            batch_quote["quote"], batch_quote["category"], batch_index
        )

        if response:
            try:
                response = re.findall(r"\[.*\]", response)[0]
                json_response = json.loads(response)
                logger.success(f"Batch {batch_index} retry successful.")
                return json_response
            except:
                logger.critical(f"Batch {batch_index}: Error response (skipping).")
        logger.critical(f"Batch {batch_index}: Skipping.")
        return []

    def translate_and_save_data(
        self, start_point, end_point, quote_sample, num_threads
    ):
        """
        *Translate quotes and save the results to JSON.
        Processes quotes in batches with multi-threading and saves the results.

        *Parameters:
        - start_point: the start index of the batch
        - end_point: the end index of the batch
        - quote_sample: a list of quotes
        - num_threads: the number of threads to use
        """
        total_batches = end_point - start_point + 1
        batch_size = 5

        assert num_threads > 0, "Number of threads must be greater than 0."
        assert start_point < end_point, "Start point must be less than end point."
        assert total_batches * 5 <= len(
            quote_sample
        ), "Length of quote sample must be greater than the number of batches."
        assert (
            num_threads <= total_batches
        ), "Number of threads must be less than the number of batches."

        logger.info(
            "Start translating quotes in multi-threading mode with batch size 5..."
        )

        if total_batches % num_threads != 0:
            left_batches = total_batches % num_threads
            end_point -= left_batches
            logger.warning(
                f"Reseting end point to {end_point} to make the number of batches divisible by the number of threads."
            )

        for i in range(start_point, end_point + 1, num_threads):

            logger.info(
                f"Processing batch {i}-->{i+num_threads-1} in multi-threading..."
            )
            with concurrent.futures.ThreadPoolExecutor() as executor:
                responses = executor.map(
                    self.process_batch,
                    [
                        quote_sample[(i + j) * batch_size : ((i + j) + 1) * batch_size]
                        for j in range(num_threads)
                    ],
                    [i + j for j in range(num_threads)],
                )

            results = [response for response in responses if response]

            self.save_results(i, num_threads, results)
            time.sleep(5)

    def save_results(self, start_index, num_threads, results):
        """Save the batch results to a JSON file."""
        logger.info(f"Saving batch {start_index}-->{start_index+num_threads-1}...")
        with open(
            f"data/translated_quote_batch_{start_index}_{start_index+num_threads-1}.json",
            "w",
        ) as f:
            json.dump(results, f, indent=2)
        logger.success(
            f"Batch {start_index}-->{start_index+num_threads-1} saved successfully."
        )

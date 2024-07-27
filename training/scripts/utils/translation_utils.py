import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import time 
from loguru import logger
import re
import json
import concurrent.futures

def get_quote(model, quotes, suggest_topics, i ):

    safe = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
    
    topic = ["Life and Inspiration: (Includes broader themes of life lessons, inspiration, courage, and personal growth.)",
          "Love and Relationships (Covers themes like love, romance, heartbreak, marriage, and relationships.)",
          "Friendship: (Covers themes like friend, companionship, loyalty, trust, mutual support, and shared experiences.))",
          "Spirituality and Faith: (Includes themes of faith, hope, spiritual growth, and introspection.)",
          "Humor and Light-heartedness: (Covers themes of humor, wit, light-hearted moments, and laughter.)",
          ]

                                        
    prompt_template = f"""
    You are a language model capable of translating quotes from English to Vietnamese that are meaningful and inspirational.

    
    Perform the following actions:
    Step 1 - 1 - Proofread and correct the original quote, paying special attention to punctuation, and rewrite the corrected version of the original quote. Ensure all necessary punctuation marks are correctly placed. If you don't find any errors, just go ahead to step 2.
    Step 2 - Based on the suggested topic below, determine whether each item in the following list of topics is a topic in the original quote. List of topics: {", ".join(topic)}
    Step 3 - Translate the original quote into Vietnamese.
    Step 4 - Proofread and rewrite the corrected version of the translated Vietnamese quote, including punctuation. If you don't find any errors, just go ahead.

    Finally, return the result as a JSON object in the exact format shown below (on a single line without line breaks):
    {{ "topic": "Life and Inspiration", "quote": "Làm việc chăm chỉ là chìa khóa để thành công." }}

    Important notes:
    - If the quote is related to topics like love, inspiration, life, or motivation, translate it in a thoughtful and meaningful manner.
    - If the meaning of the quote is humorous, translate it in a way that maintains its humor and makes people laugh.
    - Do not add any extra characters, explanations, formatting, or line breaks. The result should be returned in the exact same format as the example above on a single line.
    - The suggested topic is not always true, so you should keep this as a reference and prioritize determining the topic based on the meaning of the quote itself.
    - If the determined topic is not in the list of topics, return the topic as None.
    -- **Ensure that all punctuation marks in the quote are correct and appropriately placed. Correct any punctuation errors before proceeding.**

    For each of the following 5 quotes, perform the steps described above and return a list of dictionaries:

    {[{'original_quote': x, 'suggested_topic': y} for x, y in zip(quotes, suggest_topics)]}
    
    """
    start_time = time.time()

    while True:
        
        try:
            response = model.generate_content(prompt_template, 
                                    generation_config=genai.types.GenerationConfig(temperature=0.6),
                                    safety_settings=safe
            )
            return response.text
        except ResourceExhausted:
            logger.error(f"Batch {i}: Resource exhausted. Retrying in 5s...")
            time.sleep(5)
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= 300:
            logger.critical(f"Batch {i}: Timeout")
            return None

def process_batch(model, batch_quote, i):

    logger.info(f"Start batch {i}...")

    response = get_quote(model, batch_quote["quote"], batch_quote["category"], i)

    if response:

        try:
            response = re.findall(r'\[.*\]', response)[0]

            json_response = json.loads(response)

            logger.success(f"Batch {i} done.")

            return json_response

        except:
            logger.error(f"Batch {i}: Error in parsing response. Retrying...")

            logger.error(f"Batch {i}: Error response (retrying): {response}")

            response = get_quote(model, batch_quote["quote"], batch_quote["category"], i)

            
            try:
                response = re.findall(r'\[.*\]', response)[0]

                json_response = json.loads(response)

                logger.success(f"Batch {i} done.")

                return json_response

            except:

                logger.critical("Batch {i}: Error response (skipping): {response}")

                logger.critical(f"Batch {i}: Error in parsing response. Skip batch {i}.")
                json_response = []

                return json_response


    else:
        logger.critical(f"Can not process anymore. Skip batch {i}...")
        return []


def translate_and_save_data(model, start_point, end_ponint, quote_sample, num_thread):
    k =logger.add("../logs/quote_translated.log")
    batch_size = 5
    results = []
    logger.info("Start translating quotes with batch size is 5 in multi-threading mode...".upper())

    for i in range(start_point, end_ponint, num_thread):

        logger.info(f"Start batch {i}-->{i+num_thread} in multi-threading...")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            responses = executor.map(process_batch, [model] *num_thread,[quote_sample[(i+j)*batch_size:((i+j)+1)*batch_size] for j in range(num_thread)], [i+j for j in range(num_thread)])
        for response in responses:
            results.extend(response)

        logger.info(f"Saving batch {i}-->{i+num_thread}...")
        with open(f"../data/translated_quote_batch_{i}_{i+num_thread}.json", "w") as f:
            json.dump(results, f, indent=2)
        results= []
        logger.success(f"Done saving translated batch {i}_{i+num_thread}.")
        logger.success(f"Batch {i}-->{i+num_thread} done.")
        time.sleep(5)
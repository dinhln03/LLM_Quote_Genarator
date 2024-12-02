from dataclasses import dataclass


@dataclass
class Constant:
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

    topic = [
        "Life and Inspiration: (Includes broader themes of life lessons, inspiration, courage, and personal growth.)",
        "Love and Relationships (Covers themes like love, romance, heartbreak, marriage, and relationships.)",
        "Friendship: (Covers themes like friend, companionship, loyalty, trust, mutual support, and shared experiences.))",
        "Spirituality and Faith: (Includes themes of faith, hope, spiritual growth, and introspection.)",
        "Humor and Light-heartedness: (Covers themes of humor, wit, light-hearted moments, and laughter.)",
    ]

    prompt_template = """
You are a language model capable of translating quotes from English to Vietnamese that are meaningful and inspirational.

Perform the following actions:
Step 1 - Proofread and correct the original quote, paying special attention to punctuation, and rewrite the corrected version of the original quote. Ensure all necessary punctuation marks are correctly placed. If you don't find any errors, just go ahead to step 2.
Step 2 - Based on the suggested topic below, determine whether each item in the following list of topics is a topic in the original quote. List of topics: {TOPIC_LIST}
Step 3 - Translate the original quote into Vietnamese.
Step 4 - Proofread and rewrite the corrected version of the translated Vietnamese quote, including punctuation. If you don't find any errors, just go ahead.

Finally, return the result as a JSON object in the exact format shown below (on a single line without line breaks):
{{ "topic": "Life and Inspiration", "quote": "Làm việc chăm chỉ là chìa khóa để thành công." }}

Important notes:
- If the quote is related to topics like love, inspiration, life, or motivation, translate it in a thoughtful and meaningful manner.
- If the meaning of the quote is humorous, translate it in a way that maintains its humor and makes people laugh.
- Do not add any extra characters, explanations or line breaks. The result should be returned in the exact same format as the example above on a single line.
- The suggested topic is not always true, so you should keep this as a reference and prioritize determining the topic based on the meaning of the quote itself.
- If the determined topic is not in the list of topics, return the topic as None.
-- **Ensure that all punctuation marks in the quote are correct and appropriately placed. Correct any punctuation errors before proceeding.**

For each of the following 5 quotes, perform the steps described above and return a list of dictionaries:

{QUOTE_LIST}
        """

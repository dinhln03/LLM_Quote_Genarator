import asyncio
import time

from openai import OpenAI

from constants import config

try:
    endpoint_id = config.RUNPOD_ENDPOINT_ID
    api_key = config.RUNPOD_API_KEY
    hf_model_name = config.HF_MODEL_NAME
except KeyError as e:
    raise RuntimeError(f"Missing required variable: {e}")


async def get_conversation(text):

    client = OpenAI(
        base_url=f"https://api.runpod.ai/v2/{endpoint_id}/openai/v1",
        api_key=api_key,
    )
    stream = False

    completion = await asyncio.to_thread(
        client.completions.create,
        model=hf_model_name,
        prompt=[text],
        max_tokens=256,
        temperature=0.7,
        top_p=0.9,
        n=1,  # Number of completions to generate
        stream=stream,
    )

    return completion.choices[0].text.strip()


# result = asyncio.run(get_conversation("<bos>Truyền cảm hứng<sep>Ngày"))
# print(result)

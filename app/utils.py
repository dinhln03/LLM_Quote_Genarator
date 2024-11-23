import asyncio
import os
import time

from openai import OpenAI

try:
    endpoint_id = os.environ["RUNPOD_ENDPOINT_ID"]
    api_key = os.environ["RUNPOD_API_KEY"]
    hf_model_name = os.environ["HF_MODEL_NAME"]
except KeyError as e:
    raise RuntimeError(f"Missing required environment variable: {e}")


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

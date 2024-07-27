from openai import OpenAI
import os
import time
import asyncio

endpoint_id = "vllm-w9uf0ka28xb83b"
api_key = "4DGNCD80IJDLP0IN7Y9L4UN26DTWB8GRX0X2G4E1"

async def get_conversation(text):
    client = OpenAI(
        base_url=f"https://api.runpod.ai/v2/{endpoint_id}/openai/v1",
        api_key=api_key,
    )
    stream = False

    completion = await asyncio.to_thread(client.completions.create,
        model="dinhlnd1610/ahihi",
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
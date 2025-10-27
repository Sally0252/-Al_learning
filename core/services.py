# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI


DEEPSEEK_API_KEY = "sk-93136fac2ac64703afa79f454c04ba8f"
DEEPSEEK_API_URL = "https://api.deepseek.com"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)


def get_deepseek_response(messages):

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    return response.choices[0].message.content


# messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ]

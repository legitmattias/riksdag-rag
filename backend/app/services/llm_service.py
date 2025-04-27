# /services/llm_service.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai_chat(prompt: str) -> str:
    """Call GPT-3.5-turbo to generate answer."""
    print("[OpenAI] Sending prompt to GPT-3.5-turbo...")
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant specializing in summarizing Swedish parliamentary speeches."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

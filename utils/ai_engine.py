from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("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"))
client = Groq(
    api_key=os.getenv("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")
)

def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
)

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {e}"
"""Supplied reply functions. Local mode needs no account or network."""
import os


def local_reply(messages):
    turns = sum(message["role"] == "user" for message in messages)
    return f"Local reply {turns}: you said {messages[-1]['content']}"


def live_reply_function():
    from dotenv import load_dotenv
    from groq import Groq
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("Live mode needs GROQ_API_KEY in .env. Use python app.py for local mode.")
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    def reply(messages):
        result = client.chat.completions.create(model=model, messages=messages)
        return result.choices[0].message.content

    return reply

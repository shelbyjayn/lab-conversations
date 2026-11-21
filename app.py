"""Supplied API and browser. Run python app.py, or python app.py --live."""
import argparse
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import uvicorn
import database
from replies import local_reply, live_reply_function


class NewConversation(BaseModel):
    title: str = Field(min_length=1)


class NewMessage(BaseModel):
    content: str = Field(min_length=1)


def create_app(path="conversations.db", reply=local_reply):
    database.init_db(path)
    app = FastAPI()

    @app.get("/")
    def home():
        return FileResponse(Path(__file__).with_name("index.html"))

    @app.get("/conversations")
    def conversations():
        return database.list_conversations(path)

    @app.post("/conversations")
    def new_conversation(data: NewConversation):
        return {"id": database.create_conversation(path, data.title)}

    @app.get("/conversations/{conversation_id}/messages")
    def messages(conversation_id: int):
        return database.get_messages(path, conversation_id)

    @app.post("/conversations/{conversation_id}/messages")
    def send(conversation_id: int, data: NewMessage):
        if not any(row["id"] == conversation_id for row in database.list_conversations(path)):
            raise HTTPException(404, "Conversation not found")
        database.add_message(path, conversation_id, "user", data.content)
        history = database.get_messages(path, conversation_id)
        request = [{"role": row["role"], "content": row["content"]} for row in history]
        try:
            answer = reply(request)
        except Exception as error:
            raise HTTPException(502, "The reply service failed. Your message is saved; check your key or use local mode.") from error
        database.add_message(path, conversation_id, "assistant", answer)
        return database.get_messages(path, conversation_id)

    @app.get("/search")
    def search(q: str = ""):
        return database.search_messages(path, q)

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Use Groq instead of local replies")
    args = parser.parse_args()
    try:
        reply = live_reply_function() if args.live else local_reply
    except ValueError as error:
        parser.error(str(error))
    mode = "live Groq replies" if args.live else "local replies (no API key needed)"
    print(f"Using {mode}. Open http://127.0.0.1:8000")
    uvicorn.run(create_app(reply=reply), host="127.0.0.1", port=8000)

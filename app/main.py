from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import requests
from dotenv import load_dotenv
from company_data import COMPANY_DATA

load_dotenv()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/chat")
@limiter.limit("10/minute")
def chat(request: Request, body: ChatRequest):
    system_prompt = (
        "Du är en hjälpsam kundtjänstassistent för Städfirma AB. "
        "Du MÅSTE alltid svara på svenska oavsett vilket språk användaren skriver på. "
        "Svara ALDRIG på engelska, ryska eller något annat språk än svenska. "
        "Använd endast informationen nedan för att svara.\n\n"
    )
    for item in COMPANY_DATA:
        system_prompt += f"F: {item['question']}\nS: {item['answer']}\n\n"

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
            json={
                "model": os.getenv("OPENROUTER_MODEL"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *body.history,
                    {"role": "user", "content": body.message},
                ],
            },
            timeout=15,
        )

        data = response.json()

        if "error" in data:
            return {"response": "AI är just nu otillgänglig, försök igen senare."}

        return {"response": data["choices"][0]["message"]["content"]}

    except Exception as e:
        print("EXCEPTION:", e)
        return {"response": "Något gick fel, försök igen."}

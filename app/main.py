from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_TENANTS_DIR = os.path.join(os.path.dirname(__file__), 'tenants')
DEFAULT_TENANT = "stadfirma"

def load_tenant_data(tenant_name):
    """Load tenant configuration and data from JSON files."""
    tenant_dir = os.path.join(BASE_TENANTS_DIR, tenant_name)
    
    if not os.path.exists(tenant_dir):
        tenant_dir = os.path.join(BASE_TENANTS_DIR, DEFAULT_TENANT)
        tenant_name = DEFAULT_TENANT
    
    with open(os.path.join(tenant_dir, 'data.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(os.path.join(tenant_dir, 'config.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return data, config, tenant_dir

def get_tenant_from_request(request: Request):
    """Extract tenant from subdomain."""
    host = request.headers.get('Host', '')
    # "stadfirma.meetopia.tech" → "stadfirma"
    subdomain = host.split(".")[0]
    return subdomain

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


MAX_HISTORY = 10


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/widget.js")
def widget():
    """Serve the embeddable widget script."""
    return FileResponse("static/widget.js", media_type="application/javascript")


@app.get("/config")
def get_config(request: Request):
    tenant = get_tenant_from_request(request)
    _, config, _ = load_tenant_data(tenant)
    return config


@app.get("/logo")
def get_logo(request: Request):
    tenant = get_tenant_from_request(request)
    _, _, tenant_dir = load_tenant_data(tenant)
    logo_path = os.path.join(tenant_dir, "logo.png")
    
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    return {"error": "Logo not found"}, 404


@app.post("/chat")
@limiter.limit("10/minute")
def chat(request: Request, body: ChatRequest):
    tenant = get_tenant_from_request(request)
    company_data, company_config, _ = load_tenant_data(tenant)
    
    trimmed_history = body.history[-MAX_HISTORY:]

    system_prompt = (
        f"Du är en hjälpsam kundtjänstassistent för {company_config['company_name']}. "
        "Du MÅSTE alltid svara på svenska oavsett vilket språk användaren skriver på. "
        "Svara ALDRIG på engelska, ryska eller något annat språk än svenska. "
        "Använd endast informationen nedan för att svara.\n\n"
    )
    for item in company_data:
        system_prompt += f"F: {item['question']}\nS: {item['answer']}\n\n"

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
            json={
                "model": os.getenv("OPENROUTER_MODEL"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *trimmed_history,
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

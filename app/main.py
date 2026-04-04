import html as html_module
import json
import os

import httpx
import resend
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

BASE_TENANTS_DIR = os.path.join(os.path.dirname(__file__), "tenants")
DEFAULT_TENANT = "stadfirma"


def load_tenant_data(tenant_name):
    """Load tenant configuration and data from JSON files."""
    tenant_dir = os.path.join(BASE_TENANTS_DIR, tenant_name)

    if not os.path.exists(tenant_dir):
        tenant_dir = os.path.join(BASE_TENANTS_DIR, DEFAULT_TENANT)
        tenant_name = DEFAULT_TENANT

    with open(os.path.join(tenant_dir, "data.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(tenant_dir, "config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)

    return data, config, tenant_dir


def get_tenant_from_request(request: Request):
    """Extract tenant from subdomain and validate against existing folders."""
    host = request.headers.get("Host", "")
    # "comp1.aloitus.se" → "comp1"
    subdomain = host.split(".")[0]

    # Validate that the subdomain is an actual tenant folder
    tenant_dir = os.path.join(BASE_TENANTS_DIR, subdomain)
    if not os.path.isdir(tenant_dir):
        subdomain = DEFAULT_TENANT

    return subdomain


limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://*.aloitus.se", "https://aloitus.se"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str
    history: list = []


class ContactRequest(BaseModel):
    name: str
    email: str
    message: str


MAX_HISTORY = 10


@app.get("/")
def root(request: Request):
    host = request.headers.get("Host", "")
    subdomain = host.split(".")[0]
    if subdomain in ["aloitus", "www", ""]:
        return FileResponse("static/landing.html")
    return FileResponse("static/index.html")


@app.get("/robots.txt")
def robots_txt():
    """Serve robots.txt for SEO crawlers."""
    return FileResponse("static/robots.txt", media_type="text/plain")


@app.get("/sitemap.xml")
def sitemap_xml():
    """Serve sitemap.xml for SEO."""
    return FileResponse("static/sitemap.xml", media_type="application/xml")


@app.get("/chat-ui")
def chat_ui():
    return FileResponse("static/index.html")


@app.get("/embed")
def embed():
    return FileResponse("static/embed.html")


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
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest):
    tenant = get_tenant_from_request(request)
    company_data, company_config, _ = load_tenant_data(tenant)

    if len(body.message) > 2000:
        return {"response": "Meddelandet är för långt."}

    trimmed_history = [
        msg for msg in body.history[-MAX_HISTORY:]
        if isinstance(msg, dict) and msg.get("role") in ("user", "assistant")
    ]

    system_prompt = (
        f"Du är en hjälpsam kundtjänstassistent för {company_config['company_name']}. "
        "Du MÅSTE alltid svara på svenska oavsett vilket språk användaren skriver på. "
        "Svara ALDRIG på engelska, ryska eller något annat språk än svenska. "
        "Använd endast informationen nedan för att svara.\n\n"
    )
    for item in company_data:
        system_prompt += f"F: {item['question']}\nS: {item['answer']}\n\n"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
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


@app.post("/contact")
@limiter.limit("5/minute")
async def contact(request: Request, body: ContactRequest):
    if not body.name or len(body.name) > 100:
        return {"error": "Ogiltigt namn"}
    if not body.email or "@" not in body.email or len(body.email) > 200:
        return {"error": "Ogiltig e-post"}
    if not body.message or len(body.message) > 5000:
        return {"error": "Ogiltigt meddelande"}

    try:
        resend.Emails.send(
            {
                "from": "Aloitus <kontakt@aloitus.se>",
                "to": ["famo1901@gmail.com"],
                "reply_to": body.email,
                "subject": f"Ny förfrågan från {body.name}",
                "html": f"""
                <h2>Ny förfrågan från Aloitus.se</h2>
                <p><strong>Namn:</strong> {html_module.escape(body.name)}</p>
                <p><strong>E-post:</strong> {html_module.escape(body.email)}</p>
                <p><strong>Meddelande:</strong></p>
                <p>{html_module.escape(body.message)}</p>
            """,
            }
        )
        return {"success": True}
    except Exception as e:
        print("RESEND ERROR:", e)
        return {"error": "Kunde inte skicka e-post"}

# AGENTS.md - Chatbot Project Context

## Project Overview

Multi-tenant AI-powered customer service chatbot supporting multiple companies via subdomains. Built with FastAPI and vanilla JavaScript. Uses OpenRouter API (DeepSeek v3.2) for AI responses.

## Architecture

### Multi-Tenant Design
- Each company gets their own subdomain (e.g., `comp1.orbixa.se`, `comp2.orbixa.se`)
- Subdomain is extracted from the Host header and mapped to a tenant directory
- Fallback to default tenant (`stadfirma`) if subdomain doesn't match an existing tenant folder

### Key Components

```
app/
├── main.py              # FastAPI application - all endpoints
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (OPENROUTER_API_KEY, OPENROUTER_MODEL)
├── static/
│   ├── index.html       # Full-page chat UI
│   ├── embed.html       # iframe-embedded chat (used by widget)
│   └── widget.js        # Embeddable widget script (injects floating chat button)
└── tenants/
    └── {tenant_name}/
        ├── config.json  # Company config (name, colors, welcome_message, avatar_emoji)
        ├── data.json    # Q&A data for AI context
        └── logo.png     # Company logo (optional)
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Full chat UI (index.html) |
| GET | `/embed` | Embedded chat UI for widget iframe |
| GET | `/config` | Returns company configuration JSON |
| GET | `/logo` | Returns company logo image |
| GET | `/widget.js` | Embeddable widget script |
| POST | `/chat` | Send message, receive AI response |

## Tenant Configuration Schema

### config.json
```json
{
    "company_name": "Company AB",
    "logo_url": "/logo",
    "colors": {
        "primary": "#2563eb",
        "primary_dark": "#1d4ed8",
        "text": "#ffffff"
    },
    "avatar_emoji": "🧹",
    "welcome_message": "Welcome message here..."
}
```

### data.json
```json
[
    {"question": "Q1", "answer": "A1"},
    {"question": "Q2", "answer": "A2"}
]
```

## Widget Embedding

Add to any website:
```html
<script src="https://comp1.orbixa.se/widget.js"></script>
```

The widget:
1. Fetches company config from `/config`
2. Creates floating chat button with company brand color
3. Opens iframe pointing to `/embed`
4. Works on mobile and desktop

## Tech Stack

- **Backend**: FastAPI, Python 3.13
- **AI**: OpenRouter API (DeepSeek v3.2)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Rate Limiting**: slowapi (30 req/min per IP)
- **Server**: Nginx + Systemd
- **SSL**: Cloudflare Origin CA

## DNS Configuration

- Domain: `orbixa.se`
- Pattern: `*.orbixa.se` → VPS IP (wildcard)
- Tenants: `comp1.orbixa.se`, `comp2.orbixa.se`, etc.

## Deployment

### Local Development
```bash
cd app
source venv/bin/activate
uvicorn main:app --reload --port 8001
```

### Production Deployment
```bash
./deploy.sh setup      # Initial setup
./deploy.sh nginx      # Configure nginx
./deploy.sh deploy     # Full deployment
./deploy.sh restart    # Restart service
./deploy.sh logs       # View logs
```

## Environment Variables Required

Create `app/.env`:
```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=deepseek/deepseek-v3.2
```

## Rate Limiting

- Application level: 30 requests/minute per IP (slowapi)
- Nginx level: 10 requests/second with burst of 10

## Adding a New Tenant

1. Create directory: `app/tenants/newcompany/`
2. Add `config.json` with company branding
3. Add `data.json` with Q&A pairs
4. Add `logo.png` (optional)
5. Live at `https://newcompany.orbixa.se` (requires wildcard DNS)

## Important Notes

- All AI responses are in Swedish
- Chat history is client-side only (max 10 messages)
- CORS is currently open (`allow_origins=["*"]`) - restrict in production
- `.env` and `tenants/` are gitignored for security
- Default tenant is `stadfirma` if subdomain not found

## File References

- Main API logic: `app/main.py:1`
- Tenant extraction: `app/main.py:33`
- System prompt: `app/main.py:110`
- Rate limit config: `app/main.py:103`
- Widget script: `app/static/widget.js:1`
- Nginx config: `deploy/nginx-chatbot.conf:1`

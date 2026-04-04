# Multi-Tenant AI Chatbot

AI-powered customer service chatbot supporting multiple companies via subdomains. Built with FastAPI and vanilla JavaScript. Uses OpenRouter API (DeepSeek v3.2) for AI responses.

## Features

- **Multi-tenant architecture** - Each company gets their own subdomain
- **Embeddable widget** - Add chat to any website with one script tag
- **Dynamic theming** - Company colors, logos, and branding
- **Rate limiting** - 10 requests/minute per IP
- **History trimming** - Prevents token blowup (max 10 messages)
- **Cloudflare-ready** - SSL, security headers, DDoS protection

## Project Structure

```
chatbot/
├── app/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (not committed)
│   ├── static/
│   │   ├── index.html       # Chat widget UI
│   │   └── widget.js        # Embeddable widget script
│   └── tenants/             # Company data (not in git)
│       └── stadfirma/       # Example tenant
│           ├── config.json  # Company config (name, colors, avatar)
│           ├── data.json    # Q&A data
│           └── logo.png     # Company logo
├── deploy.sh                # Deployment script
├── deploy/
│   ├── nginx-chatbot.conf   # Nginx configuration
│   └── chatbot.service      # Systemd service
└── scripts/                 # Utility scripts
```

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/famo7/chatbot.git
cd chatbot/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `app/.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=deepseek/deepseek-v3.2
```

### 3. Add Tenant Data

Create `app/tenants/stadfirma/config.json`:

```json
{
    "company_name": "Städfirma AB",
    "logo_url": "/logo",
    "colors": {
        "primary": "#2563eb",
        "primary_dark": "#1d4ed8",
        "text": "#ffffff"
    },
    "avatar_emoji": "🧹",
    "welcome_message": "Hej! Välkommen till Städfirma AB. Jag kan hjälpa dig med frågor om tjänster, priser och bokningar. Vad kan jag hjälpa dig med?"
}
```

Create `app/tenants/stadfirma/data.json`:

```json
[
    {"question": "Vad heter företaget?", "answer": "Städfirma AB"},
    {"question": "När grundades företaget?", "answer": "Vi grundades 2015."},
    {"question": "Vilka tjänster erbjuder ni?", "answer": "Vi erbjuder: Fönsterputs, Kontorsstädning, Storstädning, Flyttstädning och Mattvätt."},
    {"question": "Vad kostar era tjänster?", "answer": "Fönsterputs: 300 kr/timme, Kontorsstädning: 250 kr/timme, Storstädning: 400 kr/timme, Flyttstädning: 3500 kr fast pris, Mattvätt: 50 kr/kvm."},
    {"question": "Hur kontaktar jag er?", "answer": "E-post: info@stadfirma.se, Telefon: +46 70 123 45 67, Adress: Storgatan 1, 123 45 Stockholm"},
    {"question": "Vilka är era öppettider?", "answer": "Måndag-fredag: 08:00-18:00, Lördag: 09:00-14:00. Minst 48 timmars förvarning krävs för bokningar."},
    {"question": "Vilka områden täcker ni?", "answer": "Vi täcker: Stockholm, Solna, Sundbyberg och Lidingö. Kontakta oss för att kolla om vi finns i ditt område."},
    {"question": "Hur bokar jag en tjänst?", "answer": "Ring oss på +46 70 123 45 67 eller maila info@stadfirma.se. Vi kräver minst 48 timmars förvarning."},
    {"question": "Gäller RUT-avdrag?", "answer": "Ja! Du kan använda RUT-avdraget för hemstädning och fönsterputs. Det innebär att du betalar halva priset — vi sköter resten direkt med Skatteverket."}
]
```

Add logo: `app/tenants/stadfirma/logo.png`

### 4. Run Locally

```bash
uvicorn main:app --reload --port 8001
```

Test: http://localhost:8001

## Deployment

### Server Setup

```bash
./deploy.sh setup      # Install dependencies
./deploy.sh deploy     # Full deployment
```

### Nginx Configuration

```bash
./deploy.sh nginx      # Configure nginx
```

### DNS Setup (Cloudflare)

Add wildcard A record:
- Type: A
- Name: *
- Target: YOUR_VPS_IP
- Proxy: On

New companies work automatically — no DNS changes needed!

## Usage

### Direct Access

Visit your subdomain:
```
https://comp1.aloitus.se
```

### Embed on Any Website

Add this script tag to any HTML page:

```html
<script src="https://comp1.aloitus.se/widget.js"></script>
```

The widget will:
- Appear as a floating chat button (bottom-right)
- Use company's brand colors
- Load the full chat in an iframe
- Work on mobile and desktop

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Chat widget UI |
| GET | `/config` | Company configuration |
| GET | `/logo` | Company logo image |
| GET | `/widget.js` | Embeddable widget script |
| POST | `/chat` | Send message, get AI response |

### Chat Example

```bash
curl -X POST https://comp1.aloitus.se/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Vad kostar städning?", "history": []}'
```

Response:
```json
{"response": "Vi erbjuder fönsterputs för 300 kr/timme..."}
```

## Adding a New Company

1. **Create tenant directory on VPS:**
   ```bash
   mkdir app/tenants/newcompany
   ```

2. **Add files:**
   - `config.json` - Company name, colors, welcome message
   - `data.json` - Q&A pairs
   - `logo.png` - Company logo (optional)

3. **Done!** Live at `https://newcompany.aloitus.se`

## Tech Stack

- **Backend**: FastAPI, Python 3.13
- **AI**: OpenRouter API (DeepSeek v3.2)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Rate Limiting**: slowapi
- **Server**: Nginx + Systemd
- **SSL**: Cloudflare Origin CA

## Security Notes

- `.env` and `tenants/` are **not committed to git**
- API key stored only on server
- Rate limiting prevents abuse
- CORS restricted to your domain in production
- Tenant data stays on server only

## Management Commands

```bash
./deploy.sh setup      # Initial setup (venv, dependencies)
./deploy.sh install    # Install systemd service
./deploy.sh deploy     # Full deployment (setup, install, start)
./deploy.sh update     # Pull changes and update
./deploy.sh nginx      # Configure Nginx
./deploy.sh start      # Start the service
./deploy.sh stop       # Stop the service
./deploy.sh restart    # Restart the service
./deploy.sh logs       # View application logs
./deploy.sh status     # Check service status
./deploy.sh help       # Show help message
```

## Notes

- All AI responses are in Swedish
- Chat history kept client-side (max 10 messages)
- Logo fallback: hides if image fails to load
- Widget button color matches company brand
- Mobile responsive design
- Support for custom avatar emojis per tenant

## License

MIT

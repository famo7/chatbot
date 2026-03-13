# Stadfirma Chatbot

AI-powered customer service chatbot for **Stadfirma AB** (a Swedish cleaning company). Built with FastAPI and vanilla JavaScript. Uses OpenRouter API (DeepSeek v3.2) to answer customer questions in Swedish about services, pricing, booking, and more.

## Project Structure

```
stadfirma-bot/
├── README.md
└── app/
    ├── main.py            # FastAPI application
    ├── company_data.py    # Company Q&A data
    ├── requirements.txt   # Python dependencies
    ├── .env               # Environment variables (not committed)
    ├── .gitignore
    └── static/
        └── index.html     # Chat widget UI
```

## Setup

```bash
cd stadfirma-bot/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `app/`:

```
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=deepseek/deepseek-v3.2
```

## Run

```bash
uvicorn main:app --reload
```

- App: http://localhost:8000
- API docs: http://localhost:8000/docs

## API

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| GET | `/` | Serves the chat widget UI | - |
| POST | `/chat` | Send message, get AI response | 10/min per IP |

### Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Vad kostar städning?", "history": []}'
```

## Tech Stack

- **Backend**: FastAPI, Python 3.12
- **AI**: OpenRouter API (DeepSeek v3.2)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Rate limiting**: slowapi

## Notes

- All responses are in Swedish
- Chat history is maintained client-side and sent with each request (no server-side persistence)
- Company Q&A data is defined in `company_data.py` -- edit this file to customize
- CORS is open for development (all origins allowed)

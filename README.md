## Reverse Notebook LM - End-to-End Voice Setup

This repo uses the OpenAI Agents SDK for voice with two entry points:

- WebRTC web test page (browser mic ↔ OpenAI Realtime)
- Twilio voice integration (phone call ↔ OpenAI Realtime)

### Prerequisites

- **OpenAI API key**: export in your shell: `export OPENAI_API_KEY=sk-...`
- macOS with working mic/speakers
- Python 3.10+
- Node.js 18+
- Optional for Twilio: a Twilio account/number and `ngrok` for public URL

### 1) Start Python Tools API (FastAPI)

Exposes `POST /tools/file_operation` used by the agent.

```bash
cd /Users/samliu/code/reverse-notebook-lm/backend
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 2) Agents SDK gateway (web test page + Twilio)

This starts a TypeScript gateway using the OpenAI Agents SDK. It exposes:

- A web test page at `http://localhost:8080` that connects mic ↔ Realtime via WebRTC (no custom audio encoding needed)
- Twilio voice webhook + media stream bridge that forwards phone-call audio ↔ Realtime

Setup:

```bash
cd /Users/samliu/code/reverse-notebook-lm/voice-gateway
npm install
```

Run the server:

```bash
npm run dev
# Server on http://localhost:8080
```

#### 2A) Web test (WebRTC in browser)

1. Open `http://localhost:8080`
2. Click Connect and grant mic access
3. Speak; you should hear the assistant reply
4. Click Disconnect to stop

The browser sends SDP to the gateway (`/realtime/sdp`), which forwards it to OpenAI using your server-side `OPENAI_API_KEY`. Audio I/O is handled by WebRTC; your API key never leaves the server.

#### 2B) Twilio voice integration

1. Expose your local server publicly (for Twilio to reach it):

```bash
ngrok http 8080
# copy the https URL shown by ngrok
```

2. In the Twilio Console, set your phone number’s Voice webhook to `POST https://<your-ngrok-domain>/twilio/voice`.

3. Call your Twilio number. The gateway responds with TwiML to start a media stream to `/twilio/stream`, and bridges audio with the Realtime Agent. You should be able to talk to the assistant over the phone.

Files:

- `voice-gateway/src/server.ts`: Express server, static web, Twilio webhook, WS upgrade, and RealtimeAgent wiring
- `voice-gateway/public/index.html`: WebRTC web test page
- `voice-gateway/src/tools/fileTool.ts`: `file_operation` tool calling Python FastAPI (`http://localhost:8000/tools/file_operation`)

### Tools and scripts

- The `file_operation` tool lets the assistant create/append to markdown files under `backend/workspace`.
- Script prompts live in `backend/scripts/*.json` and may be invoked via voice (e.g., “load blog writer”).

### Troubleshooting

- **FastAPI not reachable**: ensure it’s running on port 8000 before starting the gateway.
- **Twilio 403 to webhook**: ensure your webhook URL matches the exact ngrok URL and your server is running. If you enable signature validation, be sure to set `PUBLIC_URL` and `TWILIO_AUTH_TOKEN` and compute the signature correctly.

### Useful links

- Voice Agents guide: [Voice Agents guide](https://platform.openai.com/docs/guides/voice-agents?voice-agent-architecture=speech-to-speech)
- OpenAI Agents SDK (TypeScript): [OpenAI Agents SDK](https://openai.github.io/openai-agents-js/)



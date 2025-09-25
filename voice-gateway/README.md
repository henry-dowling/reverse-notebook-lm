Voice Gateway (Agents SDK + Twilio)

Setup
- Copy .env.example to .env and set OPENAI_API_KEY, PUBLIC_URL, PORT.
- Install deps: npm install
- Run dev: npm run dev

Twilio configuration
- Create a Twilio phone number and set Voice webhook to POST to `${PUBLIC_URL}/twilio/voice`.
- Ensure your PUBLIC_URL is reachable from Twilio (use ngrok for local).

What this does
- Twilio calls your number → Voice webhook responds with TwiML <Start><Stream> to `${PUBLIC_URL}/twilio/stream`.
- The server upgrades to WebSocket, bridges audio via TwilioRealtimeTransportLayer to a RealtimeAgent.
- The agent can call the `file_operation` tool which writes to `backend/workspace`.



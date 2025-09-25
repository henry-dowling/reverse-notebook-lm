import 'dotenv/config';
import express from 'express';
import crypto from 'node:crypto';
import { RealtimeAgent } from '@openai/agents/realtime';
import { TwilioRealtimeTransportLayer } from '@openai/agents-extensions';
import { fileOperationTool } from './tools/fileTool.js';
import { scriptLoadTool, listAvailableScripts } from './tools/scriptTool.js';

const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use(express.static('public'));

const PORT = Number(process.env.PORT || 8080);
const PUBLIC_URL = process.env.PUBLIC_URL || `http://localhost:${PORT}`;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

function validateTwilioRequest(req: express.Request): boolean {
  const token = process.env.TWILIO_AUTH_TOKEN;
  if (!token) return true; // skip in dev if not set
  const signature = req.get('X-Twilio-Signature') || '';
  const url = `${PUBLIC_URL}/twilio/voice`; // must match webhook URL
  const params = req.body || {};
  const sorted = Object.keys(params).sort().reduce((acc: any, k) => (acc[k] = params[k], acc), {});
  const data = url + Object.entries(sorted).map(([k, v]) => `${k}${v}`).join('');
  const computed = crypto.createHmac('sha1', token).update(data).digest('base64');
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(computed));
}

app.post('/twilio/voice', (req, res) => {
  // Optionally validate Twilio signature
  // if (!validateTwilioRequest(req)) return res.status(403).send('Forbidden');

  const wsUrl = `${PUBLIC_URL.replace('http', 'ws')}/twilio/stream`;
  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
    <Response>
      <Say>Connecting you to the assistant.</Say>
      <Start>
        <Stream url="${wsUrl}" />
      </Start>
      <Pause length="60" />
    </Response>`;
  res.type('text/xml').send(twiml);
});

// WebRTC signaling proxy: browser posts SDP offer here; gateway forwards to OpenAI and returns SDP answer
app.post('/realtime/sdp', async (req, res) => {
  try {
    const sdpOffer = String(req.body?.sdp || '');
    if (!sdpOffer) return res.status(400).json({ error: 'Missing SDP' });
    if (!OPENAI_API_KEY) return res.status(500).json({ error: 'Server missing OPENAI_API_KEY' });

    const rtResp = await fetch('https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/sdp',
        'OpenAI-Beta': 'realtime=v1'
      },
      body: sdpOffer
    });
    const sdpAnswer = await rtResp.text();
    if (!rtResp.ok) return res.status(rtResp.status).send(sdpAnswer);
    res.type('application/sdp').send(sdpAnswer);
  } catch (e: any) {
    console.error('SDP proxy error', e);
    res.status(500).json({ error: 'SDP proxy error' });
  }
});

// Simple in-memory map of active sessions by Twilio stream sid
const activeAgents = new Map<string, RealtimeAgent>();

import { WebSocketServer } from 'ws';
const wss = new WebSocketServer({ noServer: true });

// Upgrade HTTP -> WS for Twilio media stream
const server = app.listen(PORT, () => {
  console.log(`Voice gateway listening on ${PORT}`);
});

server.on('upgrade', (request, socket, head) => {
  const { url } = request;
  if (!url || !url.startsWith('/twilio/stream')) {
    socket.destroy();
    return;
  }
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

wss.on('connection', async (ws) => {
  // Each websocket corresponds to a Twilio media stream for a single call
  const transport = new TwilioRealtimeTransportLayer({
    websocket: ws,
  });

  // Enhanced system prompt with script information
  const instructions = `You are a helpful voice assistant that can guide users through interactive scripts and collaborative activities. You have access to several interactive scripts that provide structured guidance for different activities.

Available scripts:
- blog_writer: Helps create engaging blog posts through conversation
- brainstorm_session: Facilitates creative idea generation and development  
- email_workshop: Guides users in crafting effective emails with proper structure
- improv_game: Play collaborative storytelling games using "Yes, and..." principles
- interview_prep: Practice interview scenarios and provide real-time feedback

Use the get_script_info tool to retrieve detailed information about any script, including its stages, prompts, and guidance. This will help you provide structured, script-based assistance to users.

You can also use the file_operation tool to create and manage markdown files to capture content during your interactions.`;

  const agent = new RealtimeAgent({
    name: 'Assistant',
    instructions: instructions,
    transportLayer: transport,
    tools: {
      file_operation: async (args) => {
        return await fileOperationTool(args as any);
      },
      get_script_info: async (args: any) => {
        try {
          const result = await scriptLoadTool(args);
          return {
            success: true,
            script: result.script,
            guidance: result.instructions
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error'
          };
        }
      },
      list_available_scripts: async () => {
        try {
          const scripts = await listAvailableScripts();
          return {
            success: true,
            scripts
          };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error'
          };
        }
      }
    }
  });

  activeAgents.set(crypto.randomUUID(), agent);
  try {
    await agent.connect();
  } catch (err) {
    console.error('Agent connection error', err);
    ws.close();
  }
});



# voice-receptionist

A German-speaking **voice AI receptionist** for a (fictional) physiotherapy practice, built on
[LiveKit Agents](https://docs.livekit.io/agents/). Callers reach it via WebRTC or a SIP trunk;
it finds free slots, books appointments and takes callback requests.

```
caller ──SIP/WebRTC──► LiveKit room ──► VAD ─► STT (Deepgram) ─► LLM + tools ─► TTS (Cartesia) ──► caller
                                                              │
                                                       clinic.py (business logic)
```

## Design decisions from production voice work

- **Business logic is separate from the voice stack** (`agent/clinic.py`), so it is unit-tested without audio or API keys.
- **Speech-friendly outputs:** at most three slots offered, times rendered for reading aloud, short answers.
- **Validate what callers say:** phone numbers are normalised (0151… → +49151…) and rejected if incomplete *before* anything is booked.
- **Confirmation before side effects:** the prompt requires repeating name, date, time and number before booking.
- **Bounded tool loops** (`max_tool_steps=3`) and a callback fallback when the caller needs a human.
- **Safety:** no medical advice; emergencies are redirected; tool output is treated as data.

## Run

```bash
pip install -r requirements.txt
pytest -q                                  # business logic + tool registration, no keys needed
cp .env.example .env                       # LiveKit, Deepgram, OpenAI, Cartesia keys
python -m agent.receptionist console       # talk to it in the terminal
python -m agent.receptionist dev           # connect to a LiveKit project (add a SIP trunk for phone calls)
```

## Background

Patterns distilled from building and operating phone assistants that handle real calls for businesses in DACH.
Domain, names and data here are fictional.

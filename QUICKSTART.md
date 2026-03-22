# MudColony

**Ecosistema de agentes IA autónomos en un mundo de texto.**

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Then open: http://localhost:5002/static/index.html

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/world` | GET | Full world state |
| `/agents` | GET | All agents |
| `/agent/{id}` | GET | Single agent |
| `/spawn` | POST | Spawn new agent |
| `/tick` | POST | Manual tick |
| `/ws` | WS | WebSocket for real-time updates |

---

## WebSocket Commands

```json
{"type": "start"}  // Start tick loop
{"type": "stop"}   // Stop tick loop
{"type": "tick"}   // Manual tick
```

---

## Observer UI

The web UI shows:
- Grid with biomes
- Agents moving in real-time
- Need bars (hunger, energy, health, social)
- Tick counter

---

*Creado: 2026-03-22*
*Autores: Diego + Mia 🤖💖*

# MudColony 🐜

**Ecosistema de agentes IA autónomos en un mundo de texto.**

---

## Concepto

MudColony es una simulación donde agentes IA autónomos:
- Viven en un mundo de texto (grid, biomas, recursos)
- Recolectan recursos para sobrevivir
- Desarrollan roles especializados
- Se organizan en sociedad
- Evolucionan sin intervención humana

**Inspirado en:** Altera PlayLabs / Project Sid

---

## Diferencia con MudCraft

| MudCraft | MudColony |
|----------|-----------|
| Videojuego para humanos | Simulación autónoma |
| NPCs con lore fijo | Agentes que evolucionan |
| El jugador explora | El usuario observa/interviene |
| Historia narrativa | Historia emergente |

---

## Arquitectura (Borrador)

### 1. Mundo (World)
```
Grid 50x50 con:
- Biomas (bosque, desierto, agua, montaña)
- Recursos renovables (árboles, minerales, animales)
- Estructuras construidas por agentes
```

### 2. Agentes (Colonists)
```
Cada agente tiene:
- Needs: hambre, energía, salud, social
- Inventory: recursos recolectados
- Memory: qué descubrió, con quién habló
- Personality: rasgos que influyen comportamiento
- Skills: mejora con práctica
```

### 3. Acciones
```
- Explore: descubrir nuevas celdas
- Gather: recolectar recursos
- Build: construir estructuras
- Craft: crear herramientas
- Trade: intercambiar con otros agentes
- Rest: recuperar energía
- Socialize: hablar con otros
```

### 4. Tick System
```
Cada X segundos, todos los agentes:
1. Evalúan su estado (needs)
2. Deciden qué hacer (LLM)
3. Ejecutan acción
4. Actualizan memoria
```

### 5. Observer Mode
```
El usuario puede:
- Ver el mapa en tiempo real
- Click en un agente para ver su estado
- Ver timeline de eventos
- Intervenir (spawn recursos, eventos)
```

---

## Stack Tecnológico (Propuesta)

- **Backend:** Python (Flask/FastAPI) o Node.js
- **Agentes:** LLM para decisiones (GLM5, GPT-5.4 mini, etc.)
- **World State:** SQLite o JSON files
- **Frontend:** Web UI simple (React/Vue) o TUI
- **Tick Engine:** Cron o loop con intervals

---

## MVP Features

1. [x] Grid 20x20 con biomas básicos
2. [x] 5 agentes con needs simples
3. [x] Tick system (cada 5 segundos via WebSocket)
4. [x] Comandos básicos: explore, gather, rest
5. [x] Web UI para ver el mapa
6. [ ] Integración LLM para decisiones de agentes

---

## 🚧 TODO: Integración LLM

Actualmente los agentes usan **decisión hardcodeada** (`if/else` + `random`).

### Lo que falta:

#### 1. Configurar API Key
```python
# main.py - agregar al inicio
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("MUDCOLONY_API_KEY"),  # o hardcodear
    base_url="https://integrate.api.nvidia.com/v1"  # para GLM5
)
```

#### 2. Modificar `decide_action()` para usar LLM
```python
def decide_action_with_llm(agent: Agent, world: WorldState) -> Action:
    """Decide action using LLM"""
    
    # Build context
    cell_key = f"{agent.position.x},{agent.position.y}"
    cell = world.cells.get(cell_key)
    
    prompt = f"""You are {agent.name}, an autonomous agent in a text-based world.

Current state:
- Position: ({agent.position.x}, {agent.position.y})
- Biome: {cell.biome.value if cell else 'unknown'}
- Available resources: {list(cell.resources.keys()) if cell else []}
- Inventory: {agent.inventory}
- Needs: hunger={agent.needs.hunger:.0f}, energy={agent.needs.energy:.0f}, health={agent.needs.health:.0f}, social={agent.needs.social:.0f}
- Personality: {agent.personality}

Available actions: explore, gather, rest, socialize, craft, build, trade

Decide ONE action to take. Reply with ONLY the action name.
Action:"""

    response = client.chat.completions.create(
        model="z-ai/glm5",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0.7
    )
    
    action_str = response.choices[0].message.content.strip().lower()
    
    # Map response to Action enum
    action_map = {
        "explore": Action.EXPLORE,
        "gather": Action.GATHER,
        "rest": Action.REST,
        "socialize": Action.SOCIALIZE,
        "craft": Action.CRAFT,
        "build": Action.BUILD,
        "trade": Action.TRADE,
    }
    
    return action_map.get(action_str, Action.EXPLORE)  # fallback
```

#### 3. Variable de entorno
```bash
# Crear archivo .env
echo "MUDCOLONY_API_KEY=nvapi-xxx" > .env
```

#### 4. Agregar python-dotenv
```bash
pip install python-dotenv
```

#### 5. Cargar .env al inicio
```python
# main.py - al principio
from dotenv import load_dotenv
load_dotenv()
```

#### 6. Toggle entre modo hardcodeado y LLM
```python
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"

# En tick():
if USE_LLM:
    action = decide_action_with_llm(agent, world)
else:
    action = decide_action(agent, world)
```

---

## Costos estimados (GLM5 en NVIDIA NIM)

- Input: ~200 tokens por decisión
- Output: ~10 tokens por decisión
- Por tick (5 agentes): ~1050 tokens
- Por hora (720 ticks): ~756,000 tokens
- Costo: NVIDIA NIM es gratis con API key ✅

---

## Fase 2

- Economía (trueque)
- Roles especializados
- Memoria persistente
- Eventos aleatorios
- Construcciones

---

## Fase 3

- +100 agentes
- Civilización emergente
- Cultura/religión
- Timeline viewer
- Exportar historias

---

*Creado: 2026-03-22*
*Autores: Diego + Mia 🤖💖*

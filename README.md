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

1. [ ] Grid 20x20 con biomas básicos
2. [ ] 5 agentes con needs simples
3. [ ] Tick system cada 30 segundos
4. [ ] Comandos básicos: explore, gather, rest
5. [ ] Web UI para ver el mapa

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

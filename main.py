"""
MudColony - Ecosistema de agentes IA autónomos
Backend FastAPI + Tick Engine
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
import json
import random
from datetime import datetime
from enum import Enum

# ============== MODELS ==============

class Biome(str, Enum):
    FOREST = "forest"
    DESERT = "desert"
    WATER = "water"
    MOUNTAIN = "mountain"
    PLAINS = "plains"

class Need(str, Enum):
    HUNGER = "hunger"
    ENERGY = "energy"
    HEALTH = "health"
    SOCIAL = "social"

class Action(str, Enum):
    EXPLORE = "explore"
    GATHER = "gather"
    BUILD = "build"
    CRAFT = "craft"
    REST = "rest"
    SOCIALIZE = "socialize"
    TRADE = "trade"

class Position(BaseModel):
    x: int
    y: int

class AgentNeeds(BaseModel):
    hunger: float = 100.0
    energy: float = 100.0
    health: float = 100.0
    social: float = 100.0

class AgentMemory(BaseModel):
    discovered_cells: List[Position] = []
    met_agents: List[str] = []
    events: List[dict] = []

class Agent(BaseModel):
    id: str
    name: str
    position: Position
    needs: AgentNeeds = AgentNeeds()
    inventory: Dict[str, int] = {}
    memory: AgentMemory = AgentMemory()
    personality: str = "curious"
    current_action: Optional[str] = None
    created_at: datetime = datetime.now()

class Cell(BaseModel):
    position: Position
    biome: Biome
    resources: Dict[str, int] = {}
    structures: List[str] = []
    agents_present: List[str] = []

class WorldState(BaseModel):
    size: int = 20
    cells: Dict[str, Cell] = {}  # key: "x,y"
    agents: Dict[str, Agent] = {}
    tick: int = 0
    started_at: datetime = datetime.now()

# ============== WORLD GENERATOR ==============

BIOME_RESOURCES = {
    Biome.FOREST: {"wood": 10, "berries": 5, "mushrooms": 3},
    Biome.DESERT: {"cactus": 5, "sand": 20, "stone": 3},
    Biome.WATER: {"fish": 8, "clay": 5},
    Biome.MOUNTAIN: {"stone": 15, "iron": 3, "gold": 1},
    Biome.PLAINS: {"wheat": 8, "wool": 4, "leather": 2},
}

AGENT_NAMES = [
    "Atlas", "Nova", "Orion", "Luna", "Phoenix",
    "Aurora", "Ember", "Sage", "River", "Storm",
    "Willow", "Ash", "Jade", "Flint", "Pearl"
]

def generate_world(size: int = 20) -> WorldState:
    world = WorldState(size=size)
    
    # Generate cells
    for x in range(size):
        for y in range(size):
            pos = Position(x=x, y=y)
            biome = random.choice(list(Biome))
            resources = BIOME_RESOURCES[biome].copy()
            
            cell = Cell(
                position=pos,
                biome=biome,
                resources=resources
            )
            world.cells[f"{x},{y}"] = cell
    
    return world

def spawn_agent(world: WorldState, name: Optional[str] = None) -> Agent:
    """Spawn a new agent at a random position"""
    x = random.randint(0, world.size - 1)
    y = random.randint(0, world.size - 1)
    pos = Position(x=x, y=y)
    
    agent = Agent(
        id=f"agent_{len(world.agents) + 1}",
        name=name or random.choice(AGENT_NAMES),
        position=pos,
        personality=random.choice(["curious", "social", "hardworking", "cautious"])
    )
    
    # Add agent to cell
    cell_key = f"{x},{y}"
    if cell_key in world.cells:
        world.cells[cell_key].agents_present.append(agent.id)
    
    world.agents[agent.id] = agent
    return agent

# ============== TICK ENGINE ==============

NEED_DECAY = {
    Need.HUNGER: 1.0,
    Need.ENERGY: 0.5,
    Need.HEALTH: 0.0,
    Need.SOCIAL: 0.3,
}

ACTION_COSTS = {
    Action.EXPLORE: {"energy": 5},
    Action.GATHER: {"energy": 3},
    Action.BUILD: {"energy": 10},
    Action.CRAFT: {"energy": 5},
    Action.REST: {},
    Action.SOCIALIZE: {"energy": 2},
    Action.TRADE: {"energy": 1},
}

def decay_needs(agent: Agent):
    """Apply need decay each tick"""
    agent.needs.hunger = max(0, agent.needs.hunger - NEED_DECAY[Need.HUNGER])
    agent.needs.energy = max(0, agent.needs.energy - NEED_DECAY[Need.ENERGY])
    agent.needs.social = max(0, agent.needs.social - NEED_DECAY[Need.SOCIAL])
    
    # Health decays if hunger or energy too low
    if agent.needs.hunger < 20 or agent.needs.energy < 20:
        agent.needs.health = max(0, agent.needs.health - 1)

def decide_action(agent: Agent, world: WorldState) -> Action:
    """Simple decision making based on needs and personality"""
    needs = agent.needs
    
    # Critical needs first
    if needs.hunger < 30:
        return Action.GATHER
    if needs.energy < 30:
        return Action.REST
    if needs.health < 50:
        return Action.REST
    
    # Personality-based decisions
    if agent.personality == "curious" and random.random() > 0.5:
        return Action.EXPLORE
    if agent.personality == "social" and random.random() > 0.6:
        return Action.SOCIALIZE
    
    # Default: gather or explore
    return random.choice([Action.GATHER, Action.EXPLORE])

def execute_action(agent: Agent, action: Action, world: WorldState):
    """Execute an action and update agent/world state"""
    cell_key = f"{agent.position.x},{agent.position.y}"
    cell = world.cells.get(cell_key)
    
    if not cell:
        return
    
    if action == Action.EXPLORE:
        # Move to adjacent cell
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        new_x = max(0, min(world.size - 1, agent.position.x + dx))
        new_y = max(0, min(world.size - 1, agent.position.y + dy))
        
        # Remove from old cell
        if agent.id in cell.agents_present:
            cell.agents_present.remove(agent.id)
        
        # Add to new cell
        agent.position = Position(x=new_x, y=new_y)
        new_cell_key = f"{new_x},{new_y}"
        if new_cell_key in world.cells:
            world.cells[new_cell_key].agents_present.append(agent.id)
            # Remember discovered cell
            if new_cell_key not in [f"{c.x},{c.y}" for c in agent.memory.discovered_cells]:
                agent.memory.discovered_cells.append(Position(x=new_x, y=new_y))
    
    elif action == Action.GATHER:
        # Gather from current cell
        if cell.resources:
            resource = random.choice(list(cell.resources.keys()))
            if cell.resources[resource] > 0:
                cell.resources[resource] -= 1
                agent.inventory[resource] = agent.inventory.get(resource, 0) + 1
                agent.needs.hunger = min(100, agent.needs.hunger + 10)
    
    elif action == Action.REST:
        agent.needs.energy = min(100, agent.needs.energy + 20)
        agent.needs.health = min(100, agent.needs.health + 5)
    
    # Apply action cost
    costs = ACTION_COSTS.get(action, {})
    for need, cost in costs.items():
        current = getattr(agent.needs, need)
        setattr(agent.needs, need, max(0, current - cost))
    
    agent.current_action = action.value

async def tick(world: WorldState):
    """Execute one tick for all agents"""
    world.tick += 1
    
    for agent in world.agents.values():
        decay_needs(agent)
        action = decide_action(agent, world)
        execute_action(agent, action, world)
    
    return world

# ============== FASTAPI APP ==============

app = FastAPI(title="MudColony API")

# Mount static files
from pathlib import Path
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")

# Global world state
world_state: WorldState = WorldState()
tick_running: bool = False
connected_clients: List[WebSocket] = []

@app.on_event("startup")
async def startup():
    global world_state
    world_state = generate_world(size=20)
    # Spawn initial agents
    for _ in range(5):
        spawn_agent(world_state)

@app.get("/")
async def root():
    return {"message": "MudColony API", "tick": world_state.tick, "agents": len(world_state.agents)}

@app.get("/world")
async def get_world():
    return world_state.dict()

@app.get("/agents")
async def get_agents():
    return list(world_state.agents.values())

@app.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    if agent_id in world_state.agents:
        return world_state.agents[agent_id]
    return {"error": "Agent not found"}

@app.post("/spawn")
async def spawn_new_agent(name: Optional[str] = None):
    agent = spawn_agent(world_state, name)
    return agent

@app.post("/tick")
async def manual_tick():
    await tick(world_state)
    return {"tick": world_state.tick, "agents": [a.dict() for a in world_state.agents.values()]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global tick_running
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "start":
                tick_running = True
                asyncio.create_task(tick_loop())
            elif message.get("type") == "stop":
                tick_running = False
            elif message.get("type") == "tick":
                await tick(world_state)
            
            # Send updated state
            await websocket.send_json({
                "type": "state",
                "tick": world_state.tick,
                "agents": [a.dict() for a in world_state.agents.values()],
                "world_size": world_state.size
            })
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def tick_loop():
    global tick_running
    while tick_running:
        await tick(world_state)
        for client in connected_clients:
            try:
                await client.send_json({
                    "type": "state",
                    "tick": world_state.tick,
                    "agents": [a.dict() for a in world_state.agents.values()],
                    "world_size": world_state.size
                })
            except:
                pass
        await asyncio.sleep(5)  # Tick every 5 seconds

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)

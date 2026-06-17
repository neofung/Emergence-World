import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.config import get_settings
from emergence_world.database import engine, get_db
from emergence_world.models import Agent, Base, Landmark, WorldState

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Emergence World",
    description="AI social simulation platform",
    version="0.1.0",
    lifespan=lifespan,
)


# --- Health ---

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# --- World ---

@app.get("/api/v1/world/state")
async def world_state(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    result = await db.execute(select(WorldState).limit(1))
    ws = result.scalar_one_or_none()
    if ws is None:
        return {"initialized": False}
    return {
        "initialized": True,
        "current_time": str(ws.current_time),
        "time_mode": ws.time_mode,
        "day_count": ws.day_count,
        "is_paused": ws.is_paused,
        "current_weather": ws.current_weather,
    }


# --- Agents ---

@app.get("/api/v1/agents")
async def list_agents(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(select(Agent).order_by(Agent.name))
    agents = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "role": a.role,
            "agent_type": a.agent_type.value,
            "energy": a.energy,
            "knowledge": a.knowledge,
            "influence": a.influence,
            "compute_credits": a.compute_credits,
            "is_alive": a.is_alive,
            "position": {"x": a.position_x, "y": a.position_y, "z": a.position_z},
        }
        for a in agents
    ]


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    agent = await db.get(Agent, agent_id)
    if agent is None:
        return {"error": "Agent not found"}
    return {
        "id": str(agent.id),
        "name": agent.name,
        "role": agent.role,
        "personality": agent.personality,
        "north_star_goal": agent.north_star_goal,
        "agent_type": agent.agent_type.value,
        "energy": agent.energy,
        "knowledge": agent.knowledge,
        "influence": agent.influence,
        "compute_credits": agent.compute_credits,
        "is_alive": agent.is_alive,
        "mood": agent.mood,
        "position": {"x": agent.position_x, "y": agent.position_y, "z": agent.position_z},
    }


# --- Landmarks ---

@app.get("/api/v1/landmarks")
async def list_landmarks(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(select(Landmark).order_by(Landmark.name))
    landmarks = result.scalars().all()
    return [
        {
            "id": str(lm.id),
            "name": lm.name,
            "tagline": lm.tagline,
            "category": lm.category.value,
            "position": {"x": lm.position_x, "y": lm.position_y, "z": lm.position_z},
            "is_open": lm.is_open,
        }
        for lm in landmarks
    ]


# --- WebSocket (stub) ---

@app.websocket("/ws/events")
async def websocket_events(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_json({"echo": data})
    except WebSocketDisconnect:
        pass

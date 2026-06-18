import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from emergence_world.backend.config import get_settings
from emergence_world.backend.core.engine import SimulationEngine
from emergence_world.backend.core.llm import LLMClient
from emergence_world.backend.database import async_session, engine, get_db
from emergence_world.backend.models import Agent, Base, ConstitutionArticle, Landmark, WorldState
from emergence_world.backend.seed.loader import seed_database

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)

# Global simulation state
_sim_engine: SimulationEngine | None = None
_sim_task: asyncio.Task | None = None
_llm_client: LLMClient | None = None


def _get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed database if empty
    async with async_session() as db:
        await seed_database(db)
        logger.info("Seed data loaded")

    yield
    if _sim_engine:
        _sim_engine.stop()
    if _llm_client:
        await _llm_client.close()
    await engine.dispose()


app = FastAPI(
    title="Emergence World",
    description="AI social simulation platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
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
            "display_name": a.display_name or a.name,
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
            "display_name": lm.display_name or lm.name,
            "tagline": lm.tagline,
            "description": lm.description,
            "category": lm.category.value,
            "position": {"x": lm.position_x, "y": lm.position_y, "z": lm.position_z},
            "is_open": lm.is_open,
            "folklore": lm.folklore,
            "fun_fact": lm.fun_fact,
            "location_gated_tools": lm.location_gated_tools,
        }
        for lm in landmarks
    ]


# --- Constitution ---

@app.get("/api/v1/constitution")
async def constitution(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(
        select(ConstitutionArticle).where(ConstitutionArticle.is_active.is_(True)).order_by(ConstitutionArticle.number)
    )
    return [
        {"number": a.number, "title": a.title, "content": a.content}
        for a in result.scalars().all()
    ]


# --- AWI Metrics ---

@app.get("/api/v1/metrics/awi")
async def awi_metrics(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    from emergence_world.backend.core.awi import calculate_awi
    return await calculate_awi(db)


# --- Console ---

@app.get("/api/v1/console/status")
async def console_status(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    from emergence_world.backend.ui.console import TerminalUI
    ui = TerminalUI(db)
    return {"output": await ui.show_status()}


@app.get("/api/v1/console/agents")
async def console_agents(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    from emergence_world.backend.ui.console import TerminalUI
    ui = TerminalUI(db)
    return {"output": await ui.show_agents()}


@app.get("/api/v1/console/agent/{name}")
async def console_agent_detail(name: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    from emergence_world.backend.ui.console import TerminalUI
    ui = TerminalUI(db)
    return {"output": await ui.show_agent_detail(name)}


@app.get("/api/v1/console/landmarks")
async def console_landmarks(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    from emergence_world.backend.ui.console import TerminalUI
    ui = TerminalUI(db)
    return {"output": await ui.show_landmarks()}


@app.get("/api/v1/console/conversations")
async def console_conversations(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    from emergence_world.backend.ui.console import TerminalUI
    ui = TerminalUI(db)
    return {"output": await ui.show_recent_conversations()}


@app.get("/api/v1/console/proposals")
async def console_proposals(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    from emergence_world.backend.ui.console import TerminalUI
    ui = TerminalUI(db)
    return {"output": await ui.show_proposals()}


# --- Simulation Control ---

@app.post("/api/v1/simulation/start")
async def simulation_start() -> dict[str, Any]:
    global _sim_engine, _sim_task
    if _sim_engine and _sim_engine._running:
        return {"error": "Simulation already running", **_sim_engine.status}

    async with async_session() as db:
        _sim_engine = SimulationEngine(db, _get_llm_client())
        await _sim_engine.initialize()

    async def _run():
        async with async_session() as db:
            _sim_engine.db = db
            _sim_engine.llm = _get_llm_client()
            await _sim_engine.run()

    _sim_task = asyncio.create_task(_run())
    return {"message": "Simulation started", **_sim_engine.status}


@app.post("/api/v1/simulation/pause")
async def simulation_pause() -> dict[str, Any]:
    if not _sim_engine:
        return {"error": "No simulation running"}
    _sim_engine.pause()
    return {"message": "Simulation paused", **_sim_engine.status}


@app.post("/api/v1/simulation/resume")
async def simulation_resume() -> dict[str, Any]:
    if not _sim_engine:
        return {"error": "No simulation running"}
    _sim_engine.resume()
    return {"message": "Simulation resumed", **_sim_engine.status}


@app.post("/api/v1/simulation/stop")
async def simulation_stop() -> dict[str, Any]:
    global _sim_engine, _sim_task
    if not _sim_engine:
        return {"error": "No simulation running"}
    _sim_engine.stop()
    if _sim_task:
        _sim_task.cancel()
        _sim_task = None
    status = _sim_engine.status
    _sim_engine = None
    return {"message": "Simulation stopped", **status}


@app.get("/api/v1/simulation/status")
async def simulation_status() -> dict[str, Any]:
    if not _sim_engine:
        return {"running": False, "paused": False}
    return _sim_engine.status


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

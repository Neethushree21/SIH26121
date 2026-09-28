import asyncio
import json
import random
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.models.drilling_event import DrillingHazard
from app.schemas.alert import TelemetryTick, TelemetryEvaluationResponse
from app.services.risk_engine import risk_engine

router = APIRouter()

# Global state for simulated eRTMAC telemetry
SIMULATION_STATE = {
    "tick": 0,
    "depth_md": 2320.0,
    "depth_tvd": 2314.5,
    "rop_m_hr": 14.5,
    "wob_klbs": 21.0,
    "torque_kft_lbs": 11.2,
    "standpipe_pressure_psi": 2550.0,
    "mud_weight_ppg": 10.4,
    "flow_out_pct": 100.0,
    "active_formation": "Tipam Sandstone"
}

def advance_simulation_tick() -> TelemetryTick:
    """Simulates realistic operational drilling parameters advancing through Assam formations."""
    SIMULATION_STATE["tick"] += 1
    t = SIMULATION_STATE["tick"]

    # Increment depth
    depth_inc = random.uniform(0.3, 0.8)
    SIMULATION_STATE["depth_md"] += depth_inc
    SIMULATION_STATE["depth_tvd"] += depth_inc * 0.98
    curr_md = SIMULATION_STATE["depth_md"]

    # Determine formation based on depth
    if curr_md < 1840:
        formation = "Girujan Clay"
    elif curr_md < 2790:
        formation = "Tipam Sandstone"
    elif curr_md < 3580:
        formation = "Barail Coal-Shale"
    else:
        formation = "Kopili Shale"
    SIMULATION_STATE["active_formation"] = formation

    # Simulate dynamic hazard behaviors
    if 2335 <= curr_md <= 2355:
        # Simulate partial lost circulation in Tipam
        rop = random.uniform(22.0, 32.0)
        torque = random.uniform(9.0, 13.0)
        pressure = random.uniform(1500.0, 1900.0) # pressure drop
        flow_out = random.uniform(40.0, 65.0) # loss of returns
        wob = random.uniform(16.0, 20.0)
    elif 3410 <= curr_md <= 3435:
        # Simulate gas kick drilling break in Barail
        rop = random.uniform(28.0, 42.0) # drilling break!
        torque = random.uniform(12.0, 16.0)
        pressure = random.uniform(2100.0, 2400.0)
        flow_out = random.uniform(125.0, 160.0) # pit gain
        wob = random.uniform(14.0, 18.0)
    elif 2880 <= curr_md <= 2905:
        # Simulate tight hole / torque spike
        rop = random.uniform(1.0, 3.5) # stall
        torque = random.uniform(28.0, 39.0) # severe torque spike!
        pressure = random.uniform(2850.0, 3400.0)
        flow_out = random.uniform(95.0, 102.0)
        wob = random.uniform(28.0, 36.0)
    else:
        # Normal steady drilling
        rop = random.uniform(10.0, 16.0)
        torque = random.uniform(9.5, 13.5)
        pressure = random.uniform(2400.0, 2700.0)
        flow_out = random.uniform(98.0, 102.0)
        wob = random.uniform(19.0, 23.0)

    SIMULATION_STATE["rop_m_hr"] = round(rop, 1)
    SIMULATION_STATE["wob_klbs"] = round(wob, 1)
    SIMULATION_STATE["torque_kft_lbs"] = round(torque, 1)
    SIMULATION_STATE["standpipe_pressure_psi"] = round(pressure, 0)
    SIMULATION_STATE["flow_out_pct"] = round(flow_out, 1)

    return TelemetryTick(
        tick_index=t,
        timestamp=datetime.utcnow().isoformat(),
        depth_md=round(curr_md, 2),
        depth_tvd=round(SIMULATION_STATE["depth_tvd"], 2),
        rop_m_hr=SIMULATION_STATE["rop_m_hr"],
        wob_klbs=SIMULATION_STATE["wob_klbs"],
        torque_kft_lbs=SIMULATION_STATE["torque_kft_lbs"],
        standpipe_pressure_psi=SIMULATION_STATE["standpipe_pressure_psi"],
        mud_weight_in_ppg=SIMULATION_STATE["mud_weight_ppg"],
        flow_out_pct=SIMULATION_STATE["flow_out_pct"],
        active_formation=formation
    )

@router.get("/tick", response_model=TelemetryEvaluationResponse)
def get_current_telemetry_tick(db: Session = Depends(get_db)):
    """Advances one telemetry step and evaluates live ML risk against offset hazard memory."""
    tick = advance_simulation_tick()
    hazards = db.query(DrillingHazard).all()
    return risk_engine.evaluate_live_telemetry(tick, hazards)

@router.get("/stream")
async def stream_live_telemetry():
    """
    Server-Sent Events (SSE) streaming endpoint simulating real-time eRTMAC
    telemetry ticks and hybrid ML risk evaluations every 1.5 seconds.
    """
    async def event_generator():
        db = SessionLocal()
        try:
            hazards = db.query(DrillingHazard).all()
            while True:
                tick = advance_simulation_tick()
                eval_res = risk_engine.evaluate_live_telemetry(tick, hazards)
                yield f"data: {eval_res.json()}\n\n"
                await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            pass
        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/reset")
def reset_simulation(depth_md: float = 2320.0, mud_weight: float = 10.4):
    """Resets the eRTMAC simulated drillstring to a specified depth and mud weight."""
    SIMULATION_STATE["tick"] = 0
    SIMULATION_STATE["depth_md"] = depth_md
    SIMULATION_STATE["depth_tvd"] = depth_md * 0.98
    SIMULATION_STATE["mud_weight_ppg"] = mud_weight
    return {
        "message": f"eRTMAC telemetry simulation reset to {depth_md} m MD ({mud_weight} ppg).",
        "current_state": SIMULATION_STATE
    }

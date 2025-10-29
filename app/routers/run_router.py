from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.services.compile_service import setup_workspace
from app.services.run_service import run_robot_and_get_report
from app.core.utils_sse import stream_progress
from urllib.parse import urljoin
import asyncio
from pathlib import Path

router = APIRouter(prefix="/api/v1", tags=["run"])

@router.get("/run-test-case/{testName}/stream")
async def run_stream(request: Request, testName: str):
    root, gen, rep = setup_workspace(testName)
    if not gen.exists() or not any(gen.glob("*.robot")):
        raise HTTPException(status_code=404, detail="no generated tests found")

    base_url = str(request.base_url).rstrip("/")
    
    async def event_gen():
        # Discover test cases
        cases = [p.stem for p in gen.glob("*.robot")]
        
        # Run robot tests in background and capture timestamp
        out_dir, logs, timestamp = await asyncio.to_thread(run_robot_and_get_report, gen, rep)
        
        # Stream progress with timestamp in final download URL
        download_base = urljoin(base_url + "/", f"api/v1/download/{testName}")
        async for chunk in stream_progress(cases, final_url=download_base, timestamp=timestamp):
            yield chunk

    return StreamingResponse(event_gen(), media_type="text/event-stream")

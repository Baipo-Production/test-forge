import asyncio, json
from typing import AsyncGenerator, Dict, Any

async def sse_event(event: str, data: Dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def stream_progress(sim_cases, final_url: str, timestamp: str = None) -> AsyncGenerator[str, None]:
    """
    Stream SSE progress events.
    
    Args:
        sim_cases: List of test case names
        final_url: Base download URL (will append timestamp if provided)
        timestamp: Optional timestamp to append to download URL
    """
    for case in sim_cases:
        yield await sse_event("progress", {"case": case, "status": "running"})
        await asyncio.sleep(0.5)
        yield await sse_event("progress", {"case": case, "status": "passed"})
        await asyncio.sleep(0.2)
    
    # Build final download URL with timestamp if available
    download_url = f"{final_url}/{timestamp}" if timestamp else final_url
    
    summary = {"total": len(sim_cases), "passed": len(sim_cases), "failed": 0}
    yield await sse_event("done", {"summary": summary, "download_url": download_url})

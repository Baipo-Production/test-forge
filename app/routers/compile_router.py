from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from app.services.compile_service import setup_workspace, generate_robot_cases_from_excel
from app.core.config import STORAGE_PATH
from pathlib import Path
import shutil

router = APIRouter(prefix="/api/v1", tags=["compile"])

@router.post("/compile-test-case")
async def compile_test_case(testName: str = Body(..., embed=True), file: UploadFile = File(...)):
    try:
        root, gen, rep = setup_workspace(testName)
        raw_path = root / "rawData.xlsx"
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="empty file")
        raw_path.write_bytes(content)
        tests = generate_robot_cases_from_excel(raw_path, gen)
        return {"status": "compiled", "testName": testName, "cases": len(tests),
                "run_url": f"/api/v1/run-test-case/{testName}/stream"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"compile error: {e}")

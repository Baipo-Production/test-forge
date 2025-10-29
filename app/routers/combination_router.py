from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.services.combination_service import build_combination_excel
import io

router = APIRouter(prefix="/api/v1", tags=["combination"])

@router.post("/combination-test-case")
async def combination_test_case(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty file")
    try:
        data = build_combination_excel(content, file.filename or "input.xlsx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"process error: {e}")
    headers = {"Content-Disposition": 'attachment; filename="combination_testcases.xlsx"'}
    return StreamingResponse(io.BytesIO(data),
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers=headers)

import os
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from errors import handle_errors
from server_h import get_db


test_router = APIRouter(tags=["Testing Automation"])
CLEANUP_TOKEN = os.getenv("TEST_CLEANUP_TOKEN")
    
    
@test_router.post("/app/cleanup", status_code=200)
async def cleanup_test_logs(in_token:str = Header(...), db:AsyncSession= Depends(get_db)):
     
    if not CLEANUP_TOKEN or in_token != CLEANUP_TOKEN:
        raise HTTPException(
            status_code = 401,
            detail="Unauthorized cleanup requested."
        )
    try:
        await db.execute(text("DELETE FROM logs WHERE ldb_cl_name LIKE 'Stress_test_%'"))
        await db.commit()
    except Exception as e:
        print(f"Failed to add entry into the Database. Error Type: {type(e).__name__} - {e}")
        handle_errors(e)
    
    return {"status": "Database cleared of test logs."}
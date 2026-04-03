from fastapi.exceptions import RequestValidationError,HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from sqlalchemy.exc import ProgrammingError

async def log_validation_exc_handler(request:Request, exc: RequestValidationError):
    message = "Incorrect format for one of the fields"
    return JSONResponse(status_code=422, content=message)

def handle_errors(e):
    if isinstance(e, RequestValidationError):
        raise
    elif isinstance(e,ProgrammingError):
        raise HTTPException(status_code=500, detail="Failed to add entry to the database")
    else:
        msg = f"Error Type: {type(e).__name__} - {e}"
        print(msg)
        raise HTTPException(status_code=500, detail=msg)


from fastapi.exceptions import RequestValidationError,HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from sqlalchemy.exc import ProgrammingError,InterfaceError

# If you want custom messages 
async def log_validation_exc_handler(request:Request, exc: RequestValidationError):
    message = "Incorrect format/fieldname for one of the fields"
    raise HTTPException(status_code=422, detail=message)

def handle_errors(e):
    if isinstance(e,ProgrammingError):
        raise
    elif isinstance(e, InterfaceError):
        msg = f"Error Type: {type(e).__name__} - {e}. Internal interface error."
        print(msg)
        raise HTTPException(status_code=500, detail=msg)
    else:
        msg = f"Error Type: {type(e).__name__} - {e}"
        print(msg)
        raise HTTPException(status_code=500, detail=msg)


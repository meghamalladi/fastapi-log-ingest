# Log ingestion server
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from dotenv import load_dotenv
load_dotenv()

from validation_class import User_log
from database import LogRecord, SessionLocal, Base,engine
from datetime import datetime
from errors import handle_errors, log_validation_exc_handler

app = FastAPI(
    title="Log ingestion server",
    description="A server that takes,transforms and stores incoming traffic",
    version="1.0.0",
)
app.add_exception_handler(RequestValidationError, log_validation_exc_handler)

# Create all the tables associated with the required database.
try:
    Base.metadata.create_all(engine)
except Exception as e:
    print(f"Error: Could not connect to the database or create tables. {e}")
    handle_errors(e)

@app.get("/")
def init():
    return {"message":"Server is up!"}

# Database session dependency for all the webrequests that require it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# in_log = User_log()  send in the actual data?
# We need database operation in this case; Hence the async method.
@app.post("/ingest")
def ingest(inlog:User_log, db:Session = Depends(get_db)):
    curr_time = datetime.now()
    new_entry = LogRecord()
    
    # Copy new values to the new entry
    new_entry.ldb_cl_name = inlog.usr_cl_name
    new_entry.ldb_level = inlog.usr_level
    new_entry.ldb_cl_ts = curr_time
    new_entry.ldb_msg = inlog.usr_msg

    print(inlog.usr_cl_name,inlog.usr_level, curr_time, inlog.usr_msg)

    try:
        db.add(new_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to add entry into the Database. Error Type: {type(e).__name__} - {e}")
        handle_errors(e)
        
    print(f"Data entry added. id: {new_entry.ldb_cl_name}")
    return {"status": "Success. Data has been ingested."} 
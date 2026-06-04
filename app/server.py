# Log ingestion server
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# We don't need load_dotenv if we are running Docker. We use .env information in the docker-compose yml file.
# Use the function only if we are not using docker for any reason
#from dotenv import load_dotenv
#load_dotenv("../.env")

from database import LogRecord
from server_h import lifespan, get_db, load_dependency
from validation_class import User_log
from errors import handle_errors


# Create our app
app = FastAPI(
    title="Log ingestion server",
    description="A server that takes,transforms and stores incoming traffic",
    version="1.0.0",
    lifespan = lifespan
)

# Load all dependencies
load_dependency(app)


@app.get("/")
def init():
    return {"message":"Server is up!"}


# in_log = User_log()  send in the actual data?
# We need database operation in this case; Hence the async method.
@app.post("/ingest")
async def ingest(inlog:User_log, db:AsyncSession = Depends(get_db)):
    new_entry = LogRecord()
    
    # Copy new values to the new entry
    new_entry.ldb_cl_name = inlog.usr_cl_name
    new_entry.ldb_level = inlog.usr_level
    new_entry.ldb_cl_ts = inlog.usr_cl_ts
    new_entry.ldb_msg = inlog.usr_msg

    try:
        db.add(new_entry)
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Failed to add entry into the Database. Error Type: {type(e).__name__} - {e}")
        handle_errors(e)
        
    print(f"Data entry added. id: {inlog.usr_cl_name}, request time: {inlog.usr_cl_ts}")
    return {"status": "Success. Data has been ingested."} 


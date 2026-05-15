import os, sys
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from errors import log_validation_exc_handler
from database import Base

# url: address of the database
db_url = os.getenv("DATABASE_URL")

if not db_url:
    # There is no database to proceed with. Fail immediately. 
    print("DATABASE_URL env variable is not set!")
    print("Correct format: postgresql+asyncpg://<usr>:<pwd>@host/db_name")
    sys.exit(1)

# Engine: Object that establishes connection to db and manages pool of db connections
try:
    engine = create_async_engine(db_url,pool_size=20, max_overflow=30, pool_timeout=60)
except Exception as e:
    print(f"Could not connect to the database. Check URL")
    print(f"Error Type: {type(e).__name__} - {e}")
    sys.exit(1)
print("Database engine created succesfully.\n")

# SessionLocal is the sqlalchemy session that managers db transactions
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    try:
        async with engine.begin() as conn:
            # create_all is a sync method, therefore, we need a sync handler run_sync
            await conn.run_sync(Base.metadata.create_all) 
    except Exception as e:
        print(f"Error: Could not connect to the database or create tables. {e}")
        print(f"Error Type: {type(e).__name__} - {e}")
        sys.exit(f"Error: Could not connect to the database or create tables. {e}")

# Start and end routines for the app.
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Startup phase: Connect to the database
    # If yes, create all required tables   

    await init_db()
    print("Connected to the database, and created tables.")

    # Yield control for the app to to its thing
    yield

    # Shutdown phase: Dispose the database engine
    await engine.dispose()
    print("Database Engine disposed.") 

def load_dependency(app:FastAPI):
    # Add all required handlers
    app.add_exception_handler(RequestValidationError, log_validation_exc_handler)
    

# Database session dependency for all the webrequests that require it.
async def get_db():
    # Similar to try/finally with await
    async with AsyncSessionLocal() as db:
        yield db

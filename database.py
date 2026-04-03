from sqlalchemy import create_engine, Column, Integer, String,DateTime, func
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy_utils import database_exists, create_database
import os

# url: address of the database
# Engine: Object that establishes connection to db and manages pool of db connections

try:
    db_url = os.getenv("DATABASE_URL","postgresql://<user>:<password>@<localhost>/<db>")
    engine = create_engine(db_url)
except Exception as e:
    print(f"Could not connect to the database. Check URL")
    print(f"Error Type: {type(e).__name__} - {e}")
    raise HTTPException(status_code=500)

if not database_exists(engine.url):
    try:
        create_database(engine.url)
    except Exception as e:
        print(f"Could not create the database.")
        print(f"Error Type: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500)

print("Database engine created succesfully.\n")

# SessionLocal is the sqlalchemy session that managers db transactions
SessionLocal = sessionmaker(bind=engine)

# We create a Base class for creating database tables. 
class Base(DeclarativeBase):
    pass

class LogRecord(Base):
    __tablename__ = "logs"
    
    ldb_id = Column(Integer, primary_key = True, index=True, autoincrement=True)
    ldb_cl_name = Column(String, index=True)
    ldb_level = Column(String)
    ldb_cl_ts = Column(DateTime)
    ldb_ts = Column(DateTime, server_default=func.now(), index=True)
    ldb_msg = Column(String)




    
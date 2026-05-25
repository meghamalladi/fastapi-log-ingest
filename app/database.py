from sqlalchemy import Column, Integer, String,DateTime, func
from sqlalchemy.orm import DeclarativeBase

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




    
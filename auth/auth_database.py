from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base
import os


MYSQL_USER= os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootpassword")
MYSQL_HOST= os.getenv("MYSQL_HOST", "db")
MYSQL_PORT= os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE= os.getenv("MYSQL_DATABASE", "fast_api_db")

DATABASE_URL= f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# connection

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)


#session
sessionLocal = sessionmaker(autoflush=False, autocommit= False, bind=engine)

def get_db():
    db = sessionLocal()

    try:
        yield db
    finally:
        db.close()

# Base
base = declarative_base()

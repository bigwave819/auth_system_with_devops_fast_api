from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base


MYSQL_USER= "root"
MYSQL_PASSWORD=""
MYSQL_HOST="localhost"
MYSQL_PORT= "3306"
MYSQL_DATABASE= "fast_api"

DATABASE_URL= f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# connection

engine = create_engine

#session
sessionLocal = sessionmaker(autoflush=False, autocommit= False, bind=engine)

def get_db():
    db = sessionLocal()

    try:
        yield db
    except:
        db.close()

# Base
base = declarative_base()

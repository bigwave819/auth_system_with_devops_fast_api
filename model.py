from sqlalchemy import Integer, Column, VARCHAR
from database import Base

class book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(VARCHAR(255))
    author = Column(VARCHAR(255))
    publish_date = Column(VARCHAR(255))
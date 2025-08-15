from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    discord_id = Column(BigInteger, primary_key=True)
    steam_id = Column(String(17), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(String(3), nullable=False)
    crime = Column(String(200), nullable=False)
    sentence = Column(String(50), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

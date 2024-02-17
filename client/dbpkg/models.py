from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserInfo(Base):
    __tablename__ = "user_info"

    fid = Column(String(10), nullable=False, primary_key=True)
    uid = Column(String(10), nullable=False)
    name = Column(String(20), nullable=False)
    rank4 = Column(Integer, nullable=False)
    point4 = Column(Integer, nullable=False)
    rank3 = Column(Integer, nullable=False)
    point3 = Column(Integer, nullable=False)
    last_update = Column(DateTime, nullable=False)

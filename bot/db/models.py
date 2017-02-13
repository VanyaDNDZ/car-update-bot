from sqlalchemy import Column, TEXT, DATE
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Cars(Base):
    __tablename__ = 'cars'
    id = Column(TEXT, primary_key=True)
    base_url = Column(TEXT)
    url = Column(TEXT)
    desc = Column(TEXT)
    price = Column(TEXT)
    gear = Column(TEXT)
    year = Column(TEXT)
    mileage = Column(TEXT)
    update_dt = Column(DATE)


class Subscribers(Base):
    __tablename__ = 'subscribers'
    chat_id = Column(TEXT, primary_key=True)
    is_active = Column(TEXT, default='t')

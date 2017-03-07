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


class StagingCars(Base):
    __tablename__ = 'staging_cars'
    id = Column(TEXT, primary_key=True)
    base_url = Column(TEXT)
    url = Column(TEXT)
    desc = Column(TEXT)
    price = Column(TEXT)
    gear = Column(TEXT)
    year = Column(TEXT)
    mileage = Column(TEXT)
    update_dt = Column(DATE)


class RemovedCars(Base):
    __tablename__ = 'removed_cars'
    id = Column(TEXT, primary_key=True)
    base_url = Column(TEXT)
    url = Column(TEXT)
    desc = Column(TEXT)
    price = Column(TEXT)
    gear = Column(TEXT)
    year = Column(TEXT)
    mileage = Column(TEXT)
    update_dt = Column(DATE)
    deletion_dt = Column(DATE, primary_key=True)


class Subscribers(Base):
    __tablename__ = 'subscribers'
    chat_id = Column(TEXT, primary_key=True)
    is_active = Column(TEXT, default='t')

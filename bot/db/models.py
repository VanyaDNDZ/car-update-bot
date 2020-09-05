import datetime

from sqlalchemy import Column, TEXT, DATE, Integer, Sequence, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Cars(Base):
    __tablename__ = "cars"
    id = Column(TEXT, primary_key=True)
    base_url = Column(TEXT)
    url = Column(TEXT)
    desc = Column(TEXT)
    price = Column(TEXT)
    gear = Column(TEXT)
    year = Column(TEXT)
    mileage = Column(TEXT)
    car_plate = Column(TEXT)
    vin = Column(TEXT)
    update_dt = Column(DATE)


class StagingCars(Base):
    __tablename__ = "staging_cars"
    id = Column(TEXT, primary_key=True)
    base_url = Column(TEXT)
    url = Column(TEXT)
    desc = Column(TEXT)
    price = Column(TEXT)
    gear = Column(TEXT)
    year = Column(TEXT)
    mileage = Column(TEXT)
    car_plate = Column(TEXT)
    vin = Column(TEXT)
    update_dt = Column(DATE)


class CarsHistory(Base):
    __tablename__ = "cars_history"
    update_id = Column(TEXT, primary_key=True)
    id = Column(TEXT)
    base_url = Column(TEXT)
    url = Column(TEXT)
    desc = Column(TEXT)
    price = Column(TEXT)
    gear = Column(TEXT)
    year = Column(TEXT)
    mileage = Column(TEXT)
    car_plate = Column(TEXT)
    vin = Column(TEXT)
    update_dt = Column(TIMESTAMP)


class RemovedCars(Base):
    __tablename__ = "removed_cars"
    id = Column(TEXT, primary_key=True)
    base_url = Column(TEXT)
    url = Column(TEXT)
    desc = Column(TEXT)
    price = Column(TEXT)
    gear = Column(TEXT)
    year = Column(TEXT)
    mileage = Column(TEXT)
    car_plate = Column(TEXT)
    vin = Column(TEXT)
    update_dt = Column(DATE)
    deletion_dt = Column(DATE, primary_key=True)


class CarsToQuery(Base):
    __tablename__ = "cars_to_query"
    car_id = Column(TEXT, primary_key=True)
    query_id = Column(TEXT)


class Bags(Base):
    __tablename__ = "bags"
    row_id = Column(Integer, Sequence('bags_id_seq'))
    url = Column(TEXT, primary_key=True)
    name = Column(TEXT)
    discount_price = Column(TEXT)
    base_price = Column(TEXT)
    chat_id = Column(TEXT)
    history = relationship("BagsPriceHistory")


class StagingBags(Base):
    __tablename__ = "staging_bags"
    url = Column(TEXT, primary_key=True)
    name = Column(TEXT)
    discount_price = Column(TEXT)
    base_price = Column(TEXT)
    update_dt = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class BagsPriceHistory(Base):
    __tablename__ = "bags_price_history"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    bag_id = Column(Integer)
    url = Column(TEXT, ForeignKey("bags.url"))
    discount_price = Column(TEXT)
    base_price = Column(TEXT)
    update_dt = Column(TIMESTAMP, default=datetime.datetime.utcnow)


class Subscribers(Base):
    __tablename__ = "subscribers"
    chat_id = Column(TEXT, primary_key=True)
    is_active = Column(TEXT, default="t")

import datetime
import logging
from contextlib import closing
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import or_, desc
from sqlalchemy.sql.functions import func

from bot.db.models import Cars, StagingCars, CarsHistory
from .engine import get_session

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_cars(days=0, filters=None):
    with closing(get_session()) as session:
        q = session.query(Cars)
        q = q.filter(Cars.update_dt >= datetime.date.today() - timedelta(days=days))
        cars = q.order_by(Cars.id).all()

        return cars


def get_cars_by_plate(plate):
    with closing(get_session()) as session:
        q = session.query(Cars)
        q = q.filter(Cars.car_plate == plate)
        cars = q.order_by(Cars.id).all()
        return cars


def get_car_history_by_plate(plate):
    with closing(get_session()) as session:
        q = session.query(CarsHistory)
        q = q.filter(CarsHistory.car_plate == plate)
        cars = q.order_by(desc(CarsHistory.update_dt)).all()
        return cars


def get_cars_by_vin(vin):
    filter_query = Cars.vin == vin
    if "XXXX" in vin:
        filter_query = Cars.vin.like(vin.replace("X", "_"))

    with closing(get_session()) as session:
        q = session.query(Cars)
        q = q.filter(filter_query)
        cars = q.order_by(Cars.id).all()
        return cars


def get_car_history_by_vin(vin):
    filter_query = CarsHistory.vin == vin
    if "XXXX" in vin:
        filter_query = CarsHistory.vin.like(vin.replace("X", "_"))

    with closing(get_session()) as session:
        q = session.query(CarsHistory)
        q = q.filter(filter_query)
        cars = q.order_by(desc(CarsHistory.update_dt)).all()
        return cars


def get_filtered(q_filter, order):
    with closing(get_session()) as session:
        q = session.query(Cars)
        q = q.filter(*q_filter)
        cars = q.order_by(*order).all()

        return cars


def update_car(car_iterator):
    added_ids = []
    with closing(get_session()) as session:
        session.query(StagingCars).delete()
        for item in car_iterator:
            session.merge(StagingCars(**item, update_dt=datetime.date.today()))
        session.flush()

        for updated_car in (
                session.query(Cars)
                        .join(StagingCars, Cars.id == StagingCars.id)
                        .filter(
                    or_(
                        Cars.vin != StagingCars.vin,
                        Cars.car_plate != StagingCars.car_plate,
                        Cars.mileage != StagingCars.mileage,
                        Cars.price != StagingCars.price,
                    )
                )
        ):
            session.add(
                CarsHistory(
                    update_id=str(uuid4()),
                    id=updated_car.id,
                    base_url=updated_car.base_url,
                    url=updated_car.url,
                    desc=updated_car.desc,
                    price=updated_car.price,
                    gear=updated_car.gear,
                    year=updated_car.year,
                    mileage=updated_car.mileage,
                    car_plate=updated_car.car_plate,
                    vin=updated_car.vin,
                    update_dt=datetime.datetime.now(),
                )
            )
        session.flush()

        for updated_car in (
                session.query(StagingCars).join(Cars, Cars.id == StagingCars.id).all()
        ):
            session.merge(
                Cars(
                    id=updated_car.id,
                    base_url=updated_car.base_url,
                    url=updated_car.url,
                    desc=updated_car.desc,
                    price=updated_car.price,
                    gear=updated_car.gear,
                    year=updated_car.year,
                    mileage=updated_car.mileage,
                    car_plate=updated_car.car_plate,
                    vin=updated_car.vin,
                    update_dt=datetime.date.today(),
                )
            )
        session.flush()

        for new_car in (
                session.query(StagingCars)
                        .outerjoin(Cars, Cars.id == StagingCars.id)
                        .filter(Cars.id == None)
                        .all()
        ):
            session.add(
                Cars(
                    id=new_car.id,
                    base_url=new_car.base_url,
                    url=new_car.url,
                    desc=new_car.desc,
                    price=new_car.price,
                    gear=new_car.gear,
                    year=new_car.year,
                    mileage=new_car.mileage,
                    car_plate=new_car.car_plate,
                    vin=new_car.vin,
                    update_dt=datetime.date.today(),
                )
            )
        session.commit()
    return added_ids


def get_stats():
    with closing(get_session()) as session:
        return (
            session.query(Cars.base_url, Cars.gear, func.count(Cars.base_url))
                .group_by(Cars.base_url, Cars.gear)
                .all()
        )

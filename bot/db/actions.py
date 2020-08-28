import datetime
import logging
from contextlib import closing
from datetime import timedelta

from sqlalchemy.sql.functions import func

from bot.db.models import Cars, Subscribers, StagingCars, RemovedCars
from .engine import get_session

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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


def get_cars_by_vin(vin):
    filter_query = Cars.vin == vin
    if "XXXX" in vin:
        filter_query = Cars.vin.like(vin.replace("X", "_"))

    with closing(get_session()) as session:
        q = session.query(Cars)
        q = q.filter(filter_query)
        cars = q.order_by(Cars.id).all()
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
        for new_car in session.query(StagingCars).outerjoin(Cars, Cars.id == StagingCars.id).filter(
                Cars.id == None).all():
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
                    update_dt=datetime.date.today()
                )
            )
        session.flush()
        session.commit()
    return added_ids


def save_subscribe(chat_id: str) -> bool:
    with closing(get_session()) as session:
        sub = session.query(Subscribers).filter(Subscribers.chat_id == chat_id).first()
        if not sub:
            session.add(Subscribers(chat_id=chat_id, is_active='t'))
            status = 'added'
        elif sub.is_active == 'f':
            sub.is_active = 't'
            session.add(sub)
            status = 're-activated'
        else:
            status = 'already active'
        session.flush()
        session.commit()
    return status


def save_unsubscribe(chat_id: str) -> bool:
    with closing(get_session()) as session:
        sub = session.query(Subscribers).filter(Subscribers.chat_id == chat_id).first()
        if not sub:
            status = 'no sub'
        elif sub.is_active == 't':
            sub.is_active = 'f'
            session.add(sub)
            status = 'deactivated'
        else:
            status = 'no sub'
        session.flush()
        session.commit()
    return status


def get_subscribers():
    with closing(get_session()) as session:
        sub = session.query(Subscribers).filter(Subscribers.is_active == 't').all()
    return sub


def create_query(car_ids: list) -> tuple:
    return {"filter": (Cars.id.in_(car_ids),), "order": (Cars.id,)}


def get_stats():
    with closing(get_session()) as session:
        return session.query(Cars.base_url, Cars.gear, func.count(Cars.base_url)).group_by(Cars.base_url,
                                                                                           Cars.gear).all()

import datetime
import logging
from contextlib import closing
from datetime import timedelta

from sqlalchemy.sql.functions import func

from bot.db.models import Cars, Subscribers
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


def get_filtered(q_filter, order):
    with closing(get_session()) as session:
        q = session.query(Cars)
        q = q.filter(*q_filter)
        cars = q.order_by(*order).all()

        return cars


def update_car(car_iterator):
    added_ids = []
    with closing(get_session()) as session:
        for item in car_iterator:
            item.pop("_type", None)
            car = session.query(Cars).filter(Cars.id == item['id']).first()
            if not car:
                added_ids.append(item['id'])
                session.add(Cars(**item, update_dt=datetime.date.today()))
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

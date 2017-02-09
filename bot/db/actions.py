import datetime
import logging
from contextlib import closing
from datetime import timedelta

from sqlalchemy.sql.functions import func

from bot.db.models import Cars
from .engine import get_session

logger = logging.getLogger(__name__)


def get_cars(days=0, filters=None):
    with closing(get_session()) as session:
        q = session.query(Cars)
        q = q.filter(Cars.update_dt >= datetime.date.today() - timedelta(days=days))
        cars = q.order_by(Cars.id).all()

        return cars


def update_car(item):
    item.pop("_type", None)
    with closing(get_session()) as session:

        car = session.query(Cars).filter(Cars.id == item['id']).first()

        if not car:
            try:
                session.add(Cars(**item, update_dt=datetime.date.today()))
                session.flush()
                session.commit()
            except Exception as e:
                logger.error(e)
                raise e

        return car


def get_stats():
    with closing(get_session()) as session:
        return session.query(Cars.base_url, Cars.gear, func.count(Cars.base_url)).group_by(Cars.base_url,
                                                                                           Cars.gear).all()

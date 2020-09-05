import datetime
import logging
from contextlib import closing
from uuid import uuid4

from sqlalchemy import or_, desc, and_

from bot.db.models import Cars, StagingCars, CarsHistory, CarsToQuery, StagingBags, Bags, BagsPriceHistory
from .engine import get_session

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_or_create_query_id(car_id):
    with closing(get_session()) as session:
        q = session.query(CarsToQuery)
        q = q.filter(CarsToQuery.car_id == car_id)
        result = q.all()
        if result:
            return result[0].query_id
        query_id = str(uuid4().int)
        session.add(CarsToQuery(car_id=car_id, query_id=query_id))
        session.flush()
        session.commit()
        return query_id


def get_car_id_by_query_id(query_id):
    with closing(get_session()) as session:
        q = session.query(CarsToQuery)
        q = q.filter(CarsToQuery.query_id == query_id)
        result = q.all()
        if result:
            return result[0].car_id
        return None


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


def get_car_history_by_id(car_id):
    with closing(get_session()) as session:
        q = session.query(CarsHistory)
        q = q.filter(CarsHistory.id == car_id)
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


def update_bags(bag_iterator):
    added_ids = []
    with closing(get_session()) as session:
        session.query(StagingBags).delete()
        for item in bag_iterator:
            session.merge(StagingBags(**item))
        session.flush()

        for first_updated in session.query(
                StagingBags, Bags.chat_id, Bags.row_id
        ).join(Bags, and_([Bags.url == StagingBags.url, Bags.name.is_(None)])):
            session.merge(
                Bags(
                    row_id=first_updated.row_id,
                    name=first_updated.name,
                    url=first_updated.url,
                    discount_price=first_updated.discount_price,
                    base_price=first_updated.base_price,
                    chat_id=first_updated.chat_id
                )
            )

        for updated_bag in session.query(Bags).join(
                Bags, and_([Bags.url == StagingBags.url, Bags.name.isnot(None), or_(
                    StagingBags.base_price != Bags.base_price,
                    StagingBags.discount_price != Bags.discount_price,
                )])):
            added_ids.append(updated_bag.row_id)
            session.add(
                BagsPriceHistory(
                    bag_id=updated_bag.row_id,
                    url=updated_bag.url,
                    discount_price=updated_bag.discount_price,
                    base_price=updated_bag.base_price,
                    name=updated_bag.name,
                )
            )

        for updated_bag in session.query(
                StagingBags, Bags.chat_id, Bags.row_id
        ).join(Bags, and_([Bags.url == StagingBags.url, Bags.name.isnot(None), or_(
            StagingBags.base_price != Bags.base_price,
            StagingBags.discount_price != Bags.discount_price,
        )])):
            added_ids.append(updated_bag.row_id)
            session.merge(
                Bags(
                    row_id=updated_bag.row_id,
                    name=updated_bag.name,
                    url=updated_bag.url,
                    discount_price=updated_bag.discount_price,
                    base_price=updated_bag.base_price,
                    chat_id=updated_bag.chat_id
                )
            )

        session.commit()

    return added_ids


def add_bag(chat_id, url):
    with closing(get_session()) as session:
        session.add(
            Bags(

                chat_id=chat_id,
                url=url
            )
        )
        session.commit()


def get_bags_for_chat(chat_id):
    with closing(get_session()) as session:
        q = session.query(Bags)
        q = q.filter(Bags.chat_id == chat_id)
        return q.order_by(desc(Bags.row_id)).all()


def delete_subscription(bag_id):
    with closing(get_session()) as session:
        session.query(BagsPriceHistory).filter(and_(BagsPriceHistory.bag_id == bag_id)).delete()
        session.query(Bags).filter(and_(Bags.row_id == bag_id)).delete()
        session.commit()


def get_url_to_parse():
    with closing(get_session()) as session:
        q = session.query(Bags.url)
        return [el.url for el in q.order_by(desc(Bags.row_id)).all()]

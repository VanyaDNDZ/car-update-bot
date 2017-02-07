import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session

from ..config import get_config


def get_engine():
    config = get_config()
    db_url = config['DBCONFIG']['DB_URL']
    db_url = db_url.format(os.environ.get('PG_PASS', 'PASSWORD'), os.environ.get('PG_URL', 'fspostgres'))
    return create_engine(db_url)


def get_session() -> session:
    return sessionmaker(bind=get_engine())()

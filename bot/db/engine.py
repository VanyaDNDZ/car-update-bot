from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session

from ..config import get_config

ENGINE = None


def get_engine():
    config = get_config()
    db_url = config["DATABASE_URL"]
    return create_engine(db_url)


def get_session() -> session:
    global ENGINE
    if ENGINE is None:
        ENGINE = get_engine()
    return sessionmaker(bind=ENGINE)()

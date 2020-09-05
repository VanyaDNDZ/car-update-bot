from bot.bags_message_handler import run_chat_bot as bags_bot
from bot.config import load_config
from bot.db.engine import get_engine
from bot.db.models import Base
from bot.message_handler import run_chat_bot
from bot.webapp import app
from multiprocessing import Process
import os


def start_car_bot():
    load_config()
    Base.metadata.create_all(get_engine())
    run_chat_bot()


def start_bags_bot():
    load_config()
    Base.metadata.create_all(get_engine())
    bags_bot()


def start_app():
    load_config()
    app.run(host="0.0.0.0", port=os.getenv("PORT"))


if __name__ == "__main__":
    p1 = Process(target=start_car_bot)
    p2 = Process(target=start_bags_bot)
    p1.start()
    p2.start()
    start_app()

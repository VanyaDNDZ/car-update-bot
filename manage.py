from bot.config import load_config
from bot.db.engine import get_engine
from bot.db.models import Base
from bot.message_handler import run_chat_bot


def start_bot():
    load_config()
    Base.metadata.create_all(get_engine())
    run_chat_bot()


if __name__ == "__main__":
    start_bot()

import sys

import click
from scrapy.cmdline import execute

from bot.config import load_config
from bot.db.engine import get_engine
from bot.db.models import Base
from bot.message_handler import run_chat_bot


def start_bot():
    click.echo("Start bot")
    load_config()
    click.echo("Config loaded")
    Base.metadata.create_all(get_engine())
    click.echo("Models created")
    run_chat_bot()


if __name__ == "__main__":
    if sys.argv[1] == "start_bot":
        start_bot()
    else:
        execute(sys.argv[:])

import configparser
import os

CONFIG = {}


def load_config():
    global CONFIG
    if not CONFIG:
        config = {}
        config["DATABASE_URL"] = os.getenv("DATABASE_URL")
        config["SHUB_API_KEY"] = os.getenv("SHUB_API_KEY")
        config["SHUB_PROJECT_ID"] = os.getenv("SHUB_PROJECT_ID")
        config["BOT_TOKEN"] = os.getenv("BOT_TOKEN")
        config["BAGS_BOT_TOKEN"] = os.getenv("BAGS_BOT_TOKEN")
        CONFIG = config


def get_config():
    return CONFIG

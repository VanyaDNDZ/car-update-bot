import configparser
import os

CONFIG = None


def load_config():
    global CONFIG
    if not CONFIG:
        config = configparser.ConfigParser()
        config_file = os.environ.get('CONFIG_FILE', 'config.ini')
        current_dir = os.path.dirname(__file__)
        if os.path.exists(os.path.join(current_dir, '..', config_file)):
            config.read(os.path.join(current_dir, '..', config_file))
        CONFIG = config


def get_config():
    return CONFIG

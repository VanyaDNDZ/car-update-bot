from setuptools import setup, find_packages


requires = [
    'sqlalchemy',
    'psycopg2-binary',
    'requests',
    'click>=6',
    'scrapinghub',
    'python-telegram-bot',
]

setup(
    name="car-bot",
    author="VanyaDNDZ",
    description="Telegram bot",
    version="0.1",
    install_requires=requires,
    packages=find_packages(),
    entry_points={"scrapy": ["settings = carinfo.settings"]},
    extras_require={
        'test': ['pytest-cov', 'flake8', 'pytest'],
        'bot': requires
    }

)

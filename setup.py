from setuptools import setup, find_packages

requires = [
    'scrapy',

]

telegram_requires = [
    'sqlalchemy',
    'pg8000',
    'requests',
    'click>=6',
    'scrapinghub',
    'python-telegram-bot',
]

setup(
    author="VanyaDNDZ",
    description="Simple scrapy tool with telegram ui",
    version="0.1",
    install_requires=requires,
    packages=find_packages(),
    entry_points={"scrapy": ["settings = carinfo.settings"]}

)


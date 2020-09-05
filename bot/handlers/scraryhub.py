from scrapinghub import Connection, ScrapinghubClient

from bot.config import get_config

scrappers = {"carinfo_hitavto", "carinfo_ais", "carinfo_planeta"}

MAX_RUNS = 10


def upload_iterator(spiders):
    loaded_scrappers = set()
    conn = Connection(get_config()["SHUB_API_KEY"])
    project = conn[int(get_config()["SHUB_PROJECT_ID"])]
    runned = 0
    for job in project.jobs():
        if job.info["spider"] not in spiders:\
            continue
        if runned > MAX_RUNS:
            raise StopIteration()
        if job.info["state"] != "finished":
            continue
        if job.info["spider"] in loaded_scrappers:
            continue
        for item in job.items():
            item.pop("_type", None)
            yield item
        loaded_scrappers.add(job.info["spider"])
        runned += 1


def start_scraping(bot=None, update=None, spider="carinfo_autoria"):
    client = ScrapinghubClient(get_config()["SHUB_API_KEY"])
    project = client.get_project(int(get_config()["SHUB_PROJECT_ID"]))
    spider = project.spiders.get(spider)
    spider.jobs.run()
    print("job run")

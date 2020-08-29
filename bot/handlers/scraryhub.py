from scrapinghub import Connection

from bot.config import get_config

scrappers = {'carinfo_hitavto', 'carinfo_ais', 'carinfo_planeta'}

MAX_RUNS = 10


def upload_iterator():
    loaded_scrappers = set()
    conn = Connection(get_config()['SHUB_API_KEY'])
    project = conn[int(get_config()['SHUB_PROJECT_ID'])]
    runned = 0
    for job in project.jobs():
        if runned > MAX_RUNS:
            raise StopIteration()
        if job.info['state'] != 'finished':
            continue
        if not loaded_scrappers.symmetric_difference(scrappers):
            raise StopIteration()
        if job.info['spider'] in loaded_scrappers:
            continue
        for item in job.items():
            item.pop("_type", None)
            yield item
        loaded_scrappers.add(job.info['spider'])
        runned += 1


def start_scraping():
    conn = Connection(get_config()['SHUB_API_KEY'])
    project = conn[int(get_config()['SHUB_PROJECT_ID'])]
    spider = project.spiders.get('carinfo_autoria')
    spider.jobs.run()
    print("job run")
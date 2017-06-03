from scrapinghub import Connection

from bot.config import get_config

scrappers = {'carinfo_hitavto', 'carinfo_ais', 'carinfo_planeta'}


def upload_iterator():
    loaded_scrappers = set()
    conn = Connection(get_config()['SCRAPYHUB']['token'])
    project = conn[int(get_config()['SCRAPYHUB']['PROJECT_ID'])]
    for job in project.jobs():
        if job.info['state'] != 'finished':
            continue
        if not loaded_scrappers.difference(scrappers):
            raise StopIteration()
        for item in job.items():
            item.pop("_type", None)
            yield item
        loaded_scrappers.add(job.info['spider'])


def clean_scrapyhub_jobs():
    cleaned_cnt = 0
    loaded_scrappers = []
    conn = Connection(get_config()['SCRAPYHUB']['token'])
    project = conn[int(get_config()['SCRAPYHUB']['PROJECT_ID'])]
    for job in project.jobs():
        if job.info['state'] != 'finished':
            continue
        if 'carinfo_ais' not in loaded_scrappers or 'carinfo_planeta' not in loaded_scrappers:
            loaded_scrappers.append(job.info['spider'])
            continue
        job.delete()
        cleaned_cnt += 1
    print("Cleaned {} jobs".format(cleaned_cnt))

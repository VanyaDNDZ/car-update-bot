from scrapinghub import Connection

from bot.config import get_config


def upload_iterator():
    loaded_scrappers = []
    conn = Connection(get_config()['SCRAPYHUB']['token'])
    project = conn[int(get_config()['SCRAPYHUB']['PROJECT_ID'])]
    for job in project.jobs():
        if job.info['state'] != 'finished':
            continue
        if 'carinfo_ais' in loaded_scrappers and 'carinfo_planeta' in loaded_scrappers:
            raise StopIteration()
        for item in job.items():
            item.pop("_type", None)
            yield item
        loaded_scrappers.append(job.info['spider'])


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

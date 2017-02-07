# Scrapy settings for dmoz project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os
import sys
from os.path import dirname

path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(path)

BOT_NAME = 'carinfo'

SPIDER_MODULES = ['carinfo.spiders']
NEWSPIDER_MODULE = 'carinfo.spiders'

ITEM_PIPELINES = {
    'carinfo.pipelines.JsonWithEncodingPipeline': 300,
}

LOG_LEVEL = 'INFO'

DOWNLOAD_DELAY = 1

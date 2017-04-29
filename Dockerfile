FROM vanyadndz/scrapy

ADD . /app

RUN set -x \
     &&  pip3.5 install -e .["bot"]

CMD python manage.py start_bot
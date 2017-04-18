FROM python:3.5-slim

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev libffi-dev --no-install-recommends

COPY . /app
WORKDIR /app
ADD . /app

RUN cd
RUN pip3.5 install -e .

RUN set -x \
	&& pip3 install -e .

CMD python manage.py start_bot



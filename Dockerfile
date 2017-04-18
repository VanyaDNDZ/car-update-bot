FROM python3.5-slim

RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev libffi-dev --no-install-recommends

RUN mkdir app
WORKDIR app
COPY . app

RUN pip3.5 install -Ue .

CMD python manage.py start_bot



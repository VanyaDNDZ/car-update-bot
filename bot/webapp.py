from sanic import Sanic
from sanic.response import json

from bot.db.actions import get_url_to_parse

app = Sanic("App Name")


@app.route("/")
async def get_urls(request):
    return json({"urls": get_url_to_parse()})

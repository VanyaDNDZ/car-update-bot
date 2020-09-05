from sanic import Sanic
from sanic.response import json
import os
from bot.db.actions import get_url_to_parse

app = Sanic("App Name")


@app.route("/")
async def get_urls(request):
    if request.args.get("id") == os.getenv("REQUEST_ID"):
        return json({"urls": get_url_to_parse()})
    return json({"id": "fuck off"})

import os
import logging
from time import time
from quart import Quart, request
from quart.logging import default_handler
from hypercorn.asyncio import serve
from hypercorn.config import Config
from lightbulb import BotApp
import ujson as json


class App():
    app = Quart(__name__,
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')
    logging.getLogger("quart.app").removeHandler(default_handler)

    def __init__(self, bot):
        self.bot = bot
        self.app = App.app

        self.tokens = {}

    def add_token(self, token: str, requester: str, requestee: str, channel: str, expire: float = time()):
        self.tokens[token] = {
            "expire": expire,
            "requester": requester,
            "requestee": requestee,
            "channel": channel
        }

    @app.route('/logtoken/<token>')
    async def logtoken(token):

        if token is None:
            return "400", 400
        if token not in self.tokens.keys():  # pylint: disable=consider-iterating-dictionary
            return "400", 400

        if self.tokens[token].get("expire") < time():
            del self.tokens[token]
            return "400", 400

        return "200", 200

    @app.route('/logs/', methods=["POST"])
    async def get_logs():
        token = request.headers.get("token")

        if token is None:
            return "401", 401
        if token not in self.tokens.keys():  # pylint: disable=consider-iterating-dictionary
            return "401", 401

        if self.tokens[token].get("expire") > time():
            del self.tokens[token]
            return "401", 401

        token = self.tokens[token]
        response = await request.get_json()
        if len(response) == 0:
            return "400", 400
        logs = []
        for key in response.keys():
            logs.append(response[key])
        return "200", 200

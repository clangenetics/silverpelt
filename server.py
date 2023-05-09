import logging
from time import time
from quart import Quart, request
from quart.logging import default_handler


tokens = {}

class App():
    app = Quart(__name__,
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')
    logging.getLogger("quart.app").removeHandler(default_handler)

    bot = None

    def __init__(self, _bot):
        self.bot = _bot
        App.bot = _bot
        self.app = App.app

        self.add_token("test", "174200708818665472", "174200708818665472", "1095692751598780526")

    def add_token(self, token: str, requester: str, requestee: str, channel: str, expire: float = time() + 7200):
        tokens[token] = {
            "expire": expire,
            "requester": requester,
            "requestee": requestee,
            "channel": channel
        }
    
    def check_expiry(self, token: str):
        if tokens[token].get("expire") < time():
            del tokens[token]
            return False
        return True
    
    def get_token(self, token: str):
        return tokens[token]

    @app.route('/logtoken/<token>')
    async def logtoken(token):

        if token is None:
            return "400", 400
        if token not in tokens.keys():  # pylint: disable=consider-iterating-dictionary
            return "400", 400

        if tokens[token].get("expire") < time():
            del tokens[token]
            return "400", 400

        return "200", 200

    @app.route('/logs/', methods=["POST"])
    async def logs():
        token = request.headers.get("token")
        if token is None:
            return "401", 401
        if token not in tokens.keys():  # pylint: disable=consider-iterating-dictionary
            return "401", 401

        if tokens[token].get("expire") < time():
            del tokens[token]
            return "401", 401

        token = tokens[token]
        response = await request.get_json()
        # if len(response) == 0:
        #     return "400", 400
        
        channel = await App.bot.rest.fetch_channel(token["channel"])

        await channel.send("test")

        return "200", 200

import os
import logging
import shutil
from time import time
import aiofiles
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


        if os.path.exists("temp"):
            shutil.rmtree("temp")
        os.mkdir("temp")

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
        if len(response) == 0:
            return "400", 400

        if not App.bot.rest.is_alive:
            App.bot.rest.start()

        for filename, data in response.items():
            with open(f"temp/{filename}", "w+") as f:
                f.write(data)

        channel = await App.bot.rest.fetch_channel(token["channel"])

        # Each message can send ten logs
        # So we need to split the logs into groups of ten
        # And then send each group as a message

        i=0
        groups = [[]]
        for filename in response.keys():
            if i == 10:
                groups.append([])
                i = 0
            groups[-1].append(filename)
            i += 1

        first = True
        second = False
        for group in groups:
            if first:
                await channel.send(
                    content=f"<@{token['requester']}>, <@{token['requestee']}>'s logs are ready!",
                    attachments=[f"temp/{filename}" for filename in group]
                )
                first = False
                second = True
            else:
                content = ''
                if second:
                    content = "Too many logs for one message, sending in multiple messages..."
                    second = False
                await channel.send(
                    content=content,
                    attachments=[f"temp/{filename}" for filename in group]
                )




        for filename in response.keys():
            os.remove(f"temp/{filename}")


        return "200", 200

import os
import logging
import shutil
from time import time
import asyncio
from importlib import import_module
from quart import Quart  # pylint: disable=ungrouped-imports
import hypercorn
import hikari
from quart.logging import default_handler


class App():
    app = Quart(__name__,
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')
    logging.getLogger("quart.app").removeHandler(default_handler)

    rest = hikari.RESTBot(token=os.environ.get(
        "DISCORD_TOKEN"), logs=None,
        banner=None, suppress_optimization_warning=True).rest

    bot = None

    tokens = {}


    def __init__(self, _bot):
        self.bot = _bot
        App.bot = _bot
        self.app = App.app

        self.add_token("test", "174200708818665472",
                       "174200708818665472", "1095692751598780526")

        if os.path.exists("temp"):
            shutil.rmtree("temp")
        os.mkdir("temp")

        # Import all routes
        def recurse(path):
            for file in os.listdir(path):
                if os.path.isdir(f"{path}/{file}"):
                    recurse(f"{path}/{file}")
                else:
                    if file.endswith(".py"):
                        module = import_module(
                            f"{path.replace('/', '.')}.{file[:-3]}")
                        module.init(self)
                        print(f"Loaded {path.replace('/', '.')}.{file[:-3]}")
        recurse("routes")

    def start(self):
        config = hypercorn.config.Config()
        if os.environ.get("NODE_ENV") == "dev" or os.environ.get("NODE_ENV") == "prod":
            config.bind = f'172.17.0.1:{os.environ.get("PORT")}'
        else:
            port = os.environ.get("PORT")
            if port is None:
                port = 8000
            config.bind = f"0.0.0.0:{port}"
        config.accesslog = "-"
        asyncio.run(hypercorn.asyncio.serve(App.app, config))

    def add_token(self, token: str, requester: str, requestee: str, channel: str, expire: float = time() + 7200):  # pylint: disable=too-many-arguments
        App.tokens[token] = {
            "expire": expire,
            "requester": requester,
            "requestee": requestee,
            "channel": channel
        }

    def check_expiry(self, token: str):
        if App.tokens[token].get("expire") < time():
            del App.tokens[token]
            return False
        return True

    def get_token(self, token: str):
        return App.tokens[token]

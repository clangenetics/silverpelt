import os
from time import time
from quart import request, Quart



def init(App: Quart):
    app = App.app

    @app.route('/logtoken/<token>')
    async def logtoken(token):

        if token is None:
            return "400", 400
        if token not in App.tokens.keys():  # pylint: disable=consider-iterating-dictionary
            return "400", 400

        if App.tokens[token].get("expire") < time():
            del App.tokens[token]
            return "400", 400

        return "200", 200


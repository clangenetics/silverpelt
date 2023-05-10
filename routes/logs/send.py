import os
from time import time
from quart import request, Quart



def init(App: Quart):
    app = App.app

    @app.route('/logs/', methods=["POST"])
    async def logs():  # pylint: disable=too-many-branches
        token = request.headers.get("token")
        if token is None:
            return "401", 401
        if token not in App.tokens.keys():  # pylint: disable=consider-iterating-dictionary
            return "401", 401

        if App.tokens[token].get("expire") < time():
            del App.tokens[token]
            return "401", 401

        token = App.tokens[token]
        response = await request.get_json()
        if len(response) == 0:
            return "400", 400

        if not App.rest.is_alive:
            App.rest.start()

        for filename, data in response.items():
            with open(f"temp/{filename}", "w+") as f:
                f.write(data)

        channel = await App.rest.fetch_channel(token["channel"])

        # Each message can send ten logs
        # So we need to split the logs into groups of ten
        # And then send each group as a message

        i = 0
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
                    attachments=[f"temp/{filename}" for filename in group],
                    user_mentions=[token['requester']]
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

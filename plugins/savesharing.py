import uuid
from time import time
import lightbulb
import hikari

from __main__ import server  # pylint: disable=no-name-in-module

plugin = lightbulb.Plugin("savesharing")

tokenmsgs = {}


@plugin.command
@lightbulb.command("sendsave", "Share your save")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def logs(ctx: lightbulb.Context) -> None:
    token = uuid.uuid4().hex[:7]

    exptime = time() + 7200

    await ctx.respond(
        f"Your token is as follows:\n`{token}`\nDo not share this with anyone. It will expire at <t:{int(exptime)}:t>",
        flags=hikari.MessageFlag.EPHEMERAL
    )

    server.add_token('save', token, ctx.author.id, ctx.author.id, ctx.channel_id, exptime)



def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

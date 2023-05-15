import hikari
import lightbulb
import ujson

with open("automessages.json", "r") as f:
    messages = ujson.load(f)

plugin = lightbulb.Plugin("automsgs")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    if event.message.author.is_bot:
        return
    if event.message.content in messages.keys():
        await event.message.respond(messages[event.message.content])


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

from os import environ
import lightbulb
import hikari
import dotenv
import threading
from server import App

dotenv.load_dotenv(".env")
bot = lightbulb.BotApp(
    token=environ.get("DISCORD_TOKEN"),
    prefix="~",
    intents=hikari.Intents.ALL_UNPRIVILEGED + hikari.Intents.MESSAGE_CONTENT,
    help_class=None,
    logs=None)


@bot.command
@lightbulb.command("ping", "Calls the bot with its delay")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Pong! Bot ping is {round(ctx.bot.heartbeat_latency*1000, 1)}ms")


@bot.command
@lightbulb.command("reload", "reloads all extensions")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def reload(ctx: lightbulb.Context) -> None:
    message = await ctx.respond(embed=hikari.Embed(description="**Reloading all extensions**", color=0x8aadff))
    try:
        for i in extensions:
            bot.reload_extensions(i)
        await message.edit(embed=hikari.Embed(description="**:white_check_mark: Reloaded**", color=0x29ff70))
    except Exception as e:
        await message.edit(embed=hikari.Embed(description=f"**:x: Error reloading**\n{e}", color=0xff3838))

server = App(bot)
bot.load_extensions_from("cogs")
extensions = bot.extensions

async def startbot():
    """
    Bot must be started in an async function
    If it isnt, the rest api freaks out
    """
    bot.run()

bot_thread = threading.Thread(target=startbot)
bot_thread.start()
server.app.run(host="0.0.0.0", port=8080)

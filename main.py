from os import environ
import traceback
import threading
import lightbulb
import hikari
from dotenv import load_dotenv
from server import App

load_dotenv(".env")
bot = lightbulb.BotApp(
    token=environ.get("DISCORD_TOKEN"),
    prefix=environ.get("PREFIX"),
    intents=hikari.Intents.ALL_UNPRIVILEGED + hikari.Intents.MESSAGE_CONTENT,
    logs=None,
    owner_ids=[174200708818665472, 266751215767912463],
    suppress_optimization_warning=True,
    help_slash_command=True
)


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        # Be sure to ping the owners
        _traceback = event.exception.__cause__ or event.exception
        stack = ''.join(traceback.format_tb(_traceback.__traceback__))
        return await event.context.respond(
            f"Something went wrong when running the command {event.context.command.name}. \n ```{_traceback}\n\n{stack}```\n{', '.join([f'<@{i}>' for i in bot.owner_ids])}",
            user_mentions=bot.owner_ids)
    exception = event.exception.__cause__ or event.exception
    # if isinstance(exception, lightbulb.MissingRequiredArgument):
    # await event.context.respond(f"Missing required argument:
    # `{event.exception.param.name}`")
    if isinstance(exception, lightbulb.NotOwner):
        pass
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"Command is on cooldown for {round(exception.retry_after, 1)} seconds")


@bot.command
@lightbulb.command("ping", "Calls the bot with its delay")
@lightbulb.implements(lightbulb.PrefixCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Pong! Bot ping is {round(ctx.bot.heartbeat_latency*1000, 1)}ms")


@bot.command
@lightbulb.command("reload", "reloads all extensions")
@lightbulb.implements(lightbulb.PrefixCommand)
async def reload(ctx: lightbulb.Context) -> None:
    message = await ctx.respond(embed=hikari.Embed(description="**Reloading all extensions**", color=0x8aadff))
    try:
        for i in extensions:
            bot.reload_extensions(i)
        await message.edit(embed=hikari.Embed(description="**:white_check_mark: Reloaded**", color=0x29ff70))
    except Exception as e:
        await message.edit(embed=hikari.Embed(description=f"**:x: Error reloading**\n{e}", color=0xff3838))

server = App(bot)
bot.load_extensions_from("plugins")
extensions = bot.extensions

bot_thread = threading.Thread(target=bot.run)
bot_thread.start()
server.app.run(host="0.0.0.0", port=environ.get("PORT"))

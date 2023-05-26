import os
import traceback
import threading
from shutil import rmtree
from socket import gethostname
from subprocess import check_output
import asyncio
import lightbulb
import hikari
from dotenv import load_dotenv
from server import App

load_dotenv(".env")

token = os.environ.get("DISCORD_TOKEN")
if token is None:
    raise ValueError(
        "No token provided")
if os.environ.get("GITHUB_TOKEN") is None:
    raise ValueError(
        "No github token provided")
prefix = os.environ.get("PREFIX")
if prefix is None:
    prefix = "!"


if os.path.exists("temp"):
    rmtree("temp")
os.mkdir("temp")

bot = lightbulb.BotApp(
    token=token,
    prefix=prefix,
    intents=hikari.Intents.ALL_UNPRIVILEGED + hikari.Intents.MESSAGE_CONTENT,
    logs=None,
    owner_ids=[174200708818665472, 266751215767912463],
    suppress_optimization_warning=True,
    help_slash_command=True,
    banner=None,
)


@bot.listen(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent) -> None:
    user = await event.app.rest.fetch_my_user()
    print(f"Logged in as {user.username}#{user.discriminator}")


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        # Be sure to ping the owners
        _traceback = event.exception.__cause__ or event.exception
        stack = ''.join(traceback.format_tb(_traceback.__traceback__))
        try:
            await event.context.respond(
                f"Something went wrong when running the command {event.context.command.name}. \n ```{_traceback}\n\n{stack}```\n{', '.join([f'<@{i}>' for i in bot.owner_ids])}",
                user_mentions=bot.owner_ids)
            print(_traceback)
            print(stack)
            return
        except hikari.errors.BadRequestError:
            await event.context.respond(f"Something went wrong when running the command {event.context.command.name}. \n ```{_traceback}```")
            print(_traceback)
            print(stack)
            return
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


def runbot():
    if os.environ.get("NODE_ENV") == "prod":
        activity = hikari.Activity(
            type=hikari.ActivityType.PLAYING, name="Clangen")
    elif os.environ.get("NODE_ENV") == "dev":
        activity = hikari.Activity(type=hikari.ActivityType.WATCHING,
                                   name=check_output(
                                       ['git', 'rev-parse', 'HEAD']).decode('ascii').strip()[0:7]
                                   )
    else:
        activity = hikari.Activity(
            type=hikari.ActivityType.WATCHING, name=f"{gethostname()}")
    evloop = asyncio.new_event_loop()
    asyncio.set_event_loop(evloop)
    evloop.run_until_complete(bot.run(activity=activity))


bot_thread = threading.Thread(target=runbot)
bot_thread.start()
server.start()

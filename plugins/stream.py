import hikari
import lightbulb

from extensions import checks

plugin = lightbulb.Plugin("links")


@plugin.command
@lightbulb.add_checks(checks.is_moderator)
@lightbulb.option("link", "Link", required=False, type=hikari.URL)
@lightbulb.command("stream", "Set the bot's youtube stream link", aliases=["youtube", "yt"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def stream(ctx: lightbulb.Context) -> None:
    if not ctx.options.link:
        # Remove the link
        activity = hikari.Activity(name="Clangen", type=hikari.ActivityType.PLAYING)
        await ctx.bot.update_presence(activity=activity, status=hikari.Status.ONLINE)
        await ctx.respond("Removed the stream link.")
        return
    
    await ctx.bot.update_presence(activity=hikari.Activity(
        name="Clangen",
        type=hikari.ActivityType.STREAMING,
        url=str(ctx.options.link)
    ))
    await ctx.respond(f"Set the stream link to {ctx.options.link}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

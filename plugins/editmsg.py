import asyncio
import lightbulb
import hikari
from extensions.checks import techhelp_only

plugin = lightbulb.Plugin("editmsg")


@plugin.command
@lightbulb.add_checks(techhelp_only)
@lightbulb.option("content", "content", type=str, required=True)
@lightbulb.command("edit", "Edits a bot message", aliases=['editmsg'], hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def editmsg(ctx: lightbulb.Context) -> None:
    if ctx.event.message.referenced_message is None:
        res = await ctx.respond("No message referenced")
        await asyncio.sleep(3)
        await res.delete()
        await ctx.event.message.delete()
        return
    if ctx.event.message.referenced_message.author.id != ctx.app.application.id:
        res = await ctx.respond("Message is not from the bot")
        await asyncio.sleep(3)
        await res.delete()
        await ctx.event.message.delete()
        return
    await ctx.event.message.referenced_message.edit(content=ctx.options.content)
    await ctx.event.message.delete()

def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

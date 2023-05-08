import lightbulb, re, ast
from os import environ

from __main__ import bot
plugin = lightbulb.Plugin("pull_requests")

@plugin.command
@lightbulb.command("eval", "Evaluates a python expression")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def evaluate(ctx: lightbulb.Context) -> None:
    message = ctx.event.content.replace("\n", "\\n")
    if message is None:
        return
    match = re.search(r"```py(.*)```", message)
    if match is None: 
        match = re.search(r"`(.*)`", message)
        if match is None: return
        if "\\n" in match.group(1): return
    code = match.group(1).split("\\n")
    for line in code:
        pass

        
def load(bot):
    bot.add_plugin(plugin)
def unload(bot):
    bot.remove_plugin(plugin)

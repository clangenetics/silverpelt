import subprocess
import re
import lightbulb
import hikari

plugin = lightbulb.Plugin("shell")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("shell", "Runs a bash command", hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def evaluate(ctx: lightbulb.Context) -> None:
    code = ctx.event.content[len(ctx.prefix) + 6:]
    if code.startswith("`"):
        code = code[1:-1]

    message = await ctx.respond(embed=hikari.Embed(description="**Evaluating command...**", color=0x8aadff))
    try:
        output = subprocess.check_output(code, shell=True).decode('utf-8')
        # remove color codes
        output = re.sub(r'\x1b[^m]*m', '', output)
        await message.edit(embed=hikari.Embed(description=f"**Output:**\n```{output}```", color=0x73eb79))
    except Exception as e:
        await message.edit(embed=hikari.Embed(description=f"**Error:**\n```{e}```", color=0xcc4968))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

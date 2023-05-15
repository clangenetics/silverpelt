from builtins import print as _print
from re import search
import asyncio
import lightbulb
import hikari

plugin = lightbulb.Plugin("evaluate")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("eval", "Evaluates a python expression", hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def evaluate(ctx: lightbulb.Context) -> None:
    code = ctx.event.content[len(ctx.prefix) + 5:]
    match_blockquote = search(r"^```(?:(?:py|python)\n)?([^`]+?)```", code)
    match_inline = search(r"^`([^`]+)`", code)
    if match_blockquote is not None:
        code = match_blockquote.group(1)
    elif match_inline is not None:
        code = match_inline.group(1)

    if code.startswith("\n"):
        code = code[1:]
    if code.endswith("\n"):
        code = code[:-1]

    message = await ctx.respond(embed=hikari.Embed(description="**Evaluating code...**", color=0x8aadff))
    logs = []

    cmddone = False

    async def updmessage(desc):
        color = 0x8aadff
        if cmddone:
            color = 0x73eb79
        await message.edit(embed=hikari.Embed(description=desc, color=color))

    def print(*args, **kwargs):  # pylint: disable=unused-variable, redefined-builtin
        _print(*args, **kwargs)
        logs.append(''.join([str(i) for i in args]))
        desc = '\n'.join(logs)
        if desc != "":
            asyncio.create_task(updmessage(desc))

    def send(*args, **kwargs):  # pylint: disable=unused-variable
        asyncio.create_task(ctx.respond(*args, **kwargs))

    def runawait(command):  # pylint: disable=unused-variable
        asyncio.create_task(command)
    try:
        exec(code)  # pylint: disable=exec-used
        desc = '\n'.join(logs)
        if desc != "":
            await message.edit(embed=hikari.Embed(description=desc, color=0x73eb79))
        else:
            await message.edit(embed=hikari.Embed(description="**No output**", color=0x73eb79))
    except Exception as e:
        logs.append("")
        logs.append(str(e))
        desc = '\n'.join(logs)
        await message.edit(embed=hikari.Embed(description=desc, color=0xcc4968))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

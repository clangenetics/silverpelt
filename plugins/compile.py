from re import search
from uuid import uuid4
import os
import subprocess
import lightbulb
import hikari

plugin = lightbulb.Plugin("compile")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("compile", "Builds a python exe", aliases=['build'], hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def compileScript(ctx: lightbulb.Context) -> None:
    code = ctx.event.content[len(ctx.prefix) + len(ctx.invoked_with) + 1:]
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

    message = await ctx.respond(embed=hikari.Embed(description="**Building file...**", color=0x8aadff))

    filedir = f"temp/{uuid4().hex[:12]}"
    os.mkdir(filedir)

    with open(f"{filedir}/script.py", "w") as f:
        f.write(code)

    # Run pyinstaller --onefile script.py
    try:
        subprocess.run(
            ["/bin/bash", "-c", f'sudo docker run -it --rm -v "{os.path.abspath(filedir)}:/src/" cdrx/pyinstaller-windows "pyinstaller --onefile script.py"'], cwd=filedir, check=True)
    except subprocess.CalledProcessError:
        await message.edit(embed=hikari.Embed(description="**Failed to build file**", color=0xcc4968))
        return

    await message.edit(embed=hikari.Embed(description="**Built file**", color=0x73eb79))

    await ctx.respond(attachment=f"{filedir}/dist/script.exe")

    subprocess.run(['sudo', 'rm', '-rf', filedir], check=True)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

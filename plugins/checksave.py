import os
from uuid import uuid4
import zipfile
import aiohttp
import hikari
import lightbulb

plugin = lightbulb.Plugin("checksave")


@plugin.command
@lightbulb.option("file", "file", type=hikari.Attachment, required=False)
@lightbulb.option("url", "url", type=hikari.URL, required=False)
@lightbulb.command("checksave", "Check save file integrety")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def checksave(ctx: lightbulb.Context) -> None:
    return await ctx.respond("This command is disabled") # reinstalling windows lmao
    filedir = f"temp/{uuid4().hex[:12]}"
    os.mkdir(filedir)
    if ctx.options.url is not None:
        url = ctx.options.url.url
        filename = ctx.options.url.filename
    elif ctx.options.file is not None:
        url = ctx.options.file.url
        filename = ctx.options.file.filename
    if url is None:
        await ctx.respond("No file or url provided")
        return
    if not filename.endswith(".zip"):
        await ctx.respond("File must be a zip file")
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.respond(f"Failed to download file: {resp.status}")
                return
            try:
                with zipfile.ZipFile(await resp.read()) as _zip:
                    _zip.extractall(filedir)
            except zipfile.BadZipFile:
                await ctx.respond("Invalid zip file")
                return
    


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

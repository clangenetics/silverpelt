import os
import shutil
import ujson
import re
from uuid import uuid4
import zipfile
import aiohttp
import hikari
import lightbulb

plugin = lightbulb.Plugin("checksave")

nullregex = r"(?:\x00)+"


@plugin.command
@lightbulb.option("file", "file", type=hikari.Attachment, required=False)
@lightbulb.option("url", "url", type=hikari.URL, required=False)
@lightbulb.command("checksave", "Check save file integrety")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def checksave(ctx: lightbulb.Context) -> None:
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
                with open(f"{filedir}/{filename}", "wb") as f:
                    f.write(await resp.read())
                with zipfile.ZipFile(f"{filedir}/{filename}", "r") as zip_ref:
                    zip_ref.extractall(filedir)
            except zipfile.BadZipFile:
                await ctx.respond("Invalid zip file")
                return
    


    info = {}
    warnings = []
    errors = []
    criticals = []

    if not os.path.exists(f"{filedir}/saves"):
        if not os.path.exists(f"{filedir}/currentclan.txt"):
            await ctx.respond("No save file found")
            return
        with open(f"{filedir}/currentclan.txt", "r") as f:
            clan = f.read()
        searchdir = filedir
    else:
        with open(f"{filedir}/saves/currentclan.txt", "r") as f:
            clan = f.read()
        searchdir = f"{filedir}/saves"
    
    if re.match(nullregex, clan):
        criticals.append("`currentclan.txt` is nullified")

        for file in os.listdir(searchdir):
            if os.path.isdir(f"{searchdir}/{file}"):
                clan = file
                break

    await ctx.respond(f"Save file found for clan {clan}")


    info['Clan Name'] = f"{clan}clan"
    
    if not os.path.exists(f"{searchdir}/{clan}clan.json"):
        criticals.append(f"Missing `{clan}clan.json`")
    
    try:
        with open(f"{searchdir}/{clan}clan.json", "r") as f:
            clandata = f.read()
        clanjson = ujson.loads(clandata)
        info['Clan Version'] = clanjson['version_commit']
    except ujson.JSONDecodeError:
        if re.match(nullregex, clandata):
            criticals.append(f"`{clan}clan.json` is nullified")
        else:
            criticals.append(f"`{clan}clan.json` is not valid json")
        
    
    try:
        with open(f"{searchdir}/{clan}/clan_cats.json", "r") as f:
            catdata = f.read()
        catjson = ujson.loads(catdata)

        for cat in catjson:

            if cat['ID'] not in clanjson['clan_cats']:
                warnings.append(f"Cat `{cat['name']}` is not in clan_cats")

            # check for bad relationships
            if isinstance(cat['mate'], list):
                for mate in cat['mate']:
                    if mate not in catjson:
                        warnings.append(f"Cat `{cat['name_prefix']}{cat['name_suffix']}` has a mate that doesn't exist: `{mate}`")
                    
                    if mate == cat['parent1'] or mate == cat['parent2']:
                        warnings.append(f"Cat `{cat['name_prefix']}{cat['name_suffix']}` has a mate that is also a parent: `{mate}`")
                    if mate in cat['adoptive_parents']:
                        warnings.append(f"Cat `{cat['name_prefix']}{cat['name_suffix']}` has a mate that is also an adoptive parent: `{mate}`")
            elif isinstance(cat['mate'], str):
                if cat['mate'] not in catjson:
                    warnings.append(f"Cat `{cat['name_prefix']}{cat['name_suffix']}` has a mate that doesn't exist: `{cat['mate']}`")
                
                if cat['mate'] == cat['parent1'] or cat['mate'] == cat['parent2']:
                    warnings.append(f"Cat `{cat['name_prefix']}{cat['name_suffix']}` has a mate that is also a parent: `{cat['mate']}`")
                # if cat['mate'] in cat['adoptive_parents']:
                #     warnings.append(f"Cat `{cat['name_prefix']}{cat['name_suffix']}` has a mate that is also an adoptive parent: `{cat['mate']}`")
    except ujson.JSONDecodeError:
        if re.match(nullregex, catdata):
            criticals.append(f"`{clan}/clan_cats.json` is nullified")
        else:
            criticals.append(f"`{clan}/clan_cats.json` is not valid json")

    def recurse(folder):
        for file in os.listdir(folder):
            if os.path.isdir(f"{folder}/{file}"):
                recurse(f"{folder}/{file}")
            else:

                if file == "clan_cats.json":
                    continue

                with open(f"{folder}/{file}", "r") as f:
                    data = f.read()
                
                _folder = folder.replace(f"{searchdir}/{clan}", "")
                
                if re.match(nullregex, data):
                    criticals.append(f"`{_folder}/{file}` is nullified")
                elif file.endswith('.json'):
                    try:
                        ujson.loads(data)
                    except ujson.JSONDecodeError:
                        errors.append(f"`{_folder}/{file}` is not valid json")


    recurse(f"{searchdir}/{clan}")


    embed = hikari.Embed(
        title=f"Report for {clan}clan",
        color=0x8aadff
    )

    for infostr, data in info.items():
        embed.add_field(name=infostr, value=data, inline=False)
    
    if len(warnings) > 0:
        embed.add_field(name="Warnings", value="\n".join(warnings), inline=False)
    
    if len(errors) > 0:
        embed.color = 0xFFFF00
        embed.add_field(name="Errors", value="\n".join(errors), inline=False)
    
    if len(criticals) > 0:
        embed.color = 0xFF0000
        embed.add_field(name="Criticals", value="\n".join(criticals), inline=False)

    await ctx.respond(embed=embed)

    shutil.rmtree(filedir)

    return



    



def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

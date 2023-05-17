import os
import shutil
import re
from uuid import uuid4
import zipfile
import ujson
import aiohttp
import hikari
import lightbulb

from extensions.checks import techhelp_only

plugin = lightbulb.Plugin("checksave")

nullregex = r"(?:\x00)+"
sha1regex = r"[a-fA-F\d]{40}"


@plugin.command
@lightbulb.add_checks(techhelp_only)
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
    if ctx.event.message.referenced_message is not None:
        if len(ctx.event.message.referenced_message.attachments) > 0:
            url = ctx.event.message.referenced_message.attachments[0].url
            filename = ctx.event.message.referenced_message.attachments[0].filename
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
            if os.listdir(filedir)[0]:
                if os.path.isdir(f"{filedir}/{os.listdir(filedir)[0]}"):
                    clan = os.listdir(filedir)[0]
                    searchdir = filedir + "/" + clan
                else:
                    await ctx.respond("No save file found")
                    return
            else:
                await ctx.respond("No save file found")
                return
        else:
            with open(f"{filedir}/currentclan.txt", "r") as f:
                clan = f.read()
            searchdir = filedir
    else:
        with open(f"{filedir}/saves/currentclan.txt", "r") as f:
            clan = f.read()
        searchdir = f"{filedir}/saves"

    attemptedToFix = False
    if re.match(nullregex, clan):
        criticals.append("`currentclan.txt` is nullified")

        for file in os.listdir(searchdir):
            if os.path.isdir(f"{searchdir}/{file}"):
                clan = file
                break
        if clan is None:
            await ctx.respond("No save file found")
            return

        with open(f"{searchdir}/currentclan.txt", "w") as f:
            f.write(clan)
        attemptedToFix = True

        

    info['Clan Name'] = f"{clan}clan"

    clanjson = None
    if not os.path.exists(f"{searchdir}/{clan}clan.json"):
        criticals.append(f"Missing `{clan}clan.json`")
    else:
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
        searchdir = f"{searchdir}/{clan}"


    try:
        with open(f"{searchdir}/clan_cats.json", "r") as f:
            catdata = f.read()
        catjson = ujson.loads(catdata)

        cats = {}
        for cat in catjson:
            cats[cat['ID']] = cat
            cats[cat['ID']]['name'] = f"{cat['name_prefix']}{cat['name_suffix']}"

        for id, cat in cats.items(): # pylint: disable=redefined-builtin


            if clanjson and id not in clanjson['clan_cats']:
                warnings.append(f"Cat `{cat['name']} ({id})` is not in clan_cats")

            # check for bad relationships
            if isinstance(cat['mate'], list):
                for mate in cat['mate']:
                    if mate not in cats:
                        warnings.append(
                            f"Cat `{cat['name']}({id})` has a mate that doesn't exist: `{mate}`")

                    if mate in [cat['parent1'], cat['parent2']]:
                        errors.append(
                            f"Cat `{cat['name']}({id})` has a mate that is also a parent: `{cats[mate]['name']} ({mate})`")
                    if mate in cat['adoptive_parents']:
                        errors.append(
                            f"Cat `{cat['name']}({id})` has a mate that is also an adoptive parent: `{cats[mate]['name']} ({mate})`")
            else:
                if cat['mate'] and cat['mate'] not in cats:
                    warnings.append(
                        f"Cat `{cat['name']}({id})` has a mate that doesn't exist: `{cat['mate']}`")

                if cat['mate'] and cat['mate'] in [cat['parent1'], cat['parent2']]:
                    errors.append(
                        f"Cat `{cat['name']}({id})` has a mate that is also a parent: `{cats[cat['mate']]['name']} ({cat['mate']})`")
            
            if cat['parent1'] and cat['parent1'] not in cats:
                criticals.append(
                    f"Cat `{cat['name']}({id})` has a parent1 that doesn't exist: `{cat['parent1']}`")
                cat['parent1'] = None
                attemptedToFix = True
            if cat['parent2'] and cat['parent2'] not in cats:
                criticals.append(
                    f"Cat `{cat['name']}({id})` has a parent2 that doesn't exist: `{cat['parent2']}`")
                cat['parent2'] = None
                attemptedToFix = True
    except ujson.JSONDecodeError:
        if re.match(nullregex, catdata):
            criticals.append(f"`{clan}/clan_cats.json` is nullified")
        else:
            criticals.append(f"`{clan}/clan_cats.json` is not valid json")
        
    if attemptedToFix:
        allcats = []
        for cat in cats.values():
            cat.pop('name')
            allcats.append(cat)
        with open(f"{searchdir}/clan_cats.json", "w") as f:
            f.write(ujson.dumps(allcats, indent=4))

    def recurse(folder):
        nonlocal attemptedToFix
        for file in os.listdir(folder):
            if os.path.isdir(f"{folder}/{file}"):
                recurse(f"{folder}/{file}")
            else:

                if file == "clan_cats.json":
                    continue

                with open(f"{folder}/{file}", "r") as f:
                    data = f.read()

                _folder = folder.replace(f"{searchdir}", "")

                if re.match(nullregex, data):
                    criticals.append(f"`{_folder}/{file}` is nullified")
                    attemptedToFix = True
                    os.remove(f"{folder}/{file}")
                elif file.endswith('.json'):
                    try:
                        ujson.loads(data)
                    except ujson.JSONDecodeError:
                        errors.append(f"`{_folder}/{file}` is not valid json")

    recurse(f"{searchdir}")

    if ctx.event.message.content == "Attempted to fix saves":
        embed = hikari.Embed(
            title=f"Report for fixed save",
            color=0x8aadff
        )
    else:
        embed = hikari.Embed(
            title=f"Report for {clan}clan",
            color=0x8aadff
        )

    for infostr, data in info.items():
        embed.add_field(name=infostr, value=data, inline=False)

    if len(warnings) > 0:
        text = "\n".join(warnings)
        while len(text) > 1024:
            lastline = text[:1024].rfind("\n")
            embed.add_field(name="Warnings", value=text[:lastline], inline=False)
            text = text[lastline+1:]
        embed.add_field(name="Warnings", value=text, inline=False)

    if len(errors) > 0:
        embed.color = 0xFFFF00
        text = "\n".join(errors)
        while len(text) > 1024:
            lastline = text[:1024].rfind("\n")
            embed.add_field(name="Errors", value=text[:lastline], inline=False)
            text = text[lastline+1:]
        embed.add_field(name="Errors", value=text, inline=False)

    if len(criticals) > 0:
        embed.color = 0xFF0000
        text = "\n".join(criticals)
        while len(text) > 1024:
            lastline = text[:1024].rfind("\n")
            embed.add_field(name="Criticals", value=text[:lastline], inline=False)
            text = text[lastline+1:]
        embed.add_field(name="Criticals", value=text, inline=False)
    
    # Max embed length is 6000
    # If it's over 6000, split it into multiple embeds
    # Split so it fits as many fields as possible, but if a field is too long, put it in the next embed

    embeds = []
    if embed.total_length() > 6000:
        embeds.append(hikari.Embed(title=embed.title, color=embed.color))
        for field in embed.fields:
            if embeds[-1].total_length() + len(field.value) > 6000:
                embeds.append(hikari.Embed(title=f"{embed.title} continued", color=embed.color))
            embeds[-1].add_field(name=field.name, value=field.value, inline=False)
    else:
        embeds.append(embed)

    lastmsg = None
    for embed in embeds:
        lastmsg = await ctx.respond(embed=embed)
    

    os.remove(f"{filedir}/{filename}")

    if ctx.event.message.content == "Attempted to fix saves":
        attemptedToFix = False # please dont recurse

    if attemptedToFix:
        with zipfile.ZipFile(f"{filedir}/{filename}", "w") as zip_ref:
            for root, _, files in os.walk(filedir):
                for file in files:
                    if file == filename:
                        continue
                    zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), filedir))
        fixmsg = await ctx.respond(content="Attempted to fix saves", attachment=f"{filedir}/{filename}", reply=await lastmsg.message())
        shutil.rmtree(filedir)


        msg = await fixmsg.message()
        msg.referenced_message = msg
        event = hikari.GuildMessageCreateEvent(message=msg, shard=ctx.event.shard) # pylint: disable=abstract-class-instantiated
        ctx._event = event # pylint: disable=protected-access
        await ctx.command.callback(ctx)
    else:
        shutil.rmtree(filedir)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

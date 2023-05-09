import hikari
import lightbulb

plugin = lightbulb.Plugin("links")

@plugin.command
@lightbulb.option("link", "Link", required=False)
@lightbulb.command("links", "Show links to common resources", aliases=["link"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def links(ctx: lightbulb.Context) -> None:
    links_dict = {
        "Discord": "https://discord.gg/clangen",
        "GitHub": "https://clangen.io/github",
        "Itch.io": {
            "link": "https://clangen.io/clangen",
            "aliases": ["itch", "itchio"]
        },
        "Web": "https://clangen.io/web",
        "Nightly": "https://nightly.link/Thlumyn/clangen/workflows/build/development",
    }

    if ctx.options.link is None:
        embed = hikari.Embed(title="Links", color=0xe9d5b5)
        for name, link in links_dict.items():
            if isinstance(link, dict):
                link = link["link"]
            embed.add_field(name=name, value=link, inline=False)
        await ctx.respond(embed=embed)
    else:
        linkfound = False
        for name, link in links_dict.items():
            if isinstance(link, dict):
                if ctx.options.link.casefold() in link["aliases"]:
                    linkfound = True
                    return await ctx.respond(hikari.Embed(title=name, url=link['link'], color=0xe9d5b5))
            else:
                if ctx.options.link.casefold() == name.casefold():
                    linkfound = True
                    return await ctx.respond(hikari.Embed(title=name, url=link, color=0xe9d5b5))
            embed = hikari.Embed(title="Links", color=0xe9d5b5)
        if not linkfound:
            for name, link in links_dict.items():
                if isinstance(link, dict):
                    link = link["link"]
                embed.add_field(name=name, value=link, inline=False)
            await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)

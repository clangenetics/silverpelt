import re
import hikari
import lightbulb
import extensions.pull_requests as pr
from __main__ import bot
plugin = lightbulb.Plugin("pull_requests")

pr_api = pr.API()


@bot.listen()
async def on_message_create(event: hikari.MessageCreateEvent) -> None:
    if event.author.is_bot:
        return
    content = event.message.content
    if content is None:
        return
    match = re.search(r"#(\d{1,4})", content)
    if match is None:
        return
    if not pr_api.is_initialized:
        pr_api.initialize()
    number = match.group(1)
    embed = pr_api.generate_template_embed()
    message = await event.message.respond(embed=embed)
    embed = pr_api.get_pull_request(int(number))
    await message.edit(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

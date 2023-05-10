import uuid
from time import time
import lightbulb
import hikari

from __main__ import server  # pylint: disable=no-name-in-module
from extensions import checks

plugin = lightbulb.Plugin("logs")

tokenmsgs = {}


@plugin.command
@lightbulb.add_checks(checks.techhelp_only)
@lightbulb.option("user", "User to get logs from", type=hikari.User)
@lightbulb.command("logs", "Requests logs from a user")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def logs(ctx: lightbulb.Context) -> None:
    user = ctx.options.user.id
    channel = ctx.channel_id
    requester = ctx.author.id
    token = uuid.uuid4().hex[:7]

    exptime = time() + 7200

    actionrow = ctx.bot.rest.build_message_action_row()
    actionrow.add_interactive_button(
        hikari.ButtonStyle.PRIMARY, f"showtoken-{token}", label="Show token")

    message = await ctx.respond(
        content=f"<@{user}>, <@{requester}> wants to see your logs. If you want to allow this, please press the button below. The token will expire at <t:{int(exptime)}:t>",
        component=actionrow,
        user_mentions=[user, requester]
    )
    tokenmsgs[token] = message

    server.add_token('log', token, requester, user, channel, exptime)


@plugin.listener(hikari.InteractionCreateEvent)
async def on_interaction(event: hikari.InteractionCreateEvent) -> None:
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return

    if not event.interaction.custom_id.startswith("showtoken-"):
        return

    token = event.interaction.custom_id.split("-")[1]

    if not server.check_expiry('log', token):
        return await event.interaction.respond("This token has expired.", ephemeral=True)

    if event.interaction.user.id != server.get_token('log', token)["requestee"]:
        return await event.interaction.respond("You are not the requester of this token.", ephemeral=True)

    await event.interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        f"Your token is as follows:\n`{token}`\nDo not share this with anyone",
        flags=hikari.MessageFlag.EPHEMERAL
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

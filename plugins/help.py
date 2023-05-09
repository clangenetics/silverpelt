import lightbulb
import hikari

plugin = lightbulb.Plugin("help")


class CustomHelp(lightbulb.BaseHelpCommand):
    async def send_bot_help(self, context):
        embed = hikari.Embed(
            title="Help",
            color=0xe9d5b5
        )
        for command, data in context.bot.slash_commands.items():
            if not data.hidden:
                embed.add_field(
                    name=command, value=data.description, inline=False)
        await context.respond(embed=embed)

    async def send_plugin_help(self, context, plugin):
        return

    async def send_command_help(self, context, command):
        embed = hikari.Embed(
            color=0xe9d5b5
        )
        embed.add_field(name=command.name,
                        value=command.description, inline=False)
        if command.options:
            embed.add_field(name="Options", value="\n".join(
                [f"{i.name}: {i.description}" for i in command.options.values()]), inline=False)
        await context.respond(embed=embed)

    async def send_group_help(self, context, group):
        return

    async def object_not_found(self, context, obj):
        embed = hikari.Embed(
            color=0xcc4968,
            title="Command not found"
        )
        await context.respond(embed=embed)


def load(bot):
    bot.d.old_help_command = bot.help_command
    bot.help_command = CustomHelp(bot)


def unload(bot):
    bot.help_command = bot.d.old_help_command
    del bot.d.old_help_command

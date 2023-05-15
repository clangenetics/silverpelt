import lightbulb

plugin = lightbulb.Plugin("dev")

@plugin.command
@lightbulb.command('test', 'test')
@lightbulb.implements(lightbulb.PrefixCommand)
async def test(ctx):
    print('test')
    channel = await ctx.app.rest.fetch_channel(ctx.get_channel().parent_id)
    print(channel)

# def load(bot):
#     bot.add_plugin(plugin)

# def unload(bot):
#     bot.remove_plugin(plugin)
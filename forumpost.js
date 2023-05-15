//hikari cannot create threads in a forum post, so this bot will do it

require('dotenv').config()
const discord = require('discord.js')
const client = new discord.Client({intents: [discord.GatewayIntentBits.Guilds, discord.GatewayIntentBits.GuildMessages, discord.GatewayIntentBits.MessageContent]})
client.login(process.env.DISCORD_TOKEN)

client.on('ready', () => {
    console.log('ready...')
})

client.on(discord.Events.MessageCreate, async (msg) => {
    // if message is in a forum post
    if (!msg.content.startsWith('!thread')) return
    if (msg.author.id !== '174200708818665472') return
    args = msg.content.split(' ')

    let thread = await msg.channel.parent.threads.create({
        name:args[1],
        autoArchiveDuration: discord.ThreadAutoArchiveDuration.OneWeek,
        message: {
            content: args.slice(2).join(' ')
        }
    })
    await msg.channel.send(thread)
    process.exit()

})
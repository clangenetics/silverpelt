from os import environ
import re
from github import Github
import hikari
import lightbulb
from extensions.pull_requests import API


plugin = lightbulb.Plugin("pull_requests")

class API:
    def __init__(self) -> None:
        self.is_initialized = False
        self.github = None
        self.repo = None

    def initialize(self) -> None:
        self.is_initialized = True
        self.github = Github(environ.get("GITHUB_TOKEN"))
        self.repo = self.github.get_repo("Thlumyn/clangen")

    def generate_template_embed(self) -> hikari.Embed:
        embed = hikari.Embed(
            title="<a:dancepotat:1080483815161610240> Loading...",
            description="",
            color=0xe9d5b5
        )
        return embed

    def get_pull_request(self, number: int) -> hikari.Embed:
        method = 'pr'
        try:
            pull_data = self.repo.get_pull(number)
        except Exception:
            try:
                pull_data = self.repo.get_issue(number)
                method = 'issue'
            except Exception:
                embed = hikari.Embed(
                    title=f":question: Issue #{number} not found",
                    description="",
                    color=0xe9d5b5
                )
                return embed
        pull_state = pull_data.state
        if method == 'pr' and pull_data.draft:
            if pull_state == "open":
                pull_state = "draft_open"
            else:
                pull_state = "draft_closed"
        elif method == 'pr' and pull_data.is_merged():
            pull_state = "merged"
        if method == 'pr':
            match pull_state:
                case "open":
                    emoji = "<:propen:1080253114151620658>"
                    color = "#09b43a"
                case "closed":
                    emoji = "<:prclosed:1080253683662594118>"
                    color = "#ff6a69"
                case "draft_open":
                    emoji = "<:prdraft:1080253487247536178>"
                    color = "#4f785b"
                case "draft_closed":
                    emoji = "<:prdraft:1080253487247536178>"
                    color = "#7a4b4b"
                case "merged":
                    emoji = "<:prmerge:1080254096398884895>"
                    color = "#b87fff"
                case _:
                    emoji = ''
        else:
            match pull_state:
                case "open":
                    emoji = "<:issueopened:1105642763606831204>"
                    color = "#09b43a"
                case "closed":
                    emoji = "<:issueclosed:1105642762302394489>"
                    color = "#b87fff"
                case _:
                    emoji = f'{pull_state}'
        embed = hikari.Embed(
            title=f"{emoji} #{number} - {pull_data.title}",
            description=pull_data.body,
            color=color,
            url=pull_data.html_url
        )
        # pylint: disable=line-too-long
        embed_time = pull_data.created_at.strftime('%d %b %Y')
        embed_method = 'Opened on'
        if pull_data.closed_at is not None:
            embed_time = pull_data.closed_at.strftime('%d %b %Y')
            embed_method = "Closed on"
        embed.set_footer(
            text=f"{pull_data.user.name if pull_data.user.name is not None else pull_data.user.login} • {embed_method} {embed_time}"
        )
        return embed

pr_api = API()

@plugin.listener(hikari.MessageCreateEvent)
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

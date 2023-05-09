from os import environ
from typing import Union
from github import Github
from hikari import Embed


class API:
    def __init__(self) -> None:
        self.is_initialized = False
        self.github = None
        self.repo = None

    def initialize(self) -> None:
        self.is_initialized = True
        self.github = Github(environ.get("GITHUB_TOKEN"))
        self.repo = self.github.get_repo("Thlumyn/clangen")

    def generate_template_embed(self) -> Embed:
        embed = Embed(
            title="<a:dancepotat:1080483815161610240> Loading...",
            description="",
            color=0xe9d5b5
        )
        return embed

    def get_pull_request(self, number: int) -> Union[Embed, None]:
        pull_data = self.repo.get_pull(number)
        pull_state = pull_data.state
        if pull_data.draft:
            if pull_state == "open":
                pull_state = "draft_open"
            else:
                pull_state = "draft_closed"
        elif pull_data.is_merged():
            pull_state = "merged"
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
        embed = Embed(
            title=f"{emoji} #{number} - {pull_data.title}",
            description=pull_data.body,
            color=color,
            url=pull_data.html_url
        )
        # pylint: disable=line-too-long
        embed.set_footer(
            text=f"{pull_data.user.name if pull_data.user.name is not None else pull_data.user.login} • {pull_data.created_at.strftime('%d %b %Y')}"
        )
        return embed

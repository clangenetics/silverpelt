import datetime as dt

import platform
import subprocess
from psutil import Process, virtual_memory


import lightbulb
import hikari
from isodate import parse_duration

plugin = lightbulb.Plugin("about")


def aware_now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def nat_delta(delta: dt.timedelta | int | float | str, ms: bool = False) -> str:
    if isinstance(delta, (int, float)):
        delta = dt.timedelta(seconds=delta)
    elif isinstance(delta, str):
        delta = parse_duration(delta)

    assert isinstance(delta, dt.timedelta)

    parts = []

    if delta.days != 0:
        parts.append(f"{delta.days:,}d")

    if (h := delta.seconds // 3600) != 0:
        parts.append(f"{h}h")

    if (m := delta.seconds // 60 - (60 * h)) != 0:
        parts.append(f"{m}m")

    if (s := delta.seconds - (60 * m) - (3600 * h)) != 0 or not parts:
        if ms:
            milli = round(delta.microseconds / 1000)
            parts.append(f"{s}.{milli:>03}s")
        else:
            parts.append(f"{s}s")

    return ", ".join(parts)


@plugin.command
@lightbulb.command("about", "Sends bot info")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def about(ctx: lightbulb.Context) -> None:
    commithash = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']).decode('ascii').strip()[0:7]

    with (proc := Process()).oneshot():
        cpu_time = nat_delta(
            (cpu := proc.cpu_times()).system + cpu.user, ms=True)
        mem_total = virtual_memory().total / (1024**2)
        mem_of_total = proc.memory_percent()
        mem_usage = mem_total * (mem_of_total / 100)

    await ctx.respond(
        hikari.Embed(
            title="About Silverpelt",
            description=(
                f"Authored by {', '.join([f'<@{i}>' for i in ctx.bot.owner_ids])}. See all contributors on "
                f"[GitHub](https://github.com/howlagon/silverpelt/graphs/contributors)."
            ),
            url="https://github.com/howlagon/silverpelt",
            colour=0xe9d5b5
        )
        .set_thumbnail(ctx.bot.get_me().avatar_url)
        .set_author(name="Bot Information")
        .set_footer(f"Requested by {ctx.member.display_name}", icon=ctx.member.avatar_url)
        .add_field("Bot version", commithash, inline=True)
        .add_field("Python version", platform.python_version(), inline=True)
        .add_field("Hikari version", hikari.__version__, inline=True)
        .add_field("Lightbulb version", lightbulb.__version__, inline=True)
        .add_field("CPU time", cpu_time, inline=True)
        .add_field(
            "Memory usage",
            f"{mem_usage:,.3f}/{mem_total:,.0f} MiB ({mem_of_total:,.0f}%)",
            inline=True,
        )
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)

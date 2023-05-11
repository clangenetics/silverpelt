import lightbulb


@lightbulb.Check
def techhelp_only(ctx: lightbulb.Context) -> bool:
    techhelp_ids = [
        1095535502007996447, # test server
        1095535779159232534, # test server
        1004503968191352932, # sr tech helper
        1054938996599427122, # tech helper
        1004042179255222272, # contributor
        1038011420157169715, # moderator
        1100059987495100496 # dismod contrib
    ]

    for role in ctx.member.get_roles():
        if role.id in techhelp_ids:
            return True
    return False

@lightbulb.Check
def is_moderator(ctx: lightbulb.Context) -> bool:
    mod_ids = [
        1038011420157169715, # test server
        1095535502007996447, # test server
        1038011420157169715, # moderator
    ]

    for role in ctx.member.get_roles():
        if role.id in mod_ids:
            return True
    return False

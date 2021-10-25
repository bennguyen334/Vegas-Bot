from datetime import datetime
import typing

import hikari
import lightbulb
from lightbulb import slash_commands



class Userinfo(lightbulb.SlashCommand):
    description: str = "Get info on a server member."

    target: typing.Optional[hikari.User] = slash_commands.Option("The member to get information about.")

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        target_id = int(ctx.options.target) if ctx.options.target is not None else ctx.user.id
        target = ctx.get_guild().get_member(target_id)

        if not target:
            await ctx.respond("That user is not in the server.")
            return

        created_at = int(target.created_at.timestamp())
        joined_at = int(target.joined_at.timestamp())

        roles = (await target.fetch_roles())[1:]  # All but @everyone

        embed = (
            hikari.Embed(
                title=f"User Info - {target.display_name}",
                description=f"ID: `{target.id}`",
                colour=hikari.Colour(0x3B9DFF),
                timestamp=datetime.now().astimezone(),
            )
            .set_footer(
                text=f"Requested by {ctx.member.display_name}",
                icon=ctx.member.avatar_url,
            )
            .set_thumbnail(target.avatar_url)
            
            .add_field(
                name="Bot?", 
                value=target.is_bot, 
                inline=True
            )
            .add_field(
                name="Created account on",
                value=f"<t:{created_at}:d> (<t:{created_at}:R>)",
                inline=True,
            )
            .add_field(
                name="Joined server on",
                value=f"<t:{joined_at}:d> (<t:{joined_at}:R>)",
                inline=True,
            )
            .add_field(
                name="Roles",
                value=", ".join(r.mention for r in roles),
                inline=False,
            )
        )

        await ctx.respond(embed)


def load(bot: lightbulb.Bot) -> None:
    bot.add_slash_command(Userinfo)

import typing
import hikari
import lightbulb
from lightbulb import slash_commands

class Createcategory(lightbulb.SlashCommand):
    description = "Create a new channel with the added name."

    text: str = slash_commands.Option("New category name")

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        guild = ctx.get_guild()
        name = ctx.options.text
        await guild.create_category(name=name)

        await ctx.respond("New category created: #" + name)

def load(bot: lightbulb.Bot) -> None:
    bot.add_slash_command(Createcategory)


import typing
import hikari
import lightbulb
from lightbulb import slash_commands

class Createchannel(lightbulb.SlashCommand):
    description = "Create a new channel with the added name."

    text: str = slash_commands.Option("new channel name")

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        guild = ctx.get_guild()
        name = ctx.options.text
        await guild.create_text_channel(name=name)

        await ctx.respond("New channel created: #" + name)

def load(bot: lightbulb.Bot) -> None:
    bot.add_slash_command(Createchannel)

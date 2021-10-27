import typing
import hikari
import lightbulb
from lightbulb import slash_commands

class Showchannels(lightbulb.SlashCommand):
    description = "Show all channels in this server"

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        guild = ctx.get_guild()
        nom = ctx.options.text

# Note: find way to print channel names
        channels = list(str(i) for i in guild.get_channels())
        await ctx.respond('\n'.join(channels))        

def load(bot: lightbulb.Bot) -> None:
    bot.add_slash_command(Showchannels)

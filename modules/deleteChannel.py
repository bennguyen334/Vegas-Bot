import typing
import hikari
import lightbulb
from lightbulb import slash_commands

class Deletechannel(lightbulb.SlashCommand):
    description = "Create a new channel with the added name."

    channel: hikari.TextableChannel = slash_commands.Option("Channel to yeet")

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        guild = ctx.get_guild()
        #channel_name = ctx.options.channel.name
        await guild.delete_channel(ctx.options.channel)
        await ctx.respond(str(ctx.options.channel) + " deleted")


def load(bot: lightbulb.Bot) -> None:
    bot.add_slash_command(Deletechannel)


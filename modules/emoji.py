import hikari
import lightbulb
from lightbulb import slash_commands

class Printemoji(lightbulb.SlashCommand):
    description = "Prints an emoji"
    
    emoji: str = lightbulb.Option("Emoji to print")
    
    async def callback(self, ctx):
        await ctx.respond(ctx.options.emoji)

def load(bot: lightbulb.Bot) -> None:
    bot.add_slash_command(Printemoji)

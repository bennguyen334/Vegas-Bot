import hikari
import lightbulb
from lightbulb import slash_commands

class Play(lightbulb.SlashCommandGroup):
    description = "Play whatever game you choose"
    foo: hikari.Snowflake = Option("Pick a game")

@Play.subcommand()
class Baccarat(lightbulb.SlashSubCommand):
    description = "Classic game of Baccarat"
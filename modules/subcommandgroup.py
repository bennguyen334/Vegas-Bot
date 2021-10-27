import lightbulb
import hikari
from lightbulb import slash_commands

class Foo(lightbulb.SlashCommandGroup):
    description = "Test slash command group."

@Foo.subcommand()
class Bar(lightbulb.SlashSubCommand):
    description = "Test subcommand."

    baz: str = lightbulb.Option("Test subcommand option.")

    async def callback(self, context):
        await context.respond(context.options.baz)

def load(bot: lightbulb.Bot) -> None:
    bot.add_slash_command(Foo)

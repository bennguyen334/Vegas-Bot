import hikari
from hikari.events.message_events import MessageCreateEvent
import lightbulb
from lightbulb import plugins
from testbot.bot import Bot
import logging

class ErrorHandler(lightbulb.Plugin):
    @plugins.listener()
    async def on_command_error(self, event: lightbulb.CommandErrorEvent) -> None:
        if isinstance(event.exception, lightbulb.errors.CommandNotFound):
            return 

        if isinstance(event.exception, lightbulb.errors.NotEnoughArguments):
            return await event.context.respond(
                "There are some missing arguments: " + ", ".join(event.exception.missing_args)
                )

        if isinstance(event.exception, lightbulb.errors.TooManyArguments):
            return await event.context.respond("Too many arguments were passed.")

        if isinstance(event.exception, lightbulb.errors.CommandIsOnCooldown):
            return await event.context.respond("Command is on cooldown. Try again in {event.exception.retry_after:.0f} second(s)."
            )

        await event.context.respond("Invalid command.")
        raise event.exception


def load(bot: Bot) -> None:
    bot.add_plugin(ErrorHandler())


def unload(bot: Bot) -> None:
    bot.remove_plugin("ErrorHandler")
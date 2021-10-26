from __future__ import annotations

import logging
from pathlib import Path

#from typing import AsyncContextManager, AsyncIterator
import asyncio 

import hikari
from hikari.events import reaction_events
from hikari.events.guild_events import GuildAvailableEvent
import lightbulb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from testbot import __version__

class Bot(lightbulb.Bot):
    def __init__(self) -> None:
        self._extensions = [p.stem for p in Path("./testbot/bot/extensions/").glob("*.py")]
        self.scheduler = AsyncIOScheduler() 
        self.scheduler.configure(timezone=utc)
    
        with open("./secrets/token", mode="r", encoding="utf-8") as f:
            token = f.read().strip("\n")
        super().__init__(
            prefix = "-",
            insensitive_commands = True,
            token=token,
            intents=hikari.Intents.ALL,
        )


    def run(self) -> None:       
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)  

        super().run(
            activity=hikari.Activity(
                name=f"-help | Version {__version__}", 
                type=hikari.ActivityType.WATCHING
                )
        )

    async def on_starting(self, event: hikari.StartingEvent) -> None:
        for ext in self._extensions:
           self.load_extension(f"testbot.bot.extensions.{ext}")
        logging.info(f" {ext} extension loaded") 

    async def on_started(self, event: hikari.StartedEvent) -> None:
        self.scheduler.start()
        logging.info("BOT READY!")

    async def on_stopping(self, event: hikari.StoppingEvent) -> None:
        self.scheduler.shutdown()

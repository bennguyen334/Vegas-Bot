from hikari.events.reaction_events import GuildReactionAddEvent
import hikari, asyncio
class Utils:
    def __init__(self, bot):
        self.bot = bot
    
    # waits for a reaction from user_id, on a message with message_id, with an emoji in emojis. Will timeout after timeout seconds and print timeoutmsg
    async def waitForReaction(self,reaction: GuildReactionAddEvent, event: hikari.GuildMessageCreateEvent, message_id, user_id, emojis, timeoutmsg = "Timeout", timeout=60):
        while reaction.user_id != user_id or reaction.message_id != message_id or reaction.emoji_name not in emojis:
                        try:
                            reaction = await self.bot.wait_for(GuildReactionAddEvent, timeout)
                        except asyncio.TimeoutError:
                            await event.message.respond(timeoutmsg)
                            return None
        return reaction

    #wait for a message from user_id
    async def waitForMessage(self,event: hikari.GuildMessageCreateEvent, user_id, timeoutmsg = "Timeout", timeout=60):
        try:
                msg = await self.bot.wait_for(hikari.GuildMessageCreateEvent, timeout)
        except asyncio.TimeoutError:
                await event.message.respond(timeoutmsg)
                return None
        #print(msg.message)
        while msg.author_id != user_id:
                        try:
                            msg = await self.bot.wait_for(hikari.GuildMessageCreateEvent, timeout)
                        except asyncio.TimeoutError:
                            await event.message.respond(timeoutmsg)
                            return None
        return msg
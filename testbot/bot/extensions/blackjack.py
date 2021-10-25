import random
from asyncio.tasks import wait_for
from hikari import channels, snowflakes, events
import hikari
from hikari import emojis
from hikari.api.cache import CacheView
from hikari.embeds import Embed
from hikari.emojis import Emoji
from hikari.events import guild_events
from hikari.events import reaction_events
from hikari.events.lifetime_events import StartingEvent
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.events.reaction_events import GuildReactionAddEvent, ReactionAddEvent, ReactionEvent
from hikari.guilds import Guild
from hikari.interactions.base_interactions import MESSAGE_RESPONSE_TYPES
from hikari.messages import Reaction
import lightbulb
from testbot.bot import Bot
import pydealer as pd
from typing import *
import asyncio
import typing

class Card:
    suits = ["diamonds", "hearts", "clubs", "spades"]
    def __init__(self, suit: str, value: int, down = True):
        self.down = down
        self.value = value
        self.suit = suit
        self.symbol = self.faceCardNumber[0].upper()

    def flip(self):
        self.down = not self.down
        return self

    @property
    def faceCardNumber(self) -> str:
        if self.value <= 10:
            return str(self.value)
        else:
            return {
                11: "jack",
                12: "queen",
                13: "king",
                14: "ace"
            }[self.value]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'{self.faceCardNumber.title()} of {self.suit.title}'

#-------------------------------------------------------------------------
class Blackjack():
    def __init__(self, client: lightbulb.Plugin):
        self.client = client

    def calculate(hand: List[List[Card]]) -> int:
        noAce = [card for card in hand
                    if card.symbol != 'A']
        ace = [card for card in hand
                    if card.symbol == 'A']
        sum = int

        for card in ace:
            if not card.down:
                if sum <= 10:
                    sum = sum + 11
                else:
                    sum = sum + 1

        for card in noAce:
            if not card.down:
                    if card.symbol in 'JQK':
                        sum = sum + 10
                    else:
                        sum = sum + card.value
        return sum
class Blackjack(lightbulb.Plugin):
    def calculate(hand: List[List[Card]]) -> int:
        ace = [card for card in hand
                    if card.symbol == 'A']
        noAce = [card for card in hand
                    if card.symbol != 'A']
        sum = 0

        for Card in ace:
            if Card.down:
                if sum <= 10:
                    sum = sum + 11
                else:
                    sum = sum + 1

        for Card in noAce:
            if Card.down:
                    if Card.symbol in 'JQK':
                        sum = sum + 10
                    else:
                        sum = sum + Card.value
        
        return sum
        print ("test")

    def show(hand: List[List[Card]]) -> list:
        holder = []
        for x in hand:
            if(not x.down):
                temp = ["HIDDEN"]
            elif(x.value == 11):
                temp = ["Jack of ", x.suit]
            elif(x.value == 12):
                temp = ["Queen of ", x.suit]
            elif(x.value == 13):
                temp = ["King of ", x.suit]
            elif(x.value == 14):
                temp = ["Ace of ", x.suit]
            else:
                temp = [x.value, " of ", x.suit]
            holder.append(temp)
        return holder

    @lightbulb.command(name="blackjack", aliases=("bj",))
    async def game(self, ctx: lightbulb.Context):

        deck = [Card(suit, num) for num in range (2,15) for suit in Card.suits]
        random.shuffle(deck)
        dealer: List[Card] = []
        player: List[Card] = []
        Stop = False

        player.append(deck.pop())
        dealer.append(deck.pop().flip())
        player.append(deck.pop())
        dealer.append(deck.pop())     

#        while (Stop == False):
        playerSum = Blackjack.calculate(player)
        dealerSum = Blackjack.calculate(dealer)
        msg = [player, dealer]
        await ctx.respond(f"Player Cards:\n{Blackjack.show(player)}\nPlayer Sum: {playerSum}")
        await ctx.respond(f"Dealer Cards:\n{Blackjack.show(dealer)}\nDealer Sum: {dealerSum}")

        if playerSum == 21:
            msg = "You won!"
#            break

        elif playerSum > 21:
            msg = "You lost!"
#            break

        msg = await ctx.respond("Hit or SKIP")
        await msg.add_reaction("🇭")
        await msg.add_reaction("🇸")

        async def waitForReaction(reaction: GuildReactionAddEvent, event: hikari.GuildMessageCreateEvent, message_id, user_id, emojis, 
        timeoutmsg = "Timeout", timeout=60):
            while reaction.user_id != user_id or reaction.message_id != message_id or reaction.emoji_name not in emojis:
                try:
                    reaction = await Bot.wait_for(GuildReactionAddEvent, timeout)
                except asyncio.TimeoutError:
                    await event.message.respond(timeoutmsg)
                    return None
            return reaction

#        if await waitForReaction(GuildReactionAddEvent, GuildMessageCreateEvent, msg.id, msg.author.id, msg.reactions, timeoutmsg, timeout) == "🇭":
#            print("Hello")

#            try: 
#               emoji = events.ReactionAddEvent.is_for_emoji(msg)
#            except asyncio.TimeoutError:
#               await ctx.respond()

#            if events.ReactionAddEvent.is_for_emoji(msg, "🇭"):
#               player.append(deck.pop())
#               await msg.delete()
#               continue
#           elif events.ReactionAddEvent.is_for_emoji(msg, "🇸"):
#              Stop = True

#    if Stop:
        dealer[1].flip()
        playerSum = Blackjack.calculate(player)    
        dealerSum = Blackjack.calculate(dealer)

        while dealerSum < 17:
            dealer.append(deck.pop())
            dealerSum=Blackjack.calculate(dealer)

        if dealerSum == 21:
            msg = "Dealer Blackjack, you lost!"
        elif dealerSum > 21:
            msg = "Dealer Busts, you won!"
        elif dealerSum == playerSum:
            msg = "Tie, no winner"
        elif dealerSum > playerSum:
            msg = "You lost!"
        elif dealerSum < playerSum:
            msg = "You won"


def load(bot: Bot) -> None:
    bot.add_plugin(Blackjack())

def unload(bot: Bot) -> None:
    bot.remove_plugin("Blackjack")
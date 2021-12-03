import random
from asyncio.tasks import wait_for
import hikari
import hikari.api.cache 
from hikari.embeds import Embed
from hikari.events.message_events import GuildMessageCreateEvent, MessageCreateEvent
from hikari.events.reaction_events import GuildReactionAddEvent 
from hikari.interactions.base_interactions import MESSAGE_RESPONSE_TYPES
from hikari.messages import Message
#import lightbulb
#from bot import Bot
import pydealer as pd
from typing import *
import asyncio
from hikari.embeds import Embed
import time
import sqlite3
#-----------------------------------------------------------------------
class Error(Exception):
    pass
class notInteger(Error):
    pass
#------------------------------------------------------------------------
#class to handle cards and their elements
class Card:
    suits = ["♢", "♡", "♧", "♤"]
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
class Blackjack:
#calculate the sum of the hand
#check if any card is an Ace
    def calculate(hand: List[List[Card]]) -> int:
        ace = [card for card in hand
                    if card.symbol == 'A']
        noAce = [card for card in hand
                    if card.symbol != 'A']
        sum = 0

#return the respective values for all cards except ace
        for Card in noAce:
            if Card.down:
                    if Card.symbol in 'JQK':
                        sum = sum + 10
                    else:
                        sum = sum + Card.value

#condition for Ace sum
        for Card in ace:
            if Card.down:
                if sum <= 10:
                    sum = sum + 11
                else:
                    sum = sum + 1

        return sum

#print function to show user's card in hand
    def show(hand: List[List[Card]]) -> list:
        holder = []
        for x in hand:
            if(not x.down):
                temp = ["HIDDEN"]
            elif(x.value == 11):
                temp = [f"Jack of {x.suit}"]
            elif(x.value == 12):
                temp = [f"Queen of {x.suit}"]
            elif(x.value == 13):
                temp = [f"King of {x.suit}"]
            elif(x.value == 14):
                temp = [f"Ace of {x.suit}"]
            else:
                temp = [f"{x.value} of {x.suit}"]
            holder.append(temp)

        return holder
#------------------------------------------------------------------
#actual program: initiated with -bj or -blackjack
#    @lightbulb.command(name="blackjack", aliases=("bj",))
    async def game(self, event: GuildMessageCreateEvent, ctx):

#function to help with reactions (from slot.py)
        async def waitForReaction(reaction: GuildReactionAddEvent, event: hikari.GuildMessageCreateEvent, message_id, user_id, emojis, 
                                    timeoutmsg = "Blackjack Timeout.\nPlayer did not make a choice in 30 seconds.", timeout = 30):
            while reaction.user_id != user_id or reaction.message_id != message_id or reaction.emoji_name not in emojis:
                try:
                    reaction = await ctx.bot.wait_for(hikari.GuildReactionAddEvent, timeout)
                except asyncio.TimeoutError:
                    await event.message.respond(timeoutmsg)
                    return None
            return reaction

        async def waitForChange(amount: GuildMessageCreateEvent, event: hikari.GuildMessageCreateEvent, user_id,
                                    timeoutmsg = "Blackjack Timeout.\nPlayer did not insert new amount in 30 seconds.", timeout = 30):
            while amount.author_id != user_id:
                try:
                    amount = await ctx.bot.wait_for(hikari.GuildMessageCreateEvent, timeout)
                    if not isinstance(int(amount.content), int):
                        raise notInteger
                except asyncio.TimeoutError:
                    await event.message.respond(timeoutmsg)
                    return None
                except notInteger:
                    await event.message.respond("Numbers only. Exiting Game")
                    return None
            return amount



#connect to database
        connection = sqlite3.connect('VegasBot.db')
        cursor = connection.cursor()
#find if the author is in the database
        #cursor.execute("SELECT usernameID FROM Users WHERE usernameID = ?", (event.message.author.id,))
        cursor.execute("SELECT userID From Users WHERE userID = ?", (event.message.author.id,))
        data = cursor.fetchall()
#if not in database, add to database with a set amount of money given
        if len(data) == 0:
            cursor.execute("INSERT INTO Users (userID, balance) VALUES (?, ?)", (event.message.author.id, 10000))
            connection.commit()
        cursor.execute("SELECT balance FROM Users WHERE userID = ?", (event.message.author.id,))
        data = cursor.fetchall()
        balance = data[0]


        ## Take in bet here!
        embed = Embed(title=f"Type in your initial bet",
                    description=f"User Balance: {balance[0]}", color = 0x2acaea)
        embed.set_author(name=event.message.author.username, icon = event.message.author.avatar_url)
        emb = await event.message.respond(embed)
        userBet = GuildMessageCreateEvent
        userBet = await waitForChange(userBet, event, event.message.author.id,
                                        timeoutmsg="Blackjack Timeout.\nPlayer did not insert initial amount in 30 seconds.", timeout=30)
        if userBet is None:
            await emb.delete()
            return
# #compare bet with current balance, exit if bet exceeds current balance
        # cursor.execute("SELECT balance FROM Users WHERE userID = ?", (event.message.author.id,))
        # data = cursor.fetchall()
        # balance = data[0]

        userBet = int(userBet.content)
        if (balance[0] < userBet):
            embeded = Embed(title=f"Bet Amount Exceeds User's Current Balance.\nExiting Game", 
                            description=f"User Balance: {balance[0]}\nCurrent Bet: {userBet}\n", color = 0x2acaea)
            embeded.set_author(name=event.message.author.username, icon = event.author.avatar_url)
            emb = await event.message.respond(embeded)
            return

#prompt user beginning message and emotes
        embeded = Embed(title=f"Welcome to Blackjack.\nCurrent Balance: {balance[0]}\nCurrent Bet: {userBet}", 
                            description="Press 🇧 to start.\nPress 🇶 to quit.\nPress 🇲 to change bet amount.", color = 0x2acaea)
        embeded.set_author(name=event.message.author.username, icon = event.author.avatar_url)
        emb = await event.message.respond(embeded)
        startEmote = ['🇧','🇶','🇲']
        for emoji in startEmote:
            await emb.add_reaction(emoji[0])

#wait for reaction, if no reaction then delete beginning message and timeout
        reaction = GuildReactionAddEvent
        while(True):
            reaction = await waitForReaction(reaction, event, emb.id, event.message.author.id, ['🇧', '🇶', '🇲'])
            await emb.delete()
            if reaction == None:
                return

            if reaction.emoji_name == '🇲':
                cursor.execute("SELECT balance FROM Users WHERE userID = ?", (event.message.author.id,))
                data = cursor.fetchall()
                balance = data[0]
                embeded = Embed(title= "Bet Change", 
                                    description=f"Type your new bet amount.\nYour current balance is: {balance[0]}\nYour current bet is: {userBet}", color = 0x2acaea)
                embeded.set_author(name=event.message.author.username, icon = event.message.author.avatar_url)
                emb = await event.message.respond(embeded)

                changeAmount = GuildMessageCreateEvent
                changeAmount = await waitForChange(changeAmount, ctx, event.message.author.id)
                if changeAmount == None:
                    await emb.delete()
                    return

        #check database for amount
                cursor.execute("SELECT balance FROM Users WHERE userID = ? AND balance > ?", (event.message.author.id, int(changeAmount.content)))
                data = cursor.fetchall()
                userBet = data[0]
                await emb.delete()
                if len(data) == 0:
                    embeded = Embed(title = f"Cannot change amount. Your current bet is {userBet}", 
                                        description= "Press 🇧 to start.\nPress 🇶 to quit.\nPress 🇲 to change bet amount.", color = 0x2acaea)
                else:
                    userBet = changeAmount.content
                    embeded = Embed(title=f"Bet Amount Change to {userBet}", 
                                        description = "Press 🇧 to start.\nPress 🇶 to quit.\nPress 🇲 to change bet amount.", color = 0x2acaea )
                emb = await event.message.respond(embeded)
                startEmote = ['🇧','🇶','🇲']
                for emoji in startEmote:
                    await emb.add_reaction(emoji[0])
                continue

        #if reaction is Q for quit, prompt exit message
            if reaction.emoji_name == '🇶':
                embeded = Embed(title="Exiting Blackjack", description = "Goodbye!")
                embeded.set_author(name=event.message.author.username, icon = ctx.author.avatar_url)
                emb = await event.message.respond(embeded)
                return

            if reaction.emoji_name == '🇧':
                break

#loop that continues as long as player presses B at beginning message or P during games
        while reaction.emoji_name == '🇧' or reaction.emoji_name == '🇵':

#create deck, shuffle, make two list for user and dealer, give cards and calculate current hand
            deck = [Card(suit, num) for num in range (2,15) for suit in Card.suits]
            random.shuffle(deck)
            dealer: List[Card] = []
            player: List[Card] = []

            player.append(deck.pop())
            dealer.append(deck.pop().flip())
            player.append(deck.pop())
            dealer.append(deck.pop())     
            playerSum = Blackjack.calculate(player)
            dealerSum = Blackjack.calculate(dealer)

#loop continues until break. Prompt user each person's card and their sum then prompt three options
            while(int(userBet) < int(balance[0])):
#                print (userBet, balance[0])
                embeded = Embed(title = "Blackjack", description = f"Player Cards:\n{Blackjack.show(player)}\nDealer Cards:"
                                f"\n {Blackjack.show(dealer)}\nPlayer Sum: {playerSum}\nDealer Sum: {dealerSum}\nHit, Skip, or Quit", color = 0x2acaea)
                embeded.set_author(name=event.message.author.username, icon = ctx.author.avatar_url)
                emb = await event.message.respond(embeded)

                optionEmote = ["🇭","🇸","🇶"]

                for emoji in optionEmote:
                    await emb.add_reaction(emoji[0])
                
                reaction = await waitForReaction(reaction, event, emb.id, event.message.author.id, ["🇭","🇸","🇶"], 
                                                    "Blackjack Timeout.\nPlayer did not make a choice in 30 seconds.", 30)
                await emb.delete()

#timeout if none, if H then give a card to player, calculate, and if >= 21 break.
                if reaction == None:
                    return
                if reaction.emoji_name == '🇭':
                    player.append(deck.pop())
                    playerSum = Blackjack.calculate(player)
                    if playerSum >= 21:
                        break

#if S then break out of loop and continue to dealer's turn
                elif reaction.emoji_name == '🇸':
                    break

#if Q then break out of loop and end game with prompted message
                elif reaction.emoji_name == '🇶':
                    embeded = Embed(title="Quitted Blackjack", description = "Goodbye!", color = 0x2acaea)
                    emb = await event.message.respond(embeded)
                    return

#flip dealer's first card and update the sum
            dealer[0].flip()
            dealerSum = Blackjack.calculate(dealer)

#resulted in bust
            if playerSum > 21:
                result = Embed(title = "You Bust!", description = "You Lost!", color = 0x2acaea)
                result.set_author(name=event.message.author.username, icon = ctx.author.avatar_url)
                cursor.execute("UPDATE Users SET Balance = Balance - ? WHERE usernameID = ?", (userBet, event.message.author.id))
#if player didn't bust, do dealer's turn and calculate hand
            else:    
                while dealerSum < 17:
                    dealer.append(deck.pop())
                    dealerSum=Blackjack.calculate(dealer)

#conditions for win and lost, print result
                if dealerSum == 21:
                    result = Embed(title = "Dealer Blackjack", description = "You Lost!", color = 0x2acaea)
                    cursor.execute("UPDATE Users SET Balance = Balance - ? WHERE usernameID = ?", (userBet, event.message.author.id))
                elif dealerSum > 21:
                    result = Embed(title = "Dealer Bust", description = "You Won!", color = 0x2acaea)
                    cursor.execute("UPDATE Users SET Balance = Balance + ? WHERE usernameID = ?", (userBet, event.message.author.id))
                elif dealerSum == playerSum:
                    result = Embed(title = "Tie Between Dealer and Player", description = "No Winner", color = 0x2acaea)
                elif dealerSum > playerSum:
                    result = Embed(title = "Dealer Values More Than Player", description = "You Lost!", color = 0x2acaea)
                    cursor.execute("UPDATE Users SET Balance = Balance - ? WHERE usernameID = ?", (userBet, event.message.author.id))
                elif dealerSum < playerSum:
                    result = Embed(title = "Player Values More Than Dealer", description = "You Won!", color = 0x2acaea)
                    cursor.execute("UPDATE Users SET Balance = Balance + ? WHERE usernameID = ?", (userBet, event.message.author.id))
                result.set_author(name=event.message.author.username, icon = ctx.author.avatar_url)


            results = await event.message.respond(result)
            connection.commit()
#update balance and current user's bet
            cursor.execute("SELECT Balance FROM Users WHERE usernameID = ?", (event.message.author.id,))
            data = cursor.fetchall()
            balance = data[0]

#reprint the final message for each person's card and hand
            embeded = Embed(title = f"Blackjack\nCurrent Balance: {balance[0]}\nCurrent Bet: {userBet}", 
                                        description = f"Player Cards:\n{Blackjack.show(player)}\nDealer Cards:\n {Blackjack.show(dealer)}\n"
                                                        f"Player Sum: {playerSum}\nDealer Sum: {dealerSum}\nPress 🇵 to play again.\n"
                                                            f"Press 🇶 to quit.\nPress 🇲 to change bet.", color = 0x2acaea)
            embeded.set_author(name=event.message.author.username, icon = ctx.author.avatar_url)
            emb = await event.message.respond(embeded)
            endEmote = ['🇵','🇶', '🇲']
            for emoji in endEmote:
                await emb.add_reaction(emoji[0])

#wait for a reaction from end message, timeout for None, quit game for Q, and reset game for P
            reaction = GuildReactionAddEvent
            reaction = await waitForReaction(reaction, event, emb.id, event.message.author.id, ['🇵', '🇶', '🇲' ], "Blackjack Timeout. Goodbye!", 30)
            flagPass = 0

            if int(userBet) > int(balance[0]):
                exit = Embed(title = "Current Bet Amount Exceeds User's Balance.", description = "Exiting game.", color = 0x2acaea)
            while(int(userBet) <= int(balance[0])):
                if flagPass == 0:
                    await results.delete()
                await emb.delete()

                if reaction == None:
                    return

                if reaction.emoji_name == '🇵' or reaction.emoji_name == '🇧':
                    break

                if reaction.emoji_name == '🇶':
                    embeded = Embed(title ="Exiting Blackjack", description = f"Current Balance: {balance[0]}", color = 0x2acaea)
                    embeded.set_author(name=event.message.author.username, icon = ctx.author.avatar_url)
                    emb = await event.message.respond(embeded)   
                    break

                if reaction.emoji_name == '🇲':
                    flagPass = 1
                    cursor.execute("SELECT Balance FROM Users WHERE usernameID = ?", (event.message.author.id,))
                    data = cursor.fetchall()
                    balance = data[0]
                    embeded = Embed(title= "Bet Change", description=f"Type your new bet amount.\nYour current balance is: {balance[0]}\n"
                                            f"Your current bet is: {userBet}", color = 0x2acaea)
                    embeded.set_author(name=event.message.author.username, icon = ctx.author.avatar_url)
                    emb = await event.message.respond(embeded)

                    changeAmount = GuildMessageCreateEvent
                    changeAmount = await waitForChange(changeAmount, ctx, event.message.author.id)
                    if changeAmount == None:
                        await emb.delete()
                        return

                    cursor.execute("SELECT Balance FROM Users WHERE usernameID = ? AND Balance > ?", (event.message.author.id, int(changeAmount.content)))
                    data = cursor.fetchall()
                    userBet = data[0]
                    await emb.delete()
                    if len(data) == 0:
                        embeded = Embed(title = f"Cannot change amount. Your current bet is {userBet}", 
                                                description= "Press 🇧 to start.\nPress 🇶 to quit.\nPress 🇲 to change bet amount.", color = 0x2acaea)
                    else:
                        userBet = changeAmount.content
                        embeded = Embed(title=f"Bet Amount Change to {userBet}", 
                                            description = "Press 🇧 to start.\nPress 🇶 to quit.\nPress 🇲 to change bet amount.", color = 0x2acaea )
                    emb = await event.message.respond(embeded)
                    startEmote = ['🇧','🇶','🇲']
                    for emoji in startEmote:
                        await emb.add_reaction(emoji[0])

                reaction = await waitForReaction(reaction, event, emb.id, event.message.author.id, ['🇧', '🇶', '🇲' ], "Blackjack Timeout. Goodbye!", 30)

        connection.close()

# def load(bot: lightbulb.Bot) -> None:
#     bot.add_plugin(Blackjack())

# def unload(bot: lightbulb.Bot) -> None:
#     bot.remove_plugin("Blackjack")

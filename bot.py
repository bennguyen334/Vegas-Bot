#<<<<<<< HEAD
import hikari
import lightbulb


with open("./secrets/token", "r") as f:
    token = f.read().strip()

bot = lightbulb.Bot(
    token,
    prefix="-",
    banner=None,
    intents=hikari.Intents.ALL,
    default_enabled_guilds=(885224908030873601,),
    logs={
        "version": 1,
        "incremental": True,
        "loggers": {
            "hikari": {"level": "INFO"},
            "hikari.ratelimits": {"level": "TRACE_HIKARI"},
            "lightbulb": {"level": "DEBUG"},
        },
    }
)

#@bot.listen()
#async def ping(ctx: lightbulb.Context) -> None:
#    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")

@bot.listen()
async def echo(ctx: lightbulb.Context) -> None:
    await bot.handle(hikari.DMMessageCreateEvent)
    await ctx.respond(ctx.content[5:])

bot.load_extensions_from("./modules/", must_exist=True)
#=======
import asyncio
from logging import PlaceHolder
import re
import random
import time
import hikari
from hikari import embeds
from hikari import emojis
from hikari.api.cache import Cache
from hikari.embeds import Embed
from hikari.emojis import UnicodeEmoji
from hikari.events import message_events, reaction_events
from hikari.events.reaction_events import GuildReactionAddEvent
from hikari.users import PartialUser
from treys import Card, Deck, Evaluator
import emoji

#bot = hikari.GatewayBot(token="ODk1MDU2ODU3NTE1ODI3MjY5.YVzAqA.K2820a3KEUxp672BjnRvFEuyzuY")


class Poker_Player:
    def __init__(self, user, balance: int = 0, betAmt: int = 0,hand: list = [], folded: bool = False):
        self.user = user
        self.balance = balance
        self.folded = folded
        self.hand = hand
        self.betAmt = betAmt

@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    # If a non-bot user sends a message "hk.ping", respond with "Pong!"
    # We check there is actually content first, if no message content exists,
    # we would get `None' here.
    if event.is_bot or not event.content:
        return

    if event.content.startswith("hk.ping"):
        await event.message.respond("Pong!")

#waits for a reaction from user_id, on a message with message_id, with an emoji in emojis. Will timeout after timeout seconds and print timeoutmsg
async def waitForReaction(reaction: GuildReactionAddEvent, event: hikari.GuildMessageCreateEvent, message_id, user_id, emojis, timeoutmsg = "Timeout", timeout=60):
    while reaction.user_id != user_id or reaction.message_id != message_id or reaction.emoji_name not in emojis:
                    try:
                        reaction = await bot.wait_for(GuildReactionAddEvent, timeout)
                    except asyncio.TimeoutError:
                        await event.message.respond(timeoutmsg)
                        return None
    return reaction

#wait for a message from user_id
async def waitForMessage(event: hikari.GuildMessageCreateEvent, user_id, timeoutmsg = "Timeout", timeout=60):
    try:
            msg = await bot.wait_for(hikari.GuildMessageCreateEvent, timeout)
    except asyncio.TimeoutError:
            await event.message.respond(timeoutmsg)
            return None
    #print(msg.message)
    while msg.author_id != user_id:
        try:
            msg = await bot.wait_for(hikari.GuildMessageCreateEvent, timeout)
            except asyncio.TimeoutError:
                await event.message.respond(timeoutmsg)
                return None
    return msg


@bot.listen()
async def slots(event: hikari.GuildMessageCreateEvent) -> None:
    """ activates single-player slot machine game in current channel"""
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-play slots":
        # Print welcome prompt
        embed = Embed(title="Welcome to the slot machine!", description="Press 🎰 to play!\nPress 📝 to see payouts")
        emb = await event.message.respond(embed) # Print message to channel
        await emb.add_reaction('🎰') # Add reactions to message
        await emb.add_reaction('📝')

        # Await user input via clicking on reactions
        reaction = GuildReactionAddEvent
        reaction = await waitForReaction(reaction, event, emb.id, event.message.author.id, ['🎰', '📝'])
        if reaction == None:
            return
       
        payoutsEmbed = Embed(title = "Payouts", description="Here are the 10 symbols in the slot machine:\n🍒 7️⃣ 💰 🎱 🎲 💸 🔔 🍊 🃏 🏇")
        payoutsEmbed.add_field(name="Winning Combinations", value="""One 7️⃣: Wager x 0.2\nPair of any symbol: Wager x 1\nThree of any symbol: Wager x 2
                                Pair of 7️⃣: Wager x 3\nThree 7️⃣ (Jackpot): Wager x 10\n""")
        payoutsEmbed.add_field(name="Ready to play?", value = "Press 🎰!")

        if reaction.emoji_name == '📝':
            pemb = await event.message.respond(payoutsEmbed)

            await pemb.add_reaction('🎰')
            reaction = GuildReactionAddEvent
            reaction = await waitForReaction(reaction, event, pemb.id, event.message.author.id, ['🎰'])
            if reaction == None:
                return

        while(True):
            wagerMsg = await event.message.respond("How much would you like to wager? 💸 = 5, 💵 = 10, 🤑 = 25, 💰 = 50\n")
            wagerEmojis = [('💸', 5), ('💵', 10), ('🤑', 25), ('💰', 50)]
            
            for emoji in wagerEmojis:
                await wagerMsg.add_reaction(emoji[0])

            reaction = GuildReactionAddEvent
            reaction = await waitForReaction(reaction, event, wagerMsg.id, event.message.author.id, ['💸','💵','🤑','💰'], "You never entered a wager, aborting.", 60)
            if reaction == None:
                return
            wager =0
            for possibleWager in wagerEmojis:
                if reaction.emoji_name == possibleWager[0]:
                    wager = possibleWager[1]
                    break
            
            payout = await slot_helper(event, wager)
            if payout > 0:
                msg = "You won " + str(payout) +"! To play again press 🎰"
            else:
                msg = "Sorry, you didn't win. Better luck next time! To play again press 🎰"
            mesg = await event.message.respond(msg)
            await mesg.add_reaction('🎰')

            reaction = GuildReactionAddEvent
            reaction = await waitForReaction(reaction, event, mesg.id, event.message.author.id, ['🎰'], "Goodbye, Thanks for playing!", 30)
            if reaction == None:
                return
        


async def slot_helper(event: hikari.GuildMessageCreateEvent, wager):
    emojis = ['🍒', '7️⃣', '💰', '🎱', '🎲', '💸', '🔔', '🍊', '🃏', '🏇']
    
    result = []
    payout=0
    for i in range(3):
        if i==2:
            time.sleep(1)
        else:
            time.sleep(0.5)
        rand = random.randint(0, len(emojis)-1)
        if i == 0:
            msg = await event.message.respond(emojis[rand])
        else:
            msg = await msg.edit(content = msg.content + emojis[rand])
        result.append(emojis[rand])

    if result.count('7️⃣') == 3:
        payout = wager * 10
    elif result.count('7️⃣') == 2: 
        payout = wager * 3
    elif result[0] == result[1] and result[1] == result[2]: #3 of the same symbol
        payout = wager * 2
    elif len(result) != len(set(result)): #pair of symbol
        payout = wager
    elif '7️⃣' in result:
        payout = wager * 0.2

    return payout

def make_card_string(cards: list):
    text = Card.print_pretty_cards(cards)
    text = emoji.demojize(text)
    text = text.replace('T', '10')
    text = text.replace(':club_suit:', ' of clubs')
    text = text.replace(':spade_suit:', ' of spades')
    text = text.replace(':heart_suit:', ' of hearts')
    text = text.replace(':diamond_suit:', ' of diamonds')
    return text

#returns true if need to continue playing after the betting round
async def betting_round(event: hikari.GuildMessageCreateEvent, players: list, pot, D, SB, BB, UTG, firstRound):
    currentPosition  =0
    goinloop = True

    #setting blind bets in first round
    if(firstRound):
        players[SB].betAmt = 1
        players[SB].balance -= 1
        players[BB].betAmt = 2
        players[BB].balance -= 2
        pot = 3

    #calculating current position
    if(firstRound):
            currentPosition = UTG
    else:
        for index, player in enumerate(players[D+1:]+players[:D+1]):
            if player.folded == False:
                currentPosition = index + 1 if index < len(players) -1 else 0
                break
    
    bboption = 0
    count = 0
    #while all bets aren't equal
    while [player.betAmt for player in players if player.folded == False].count(players[currentPosition].betAmt) != len([player for player in players if player.folded == False]) or goinloop or count < len(players):
        goinloop = False
        count += 1
        #check if everyone except 1 player folded
        if len([player for player in players if player.folded == False]) == 1:
            break
        
        #check if current positon is still in hand
        if players[currentPosition].folded == True:
            currentPosition = currentPosition + 1 if currentPosition != len(players)-1 else 0
            continue

        #printing current bet status
        statusMsg = "Current bets: "
        for i in range(len(players)):
            if i != 0:
                statusMsg += ', '
            statusMsg += str(players[i].user.username) + ': '
            statusMsg += str(players[i].betAmt) if players[i].folded == False else 'F'
        await event.message.respond(statusMsg)

        
        #calculating difference between current players bet and the previous players bet
        #if they're the same player can check or bet, if not player can call or bet
        difference = 0
        for i in range(currentPosition-1, -len(players)+currentPosition, -1):
            if players[i].folded == False:
                difference = abs(players[currentPosition].betAmt - players[i].betAmt)
                break

        options = ["check ✅, bet 💰, or fold ❌", "call for " + str(difference) + " ☎️, raise 🔼, or fold ❌"]
        emojis = [['✅', '💰', '❌'], ['☎️', '🔼', '❌']]
        #building and sending message to player with they're current betting options
        betMsg = str(players[currentPosition].user.username) + ': ' 
        betMsg += options[0] if difference == 0 else options[1]
        betMsgObj = await event.message.respond(betMsg)

        #getting the betting choice from the user through reactions
        reaction = GuildReactionAddEvent
        timeoutmsg = str(players[currentPosition].user.username) + ", you took too long. Folding."
        Fold = False
        if difference == 0:
            await betMsgObj.add_reaction(emojis[0][0])
            await betMsgObj.add_reaction(emojis[0][1])
            await betMsgObj.add_reaction(emojis[0][2])
            reaction = await waitForReaction(reaction, event, betMsgObj.id, players[currentPosition].user.id, emojis[0], timeoutmsg, 60)
            if reaction == None:
                Fold = True
        else:
            await betMsgObj.add_reaction(emojis[1][0])
            await betMsgObj.add_reaction(emojis[1][1])
            await betMsgObj.add_reaction(emojis[1][2])
            reaction = await waitForReaction(reaction, event, betMsgObj.id, players[currentPosition].user.id, emojis[1], timeoutmsg, 60)
            if reaction == None:
                Fold = True
        
        #doing the action the user specified, nothing happens on check so no function needed
        if reaction.emoji_name == emojis[0][1] or reaction.emoji_name == emojis[1][1]:#bet or raise
            await event.message.respond(str(players[currentPosition].user.username) + ", enter amount.")
            betAmtMsg = await waitForMessage(event, players[currentPosition].user.id, timeoutmsg)
            if betAmtMsg == None or not str(betAmtMsg.content).isnumeric():
                Fold = True
            else:
                if reaction.emoji_name == emojis[0][1]: #bet
                    players[currentPosition].betAmt += int(betAmtMsg.content)
                    pot += int(betAmtMsg.content)
                    players[currentPosition].balance -= int(betAmtMsg.content)
                else: #raise
                    players[currentPosition].betAmt += (difference + int(betAmtMsg.content))
                    pot += (difference + int(betAmtMsg.content))
                    players[currentPosition].balance -= (difference + int(betAmtMsg.content))
        elif reaction.emoji_name == emojis[1][0]: #call
            players[currentPosition].betAmt += difference
            pot += difference
            players[currentPosition].balance -= difference

        if Fold == True or reaction.emoji_name == emojis[0][2]: #Fold
            players[currentPosition].folded = True
        
        #calculates the amount a player that is still in the hand has bet, used for big blind check in first round
        not_folded_bet_amt = [player.betAmt for player in players if player.folded == False][0]

        #if it's the first round and all players called the original big blind bet, give the big blind the opportunity to raise
        if(firstRound and [player.betAmt for player in players if player.folded == False].count(not_folded_bet_amt) == len([player for player in players if player.folded == False]) and bboption == 0):
            goinloop = True
            bboption =1

        #go to next player
        currentPosition = currentPosition + 1 if currentPosition != len(players)-1 else 0
    
    if len([player for player in players if player.folded == False]) == 1:
        username = str([player for player in players if player.folded == False][0].user.username)
        endMsg = "All players except " +  username + ' folded. '
        await event.message.respond(endMsg)
        return (False, pot, username)
    else:
        curBets = ""
        balances = ""
        for i in range(len(players)):
            if i != 0:
                curBets += ', '
                balances += ', '
            curBets += str(players[i].user.username) + ': '
            curBets += str(players[i].betAmt) if players[i].folded == False else 'F'
            balances += str(players[i].user.username) + ': ' + str(players[i].balance)

        embed = Embed(title = "Betting round over", description='\u200b')
        embed.add_field(name = "Current Bets", value=curBets)
        embed.add_field(name = "Balances", value=balances)
        await event.message.respond(embed)
        return (True, pot, None)

@bot.listen()
async def poker(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-play poker":
        embed = Embed(title="Welcome to Poker!", description="Mention who you would like to play with to get started!")
        await event.message.respond(embed)
        msg = await waitForMessage(event, event.author_id)
        if msg == None:
            return
        if len(msg.message.mentions.user_ids) == 0 or event.author_id in msg.message.mentions.user_ids:
            await event.message.respond("You didn't mention anyone to play with, or you mentioned yourself. Exiting poker.")
            return

        #fetching user objects and building players list
        guild = event.get_guild()
        member = await bot.rest.fetch_member(guild, event.author_id)
        players = [] #list of poker_player objects
        players.append(Poker_Player(member.user))
        for id in msg.message.mentions.user_ids:
            member = await bot.rest.fetch_member(guild, id)
            players.append(Poker_Player(member.user))
        
        #building buy in message
        str1 = ""
        for player in players:
            str1 +=  str(player.user.username) + ', '
        str1 += "Enter your buy in amount."

        #sending buy in message
        await event.message.respond(str1)

        #waiting for all players to buy in
        buy_ins = set()
        while(len(buy_ins) != len(players)):
            binmsg = hikari.GuildMessageCreateEvent
            while binmsg.author_id not in [player.user.id for player in players] or not str(binmsg.content).isnumeric():
                try:
                    binmsg = await bot.wait_for(hikari.GuildMessageCreateEvent, 120)
                except asyncio.TimeoutError:
                    await event.message.respond("All players were not ready to play. Exiting poker.")
                    return
            buy_ins.add(binmsg.author_id)
            #updating players list with buy ins
            index = [player.user.id for player in players].index(binmsg.author_id)
            players[index].balance = int(binmsg.content)

        #shuffling player order so play isn't always in order mentioned by author
        random.shuffle(players)

        #creating card deck
        deck = Deck()
        #shuffling card deck    
        deck.shuffle()
        
        #Dealing to players
        for player in players:
            player.hand = deck.draw(2)
            await (await bot.rest.create_dm_channel(player.user.id)).send(make_card_string(player.hand))
        
        #set positon of dealer, small blind, big blind, UTG
        if len(players) > 3:
            D = 0
            SB = 1
            BB = 2
            UTG = 3
        elif len(players) == 3:
            D=0
            SB =1
            BB = 2
            UTG = 0
        elif len(players) == 2:
            D = 0
            SB = 0
            BB = 1
            UTG = 0
        
        pot = 0 #amt of money in pot
        
        #start of main loop

        #printing player order
        orderMsg = "Player order: "
        for i in range(len(players)):
            if i == D:
                orderMsg += "D "
            if i == SB:
                orderMsg += "SB "
            if i == BB:
                orderMsg += "BB "
            orderMsg += str(players[i].user.username)
            if i != len(players)-1:
                orderMsg += ', '
        await event.message.respond(orderMsg)
        
        keep_playing = True
        WinningUsername = None
        keep_playing, pot, WinningUsername = await betting_round(event, players, pot, D, SB, BB, UTG, True)
        if keep_playing:
            board = deck.draw(5)
            await event.message.respond("Flop: " + make_card_string(board[:3]))
            keep_playing, pot, WinningUsername = await betting_round(event, players, pot, D, SB, BB, UTG, False)
            if keep_playing:
                await event.message.respond("Turn: " + make_card_string(board[:4]))
                keep_playing, pot, WinningUsername = await betting_round(event, players, pot, D, SB, BB, UTG, False)
                if keep_playing:
                    await event.message.respond("River: " + make_card_string(board))
                    keep_playing, pot, WinningUsername = await betting_round(event, players, pot, D, SB, BB, UTG, False)
                    if keep_playing: #Final betting round
                        #evaluate hands
                        evaluator = Evaluator()
                        WinningScore = -1
                        WinningPlayer = PlaceHolder
                        handResultMsg = "Board: " + make_card_string(board) + '\n'
                        for player in [player for player in players if player.folded == False]:
                            handScore = evaluator.evaluate(board, player.hand)
                            hand_class = evaluator.get_rank_class(handScore)
                            if  handScore < WinningScore or WinningScore == -1:
                                WinningScore = handScore
                                WinningPlayer = player
                            handResultMsg += str(player.user.username) + "'s hand: " + make_card_string(player.hand) + ' Strength of Hand: ' + evaluator.class_to_string(hand_class) + '\n'
                        handResultMsg += WinningPlayer.user.username + ' wins ' + str(pot)
                        WinningPlayer.balance += pot
                        await event.message.respond(handResultMsg)
        if WinningUsername != None:
            handResultMsg = WinningUsername + ' wins ' + str(pot)
            for player in players:
                if player.user.username == WinningUsername:
                    player.balance += pot
            await event.message.respond(handResultMsg)
        balanceMsg = "Player balances: "
        for i, player in enumerate(players):
            balanceMsg += player.user.username + ' ' + str(player.balance)
            if i != len(players)-1:
                balanceMsg += ', '
        await event.message.respond(balanceMsg)
bot.run()
#>>>>>>> main

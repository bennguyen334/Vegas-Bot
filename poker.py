import hikari
from logging import PlaceHolder
from hikari.embeds import Embed
from hikari.events.reaction_events import GuildReactionAddEvent
import db, random, time, asyncio
from treys import Card, Deck, Evaluator
import emoji
from copy import deepcopy

DB = db.Db()

class Poker_Player:
    def __init__(self, user, balance: int = 0, betAmt: int = 0,hand: list = [], folded: bool = False, Allin: bool = False):
        self.user = user
        self.balance = balance
        self.folded = folded
        self.hand = hand
        self.betAmt = betAmt
        self.Allin = Allin

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
async def betting_round(event: hikari.GuildMessageCreateEvent, players: list, pot, D, ante, firstRound, tils):
    goinloop = True

    #setting ante bets in first round
    if(firstRound):
        for player in players:
            player.betAmt = ante
            player.balance -= ante
            pot += ante

    #calculating current position
    currentPosition = D + 1 if D+1 < len(players) else 0
    
    count = 0
    maxBet = max([player.betAmt for player in players])

    #all players not folded are all in, no need to bet
    if abs(len([player for player in players if player.Allin == True]) - len([player for player in players if player.folded == False])) <= 1:
        return (True, pot, None)

    #while all bets aren't equal
    while [player.betAmt for player in players if ((player.folded == False and player.Allin == False) or player.betAmt == maxBet)].count(players[currentPosition].betAmt) != len([player for player in players if ((player.folded == False and player.Allin == False) or player.betAmt == maxBet)]) or goinloop or count < len(players):
        goinloop = False
        count += 1

        #all players not folded are all in, no need to bet
        if len([player for player in players if player.Allin == True]) == len([player for player in players if player.folded == False]):
            return (True, pot, None)
        #check if everyone except 1 player folded
        if len([player for player in players if player.folded == False]) == 1:
            break
        
        #check if current positon is still in hand
        if players[currentPosition].folded == True:
            currentPosition = currentPosition + 1 if currentPosition != len(players)-1 else 0
            continue

        #printing current bet status
        
        statusMsg = ""
        for i in range(len(players)):
            if i != 0:
                statusMsg += ', '
            if i == D:
                statusMsg += 'D '
            statusMsg += str(players[i].user.username) + ': '
            if players[i].Allin == True:
                statusMsg += 'All In (' + str(players[i].betAmt) + ')'
            elif players[i].folded == True:
                statusMsg += 'F'
            else:
                statusMsg += str(players[i].betAmt)
        embed = Embed(title="Current Bets: ", description=statusMsg)
        await event.message.respond(embed)

        
        #calculating difference between current players bet and the previous players bet
        #if they're the same player can check or bet, if not player can call or bet
        difference = 0
        for i in range(currentPosition-1, -len(players)+currentPosition, -1):
            if ((players[i].folded == False and players[i].Allin == False) or players[i].betAmt == maxBet):
                difference = abs(players[currentPosition].betAmt - players[i].betAmt)
                break

        options = ["check ✅, bet 💰, or fold ❌", "call for " + str(difference) + " ☎️, raise 🔼, or fold ❌", "All in ☎️ or fold ❌"]
        emojis = [['✅', '💰', '❌'], ['☎️', '🔼', '❌']]
        #building and sending message to player with they're current betting options
        betMsg = ""
        if difference >= players[currentPosition].balance:
            betMsg += options[2]
        else: 
            betMsg += options[0] if difference == 0 else options[1]
        embed = Embed(title=str(players[currentPosition].user.username) + ': ', description=betMsg)
        betMsgObj = await event.message.respond(embed)

        #getting the betting choice from the user through reactions
        reaction = GuildReactionAddEvent
        timeoutmsg = str(players[currentPosition].user.username) + ", you took too long. Folding."
        Fold = False
        if difference >= players[currentPosition].balance:
            await betMsgObj.add_reaction(emojis[1][0])
            await betMsgObj.add_reaction(emojis[1][2])
            reaction = await tils.waitForReaction(reaction, event, betMsgObj.id, players[currentPosition].user.id, [emojis[1][0], emojis[1][2]], timeoutmsg, 60)
            if reaction == None:
                Fold = True
        elif difference == 0:
            await betMsgObj.add_reaction(emojis[0][0])
            await betMsgObj.add_reaction(emojis[0][1])
            await betMsgObj.add_reaction(emojis[0][2])
            reaction = await tils.waitForReaction(reaction, event, betMsgObj.id, players[currentPosition].user.id, emojis[0], timeoutmsg, 60)
            if reaction == None:
                Fold = True
        else:
            await betMsgObj.add_reaction(emojis[1][0])
            await betMsgObj.add_reaction(emojis[1][1])
            await betMsgObj.add_reaction(emojis[1][2])
            reaction = await tils.waitForReaction(reaction, event, betMsgObj.id, players[currentPosition].user.id, emojis[1], timeoutmsg, 60)
            if reaction == None:
                Fold = True
        
        
        #doing the action the user specified, nothing happens on check so no function needed
        if Fold == True or reaction.emoji_name == emojis[0][2]: #Fold
            players[currentPosition].folded = True
        elif reaction.emoji_name == emojis[0][1] or reaction.emoji_name == emojis[1][1]:#bet or raise
            await event.message.respond(str(players[currentPosition].user.username) + ", enter amount.")
            betAmtMsg = await tils.waitForMessage(event, players[currentPosition].user.id, timeoutmsg)
            if betAmtMsg == None or not str(betAmtMsg.content).isnumeric():
                Fold = True
            else:
                if reaction.emoji_name == emojis[0][1]: #bet
                    if players[currentPosition].balance <= int(betAmtMsg.content): #if players bet makes them go all in
                        players[currentPosition].Allin = True
                        pot += players[currentPosition].balance
                        players[currentPosition].betAmt += players[currentPosition].balance
                        players[currentPosition].balance = 0
                    else: #normal bet
                        players[currentPosition].betAmt += int(betAmtMsg.content)
                        players[currentPosition].balance -= int(betAmtMsg.content)
                        pot += int(betAmtMsg.content)
                else: #raise
                    if players[currentPosition].balance <= (difference + int(betAmtMsg.content)):
                        players[currentPosition].Allin = True
                        pot += players[currentPosition].balance
                        players[currentPosition].betAmt += players[currentPosition].balance
                        players[currentPosition].balance = 0
                    else:
                        players[currentPosition].betAmt += (difference + int(betAmtMsg.content))
                        pot += (difference + int(betAmtMsg.content))
                        players[currentPosition].balance -= (difference + int(betAmtMsg.content))
        elif reaction.emoji_name == emojis[1][0]: #call
            if players[currentPosition].balance <= difference:
                players[currentPosition].Allin = True
                pot += players[currentPosition].balance
                players[currentPosition].betAmt += players[currentPosition].balance
                players[currentPosition].balance = 0
            else:
                players[currentPosition].betAmt += difference
                pot += difference
                players[currentPosition].balance -= difference

        #go to next player to get their bet
        currentPosition = currentPosition + 1 if currentPosition != len(players)-1 else 0

        maxBet = max([player.betAmt for player in players])

    #out of loop
    if len([player for player in players if player.folded == False]) == 1:
        winningUser = [player for player in players if player.folded == False][0].user
        endMsg = "All players except " +  winningUser.username + ' folded. ' + winningUser.username + ' wins ' + str(pot)
        embed = Embed(title="Hand Over", description=endMsg)
        await event.message.respond(embed)
        return (False, pot, winningUser.id)
    else:
        curBets = ""
        balances = ""
        for i in range(len(players)):
            if i != 0:
                curBets += ', '
                balances += ', '
            curBets += str(players[i].user.username) + ': '
            if players[i].Allin == True:
                curBets += 'All In (' + str(players[i].betAmt) + ')'
            elif players[i].folded == True:
                curBets += 'F'
            else:
                curBets += str(players[i].betAmt)
            balances += str(players[i].user.username) + ': ' + str(players[i].balance)

        embed = Embed(title = "Betting round over", description='\u200b')
        embed.add_field(name = "Current Bets", value=curBets)
        embed.add_field(name = "Balances", value=balances)
        await event.message.respond(embed)
        return (True, pot, None)


async def poker(event: hikari.GuildMessageCreateEvent, tils):
    embed = Embed(title="Welcome to Poker!", description="Mention who you would like to play with to get started!\nOr type help to see how to play")
    await event.message.respond(embed)
    msg = await tils.waitForMessage(event, event.author_id)
    if msg == None:
        return
    if msg.content.lower() == 'help':
        embed = Embed(title = 'Poker Help', description=""" To play this version of poker, first mention who you want to play with. 
        You will then all enter a buy in amount. You will play hands until everyone except one player has lost all of their money. There will be an ante
        to start each hand starting at 1, and the ante will double every 5 hands that are played. Mention who you're playing with to start! """)
        await event.message.respond(embed)
        msg = await tils.waitForMessage(event, event.author_id)
        if msg == None:
            return
    if len(msg.message.mentions.user_ids) == 0 or event.author_id in msg.message.mentions.user_ids:
        await event.message.respond("You didn't mention anyone to play with, or you mentioned yourself. Exiting poker.")
        return
    

    #fetching user objects and building players list
    guild = event.get_guild()
    member = await tils.bot.rest.fetch_member(guild, event.author_id)
    players = [] #list of poker_player objects
    players.append(Poker_Player(member.user))
    for id in msg.message.mentions.user_ids:
        member = await tils.bot.rest.fetch_member(guild, id)
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
                binmsg = await tils.bot.wait_for(hikari.GuildMessageCreateEvent, 120)
            except asyncio.TimeoutError:
                await event.message.respond("All players were not ready to play. Exiting poker.")
                return
        buy_ins.add(binmsg.author_id)
        #updating players list with buy ins
        index = [player.user.id for player in players].index(binmsg.author_id)
        players[index].balance = int(binmsg.content)
        #update db with buy ins
        if not DB.add(int(binmsg.content)*-1, str(binmsg.author_id)):
                await event.message.respond("Not enough money, exiting poker.")
                return

    #shuffling player order so play isn't always in order mentioned by author
    random.shuffle(players)
    #set positon of dealer, small blind, big blind, UTG
    DealerPosition = 0

    #creating card deck
    deck = Deck()
    ante = 1
    hand_count = 0
    #start of main loop
    while len(players) > 1:
        if hand_count % 5 == 0 and hand_count != 0:
            ante = ante*2
            await event.message.respond("Ante raised to " + str(ante))
        hand_count += 1
        pot = 0 #amt of money in pot
        #shuffling card deck    
        deck.shuffle()
        
        for player in players: #reset folded and all in vals each hand
            player.folded = False
            player.Allin = False

        #Dealing to players
        for player in players:
            player.hand = deck.draw(2)
            await (await tils.bot.rest.create_dm_channel(player.user.id)).send('------------------------------------------------\n' + make_card_string(player.hand))
        
        #printing player order
        orderMsg = ""
        for i in range(len(players)):
            if i == DealerPosition:
                orderMsg += "D "
            orderMsg += str(players[i].user.username)
            if i != len(players)-1:
                orderMsg += ', '
        embed = Embed(title="Player Order", description=orderMsg)
        await event.message.respond(embed)
        
        keep_playing = True
        WinningUserId = None
        keep_playing, pot, WinningUserId = await betting_round(event, players, pot, DealerPosition,ante, True, tils)
        if keep_playing:
            board = deck.draw(5)
            embed = Embed(title="Flop", description=make_card_string(board[:3]))
            await event.message.respond(embed)
            keep_playing, pot, WinningUserId = await betting_round(event, players, pot, DealerPosition, ante, False, tils)
            if keep_playing:
                embed = Embed(title="Turn", description=make_card_string(board[:4]))
                await event.message.respond(embed)
                keep_playing, pot, WinningUserId = await betting_round(event, players, pot, DealerPosition, ante, False, tils)
                if keep_playing:
                    embed = Embed(title="River", description=make_card_string(board))
                    await event.message.respond(embed)
                    keep_playing, pot, WinningUserId = await betting_round(event, players, pot, DealerPosition, ante, False, tils)
                    if keep_playing: #Final betting round
                        #evaluate hands
                        evaluator = Evaluator()
                        WinningScore = -1
                        WinningPlayer = PlaceHolder
                        embed = Embed(title = "Hand Results", description='\u200b')
                        embed.add_field(name = "Board", value= make_card_string(board))
                        for player in [player for player in players if player.folded == False]:
                            handScore = evaluator.evaluate(board, player.hand)
                            hand_class = evaluator.get_rank_class(handScore)
                            if  handScore < WinningScore or WinningScore == -1:
                                WinningScore = handScore
                                WinningPlayer = player
                            embed.add_field(name =str(player.user.username) + "'s hand", value= make_card_string(player.hand) + ' Strength of Hand: ' + evaluator.class_to_string(hand_class))
                        embed.add_field(name=WinningPlayer.user.username, value= 'Wins ' + str(pot))
                        WinningPlayer.balance += pot
                        await event.message.respond(embed)
        if WinningUserId != None:
            for player in players:
                if player.user.id == WinningUserId:
                    player.balance += pot
        balanceMsg = ""
        for i, player in enumerate(players):
            balanceMsg += player.user.username + ' ' + str(player.balance)
            if i != len(players)-1:
                balanceMsg += ', '
        embed = Embed(title="Player Balances", description=balanceMsg)
        await event.message.respond(embed)
        #removing players that ran out of money, and rotating dealer around the table
        DealerOut = False
        for idx, player in enumerate(players):
            if player.balance <= 0:
                if idx == DealerPosition:
                    DealerOut = True
                await event.message.respond(player.user.username + ' ran out of money. See ya!')
        players_copy = deepcopy([player for player in players if player.balance > 0])
        players = deepcopy(players_copy)
        if not DealerOut:
            DealerPosition = DealerPosition + 1 if DealerPosition+1 < len(players) else 0
        if(len(players) > 1):
            await event.message.respond("The next hand will start in 10 seconds!")
        else:
            #update db balances at end of game
            for player in players:
                DB.add(player.balance, str(player.user.id))
            await event.message.respond("Game over, exiting poker.")
        time.sleep(10)
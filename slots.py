import hikari
from hikari.embeds import Embed
from hikari.events.reaction_events import GuildReactionAddEvent
import time, random
import db

DB = db.Db()


async def slot(event: hikari.GuildMessageCreateEvent, tils):
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-play slots":
        embed = Embed(title="Welcome to the slot machine!", description="Press 🎰 to play!\nPress 📝 to see payouts")
        emb = await event.message.respond(embed)
        await emb.add_reaction('🎰')
        await emb.add_reaction('📝')

        reaction = GuildReactionAddEvent
        reaction = await tils.waitForReaction(reaction, event, emb.id, event.message.author.id, ['🎰', '📝'])
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
            reaction = await tils.waitForReaction(reaction, event, pemb.id, event.message.author.id, ['🎰'])
            if reaction == None:
                return

        while(True):
            wagerMsg = await event.message.respond("How much would you like to wager? 💸 = 5, 💵 = 10, 🤑 = 25, 💰 = 50\n")
            wagerEmojis = [('💸', 5), ('💵', 10), ('🤑', 25), ('💰', 50)]
            
            for emoji in wagerEmojis:
                await wagerMsg.add_reaction(emoji[0])

            reaction = GuildReactionAddEvent
            reaction = await tils.waitForReaction(reaction, event, wagerMsg.id, event.message.author.id, ['💸','💵','🤑','💰'], "You never entered a wager, aborting.", 60)
            if reaction == None:
                return
            wager =0
            for possibleWager in wagerEmojis:
                if reaction.emoji_name == possibleWager[0]:
                    wager = possibleWager[1]
                    break

            if not DB.add((wager*-1), str(event.message.author.id)):
                await event.message.respond("Not enough money, exiting slots.")
                return

            payout = await slot_helper(event, wager)
            if payout > 0:
                msg = "You won " + str(payout) +"! To play again press 🎰"
                DB.add(payout, str(event.message.author.id))
            else:
                msg = "Sorry, you didn't win. Better luck next time! To play again press 🎰"
            mesg = await event.message.respond(msg)
            await mesg.add_reaction('🎰')

            reaction = GuildReactionAddEvent
            reaction = await tils.waitForReaction(reaction, event, mesg.id, event.message.author.id, ['🎰'], "Goodbye, Thanks for playing!", 30)
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
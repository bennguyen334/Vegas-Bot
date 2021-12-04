from os import name
import random
import hikari
from hikari.embeds import Embed
import slots, poker
import utils, db
import blackjack as bj
from apscheduler.schedulers.asyncio import AsyncIOScheduler

with open("./secrets/token", mode="r", encoding="utf-8") as f:
    token = f.read().strip("\n")

bot = hikari.GatewayBot(token=token)
tils = utils.Utils(bot)
DB = db.Db()

@bot.listen()
async def blackjack(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-play blackjack":

        BJ = bj.Blackjack()
        await BJ.game(event, tils)


@bot.listen()
async def help(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-help":
        embed = Embed(title= "Help", description="Here's all my commands")
        embed.add_field(name="-help", value="Displays this message")
        embed.add_field(name="-balance", value="Displays your balance")
        embed.add_field(name="-collect daily", value="Allows you to collect a random amount of points each day")
        embed.add_field(name="-play slots", value="Play the slot machine and win points!")
        embed.add_field(name="-play poker", value="Play poker with your friends!")
        embed.add_field(name="-play blackjack", value="Play the blackjack game!")
        await(event.message.respond(embed))

@bot.listen()
async def get_Balance(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-balance":
        await event.message.respond(str(event.author.username) + "'s balance is " + str(DB.get_balance(str(event.message.author.id))))

@bot.listen()
async def collect_daily(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-collect daily":
        if DB.can_user_collect(str(event.message.author.id)):
            amt = random.randint(15, 30)
            DB.add(amt, str(event.message.author.id))
            DB.setLastCollected(str(event.message.author.id))
            await event.message.respond("Collected " + str(amt) + "!")
        else:
            await event.message.respond("You've already collected today. Come back tomorrow!")

@bot.listen()
async def Slots(event: hikari.GuildMessageCreateEvent) -> None:
    await slots.slot(event, tils)

@bot.listen()
async def play_poker(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    if event.content.lower() == "-play poker":
        await poker.poker(event, tils)
                   
bot.run()
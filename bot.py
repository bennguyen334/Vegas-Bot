import hikari
import lightbulb


with open("./secrets/token", "r") as f:
    token = f.read().strip()

bot = lightbulb.Bot(
    token,
    prefix="+",
    banner=None,
    intents=hikari.Intents.ALL,
    default_enabled_guilds=(885224908030873601,)
)

@bot.command()
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")

bot.load_extensions_from("./modules/", must_exist=True)

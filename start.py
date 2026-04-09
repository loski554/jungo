import logging
import os
import asyncio
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from utils.logFormatter import CustomFormatter
from utils.database import init_db

load_dotenv()

intents = Intents.all()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

bot = commands.Bot(command_prefix="$", intents=intents)
tree = bot.tree

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")
            logging.info(f"Cog {file} loaded.")

@bot.event
async def on_ready():
    try:
        await tree.sync()
        logging.info(msg=f"Logged as {bot.user}.")
    except Exception as e:
        print(e)

async def main():
    #launch database
    await init_db()

    # setup logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("Bot was shut down.")
    except Exception as e:
        print(e)
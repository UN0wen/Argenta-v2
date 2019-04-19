from discord.ext import commands
from cogs.utils import checks, db
import discord
import nhentai
import random
import logging
from nhentai import errors

TEAQ_ID = 152373455529050113
TEAQ_NSFW_ID = 335770969362792448

log = logging.getLogger(__name__)

afk_cache = {}


class AFK(db.Table):
    def __init__(self, table_name=None):
        table = f"CREATE TABLE IF NOT EXIST {table_name}"
        column = """user_id VARCHAR (20) PRIMARY KEY, 
        afk_message VARCHAR (255)"""
        super().__init__(table, column)


class GeneralCommands(commands.Cog):
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.table = AFK(table_name='afk')

    @commands.command()
    @checks.is_bot_channel()
    async def afk(self, ctx, *, afk_msg):
        if not afk_msg:
            await ctx.send("Please specify an argument for the afk message.")
        else:
            if afk_msg == ".":
                return

    @commands.command()
    @commands.is_owner()
    async def react(self, ctx):
        msg = await ctx.channel.fetch_message(492013238670589973)
        print(msg.reactions)
        await msg.add_reaction(msg.reactions[0])

    @commands.command()
    @checks.is_in_channel(TEAQ_NSFW_ID)
    async def nh(self, ctx, tag):
        itag = int(tag)
        try:
            d = nhentai.Doujinshi(itag)
            url = f"http://nhentai.net/g/{tag}"
            e = discord.Embed(title=d.name, url=url)
            e.add_field(name="Magic number", value=d.magic)
            e.add_field(name="Tags", value=', '.join(d.tags))
            e.set_image(url=d.cover)
            e.colour = discord.Colour.teal()
            log.info("Doujin requested.")
            await ctx.send(embed=e)
        except errors.DoujinshiNotFound:
            log.info(f"Requested: {tag}. Doujin not found.")
            await ctx.send("Doujinshi not found.")

    @commands.command()
    @checks.is_in_channel(TEAQ_NSFW_ID)
    async def nhsearch(self, ctx, *, query):
        page = random.randint(1, 10)
        results = [d for d in nhentai.search(query, page)]
        if not results:
            results = [d for d in nhentai.search(query, 1)]
        try:
            d = random.choice(results)
            url = f"http://nhentai.net/g/{d.magic}"
            e = discord.Embed(title=d.name, url=url)
            e.add_field(name="Magic number", value=d.magic)
            e.add_field(name="Tags", value=', '.join(d.tags))
            e.set_image(url=d.cover)
            e.colour = discord.Colour.teal()
            log.info("Doujin search requested.")
            await ctx.send(embed=e)
        except errors.DoujinshiNotFound:
            log.info(f"Requested: {query}. Doujin not found.")
            await ctx.send(f"Doujinshi not found with query {query}")
        except IndexError:
            log.info(f"Requested: {query}. Doujin not found.")
            await ctx.send(f"Doujinshi not found with query {query}")


def setup(bot):
    bot.add_cog(GeneralCommands(bot))

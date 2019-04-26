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
        table = f"CREATE TABLE IF NOT EXISTS {table_name}"
        column = """user_id TEXT PRIMARY KEY, 
        afk_message TEXT"""
        super().__init__(table, column)


class General(commands.Cog):
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.table = AFK(table_name='Users')

    @commands.group(name='afk', rest_is_raw=True)
    @checks.is_bot_channel()
    async def afk(self, ctx, *, afk_msg):
        """Set afk message. Set to . to cancel."""
        afk_msg = afk_msg[1:]
        if afk_msg == "":
            query = "SELECT * FROM users WHERE user_id = $1"
            row = await ctx.db.fetchrow(query, str(ctx.author.id))
            if row:
                if row['afk_message']:
                    await ctx.send(f"""Your afk message is: {row['afk_message']}.""")
                else:
                    await ctx.send(f"You don't currently have an afk message.")
            else:
                await ctx.send("You don't currently have an afk message.")
        else:
            query = ("INSERT INTO users (user_id, afk_message) VALUES ($2, $1) " 
                     "ON CONFLICT (user_id) DO UPDATE SET afk_message = $1")
            if afk_msg == ".":
                await ctx.db.execute(query, None, str(ctx.author.id))
                await ctx.send("Welcome back.")
            else:
                await ctx.db.execute(query, afk_msg, str(ctx.author.id))
                await ctx.send("AFK message successfully updated.")

    @afk.before_invoke
    async def create_connection(self, ctx):
        await ctx.acquire()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.mentions:
            db = await self.bot.pool.acquire()
            for member in message.mentions:
                query = "SELECT * FROM users WHERE user_id = $1"
                row = await db.fetchrow(query, str(member.id))
                if row:
                    if row['afk_message']:
                        await message.channel.send(f"**@{member.display_name}** is currently AFK: {row['afk_message']}")
            await self.bot.pool.release(db)

    @commands.command()
    @checks.is_in_channel(TEAQ_NSFW_ID)
    async def nh(self, ctx, tag):
        """Displays the nhentai doujin with id <tag>"""
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
        """Issues a search to nhentai with <query>.
        Displays a random doujin selected from the search results."""
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
    bot.add_cog(General(bot))

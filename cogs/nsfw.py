from discord.ext import commands
from cogs.utils import checks, db, javlibrary
import discord
import nhentai
import random
import logging
import functools
from nhentai import errors
from cogs.embeds.argenta_em import ArgentaEmbed

TEAQ_ID = 152373455529050113
TEAQ_NSFW_ID = 335770969362792448

log = logging.getLogger(__name__)

class NSFW(commands.Cog):
    """NSFW commands. Most will only be usable in the
    TEAQVISITION nsfw channel."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_in_channel(TEAQ_NSFW_ID)
    async def jav(self, ctx, *, query):
        """Displays the information for a JAV.
        Valid query search term is ABCD-1234 or ABCD 1234"""
        javlib = functools.partial(javlibrary.get_javlibrary, query)
        d = await self.bot.loop.run_in_executor(None, javlib)
        if not d:
            await ctx.send(f"Video with ID {query} not found.")
            log.info(f"Requested {query}, not found.")
            return
        
        e = ArgentaEmbed(ctx.author, title=d['title'])
        e.add_field(name="Actresses", value=d['actresses'])
        e.add_field(name="Genres", value=d['genre'])
        length = d["length"] + " minutes"
        e.add_field(name="Length", value=length)
        e.add_field(name='Release Date', value=d['release_date'])
        e.add_field(name="Label", value=d["label"])
        img_url = "https:" + d['cover_url'] 
        e.set_image(url=img_url)
        e.colour = discord.Colour.dark_teal()
        await ctx.send(embed=e)
        log.info(f"JAV with ID {query} requested.")
        
    @commands.command()
    @checks.is_in_channel(TEAQ_NSFW_ID)
    async def nh(self, ctx, tag):
        """Displays the nhentai doujin with id <tag>"""
        itag = int(tag)
        try:
            d = nhentai.Doujinshi(itag)
            url = f"http://nhentai.net/g/{tag}"
            e = ArgentaEmbed(ctx.author, title=d.name, url=url)
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
            e = ArgentaEmbed(ctx.author, title=d.name, url=url)
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
    bot.add_cog(NSFW(bot))
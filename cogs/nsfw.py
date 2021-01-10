from discord.ext import commands
from cogs.utils import checks, db
from cogs.libs import javlibrary
import discord
import nhentai
import random
import logging
import functools
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
        doujin = await self.bot.loop.run_in_executor(None, javlib)
        if not doujin:
            await ctx.reply(f"Video with ID {query} not found.")
            log.info(f"Requested {query}, not found.")
            return
        
        e = ArgentaEmbed(ctx.author, title=doujin['title'])
        e.add_field(name="Actresses", value=doujin['actresses'])
        e.add_field(name="Genres", value=doujin['genre'])
        length = doujin["length"] + " minutes"
        e.add_field(name="Length", value=length)
        e.add_field(name='Release Date', value=doujin['release_date'])
        e.add_field(name="Label", value=doujin["label"])
        img_url = "https:" + doujin['cover_url'] 
        e.set_image(url=img_url)
        e.colour = discord.Colour.dark_teal()
        await ctx.reply(embed=e)
        log.info(f"JAV with ID {query} requested.")
        
    @commands.command()
    @checks.is_in_channel(TEAQ_NSFW_ID)
    async def nh(self, ctx, tag):
        """Displays the nhentai doujin with id <tag>"""
        itag = int(tag)
        try:
            doujin = nhentai.get_doujin(itag)
            e = ArgentaEmbed(ctx.author, title=doujin.titles["english"], url=doujin.url)
            e.add_field(name="Magic number", value=doujin.id)
            e.add_field(name="Tags", value=', '.join([i.name for i in doujin.tags]))
            e.set_image(url=doujin.cover)
            e.colour = discord.Colour.teal()
            log.info("Doujin requested.")
            print(e)
            await ctx.reply(embed=e)
        except ValueError:
            log.info(f"Requested: {tag}. Doujin not found.")
            await ctx.reply("Doujinshi not found.")

    @commands.command()
    @checks.is_in_channel(TEAQ_NSFW_ID)
    async def nhsearch(self, ctx, *, query):
        """Issues a search to nhentai with <query>.
        Displays a random doujin selected from the search results."""
        page = random.randint(1, 10)
        results = nhentai.search(query, page)
        if not results:
            results = nhentai.search(query, 1)
        try:
            doujin = random.choice(results)
            e = ArgentaEmbed(ctx.author, title=doujin.titles['english'], url=doujin.url)
            e.add_field(name="Magic number", value=doujin.id)
            e.add_field(name="Tags", value=', '.join([i.name for i in doujin.tags]))
            e.set_image(url=doujin.cover)
            e.colour = discord.Colour.teal()
            log.info("Doujin search requested.")
            await ctx.reply(embed=e)
        except ValueError:
            log.info(f"Requested: {query}. Doujin not found.")
            await ctx.reply(f"Doujinshi not found with query {query}")
        except IndexError:
            log.info(f"Requested: {query}. Doujin not found.")
            await ctx.reply(f"Doujinshi not found with query {query}")

def setup(bot):
    bot.add_cog(NSFW(bot))
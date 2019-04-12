from discord.ext import commands
from cogs.utils import checks
import discord
import nhentai
import random
from nhentai import errors

DNSEA_ID = 152373455529050113


class GeneralCommands(commands.Cog):
    """General commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def changegame(self, ctx, game):
        await ctx.bot.change_presence(activity=discord.Game(name=game))

    @commands.command()
    @commands.is_owner()
    async def changestatus(self, ctx, status):
        if status == 'invisible':
            sts = discord.Status.invisible
        elif status == 'online':
            sts = discord.Status.online
        elif status == 'offline':
            sts = discord.Status.offline
        elif status == 'dnd':
            sts = discord.Status.dnd
        else:
            sts = ''
        if sts:
            await ctx.bot.change_presence(status=sts)

    @commands.command()
    @commands.is_owner()
    async def delmsgsoncmd(self, ctx):
        ctx.bot.del_msgs_on_command = not ctx.bot.del_msgs_on_command
        if ctx.bot.del_msgs_on_command:
            await ctx.send("Now deleting command invocation messages.")
        else:
            await ctx.send("Stopped deleting command invocation messages.")

    def is_me(self, message):
        return message.author == self.bot.user

    @commands.command()
    @checks.is_admin()
    async def purge(self, ctx):
        deleted = await ctx.channel.purge(limit=100, check=self.is_me)
        await ctx.send('Deleted {} message(s)'.format(len(deleted)))

    @commands.command()
    @checks.is_in_guilds(DNSEA_ID)
    async def nh(self, ctx, tag):
        itag = int(tag)
        try:
            d = nhentai.Doujinshi(itag)
            url = f"http://nhentai.net/g/{tag}"
            desc = f"""Tags = {d.tags}"""
            e = discord.Embed(title=d.name, description=desc, url=url)
            e.set_image(url=d[0])
            await ctx.send(embed=e)
        except errors.DoujinshiNotFound:
            await ctx.send("Doujinshi not found.")

    @commands.command()
    @checks.is_in_guilds(DNSEA_ID)
    async def nhsearch(self, ctx, query):
        page = random.randint(1, 10)
        results = [d for d in nhentai.search(query, page)]
        try:
            d = random.choice(results)
            url = f"http://nhentai.net/g/{d.magic}"
            desc = f"""Tags = {d.tags}"""
            e = discord.Embed(title=d.name, description=desc, url=url)
            e.set_image(url=d[0])
            await ctx.send(embed=e)
        except errors.DoujinshiNotFound:
            await ctx.send("Doujinshi not found.")


def setup(bot):
    bot.add_cog(GeneralCommands(bot))

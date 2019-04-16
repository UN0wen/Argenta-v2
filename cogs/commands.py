from discord.ext import commands
from cogs.utils import checks
import discord
import nhentai
import random
import logging
from nhentai import errors
from datetime import datetime
import config

TEAQ_ID = 152373455529050113
TEAQ_NSFW_ID = 335770969362792448

log = logging.getLogger(__name__)


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

    @commands.command()
    @checks.is_mod()
    async def user(self, ctx, *, user):
        if ctx.message.mentions:
            mem = ctx.message.mentions[0]
        else:
            try:
                uid = int(user)
                mem = ctx.guild.get_member(uid)
            except ValueError:
                mem = ctx.guild.get_member_named(user)

        url = mem.avatar_url
        uname = f"{mem.name}#{mem.discriminator}"
        created_date_str = mem.created_at.strftime("%d/%m/%Y, %H:%M:%S")
        guild_join_date_str = mem.joined_at.strftime("%d/%m/%Y, %H:%M:%S")

        mem_roles = mem.roles[1:]

        e = discord.Embed(title=uname)
        e.colour = discord.Colour.teal()
        e.add_field(name="User ID", value=mem.id)
        e.add_field(name="Bot", value=mem.bot)
        e.add_field(name="Guild join date", value=guild_join_date_str)
        e.add_field(name="Account creation date", value=created_date_str)
        e.add_field(name="Roles", value=', '.join(map(str, mem_roles)))
        e.add_field(name="Status", value=mem.status)
        e.set_thumbnail(url=url)
        await ctx.send(embed=e)

    def is_me(self, message):
        return message.author == self.bot.user

    @commands.command()
    @checks.is_admin()
    async def purge(self, ctx):
        deleted = await ctx.channel.purge(limit=100, check=self.is_me)
        await ctx.send('Deleted {} message(s)'.format(len(deleted)))

    def check_prefix(self, message):
        if message is not None:
            try:
                return message.content[0] == config.BOT_PREFIX
            except IndexError:
                return False
        else:
            return False

    @commands.command()
    @checks.is_admin()
    async def delcmds(self, ctx):
        deleted = await ctx.channel.purge(limit=100, check=self.check_prefix)
        await ctx.send('Deleted {} message(s)'.format(len(deleted)))

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

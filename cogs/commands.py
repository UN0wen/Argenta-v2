from discord.ext import commands
from cogs.utils import checks, db
import discord
import random
import logging
from .embeds.argenta_em import ArgentaEmbed

TEAQ_ID = 152373455529050113
TEAQ_NSFW_ID = 335770969362792448

log = logging.getLogger(__name__)

afk_cache = {}
afk_blacklist = [526456830193434624, 352843237062606848]

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
        self.mimic = {}

    @commands.group(name='afk', rest_is_raw=True)
    #@checks.is_bot_channel()
    async def afk(self, ctx, *, afk_msg):
        """Set afk message. Set to . to cancel."""
        afk_msg = afk_msg[1:]
        if afk_msg == "":
            query = "SELECT * FROM users WHERE user_id = $1"
            row = await ctx.db.fetchrow(query, str(ctx.author.id))
            if row:
                if row['afk_message']:
                    await ctx.reply(f"""Your afk message is: {row['afk_message']}.""")
                else:
                    await ctx.reply(f"You don't currently have an afk message.")
            else:
                await ctx.reply("You don't currently have an afk message.")
        else:
            query = ("INSERT INTO users (user_id, afk_message) VALUES ($2, $1) " 
                     "ON CONFLICT (user_id) DO UPDATE SET afk_message = $1")
            if afk_msg == ".":
                await ctx.db.execute(query, None, str(ctx.author.id))
                await ctx.reply("Welcome back.")
            else:
                await ctx.db.execute(query, afk_msg, str(ctx.author.id))
                await ctx.reply("AFK message successfully updated.")
    
    @commands.command(hidden=True)
    @checks.is_mod()
    async def afkdelete(self, ctx, uid):
        query = ("INSERT INTO users (user_id, afk_message) VALUES ($2, $1) " 
                     "ON CONFLICT (user_id) DO UPDATE SET afk_message = $1")
        await ctx.db.execute(query, None, uid)
        await ctx.reply(f"AFK message of user {uid} deleted")

    @afk.before_invoke
    async def create_connection(self, ctx):
        await ctx.acquire()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content:
            return
        if message.content[0] == self.bot.command_prefix:
            return
        if message.channel.id in afk_blacklist:
            return
        if message.mentions:
            db = await self.bot.pool.acquire()
            for member in message.mentions:
                query = "SELECT * FROM users WHERE user_id = $1"
                row = await db.fetchrow(query, str(member.id))
                if row:
                    if row['afk_message']:
                        await message.channel.send(f"**@{member.display_name}** is currently AFK: {row['afk_message']}")
            await self.bot.pool.release(db)
        if message.author.id in self.mimic and self.mimic[message.author.id]:
            channel = message.channel
            msg_content = message.content
            await message.delete()
            await channel.send(msg_content)

    @commands.command()
    @checks.is_bot_channel()
    async def mimic(self, ctx):
        try:
            self.mimic[ctx.author.id] = not self.mimic[ctx.author.id]
        except KeyError:
            self.mimic[ctx.author.id] = True

        if self.mimic[ctx.author.id]:
            await ctx.reply('Mimic enabled.')
        else:
            await ctx.reply('Mimic disabled.')

    

def setup(bot):
    bot.add_cog(General(bot))

from discord.ext import commands
import discord
from cogs.utils import checks
from contextlib import redirect_stdout
import io
import traceback
import textwrap
import config
import json
import requests


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

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

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Admin(bot))

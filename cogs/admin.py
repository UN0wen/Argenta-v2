from discord.ext import commands
import discord
from cogs.utils import checks
from contextlib import redirect_stdout
import io
import traceback
import textwrap
import config
import subprocess
import sys
import json
import requests
from .embeds.argenta_em import ArgentaEmbed


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def changegame(self, ctx, game):
        await ctx.bot.change_presence(activity=discord.Game(name=game))

    @commands.command(hidden=True)
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


    # disable this since replies have arrived
    # @commands.command(hidden=True)
    # @commands.is_owner()
    # async def delmsgsoncmd(self, ctx):
    #     ctx.bot.del_msgs_on_command = not ctx.bot.del_msgs_on_command
    #     if ctx.bot.del_msgs_on_command:
    #         await ctx.send("Now deleting command invocation messages.")
    #     else:
    #         await ctx.send("Stopped deleting command invocation messages.")

    @commands.command()
    @checks.is_mod()
    async def member(self, ctx, *, user):
        """Shows information about the guild member.

        <user> can be either of the 3:

        Tag
        User ID
        Username"""
        if ctx.message.mentions:
            mem = ctx.message.mentions[0]
        else:
            try:
                uid = int(user)
                mem = ctx.guild.get_member(uid)
            except ValueError:
                mem = ctx.guild.get_member_named(user)

        if mem is None:
            await ctx.reply("Member not found.")
            return

        url = mem.avatar_url
        uname = f"{mem.name}#{mem.discriminator}"
        created_date_str = mem.created_at.strftime("%d/%m/%Y, %H:%M:%S")
        guild_join_date_str = mem.joined_at.strftime("%d/%m/%Y, %H:%M:%S")

        mem_roles = mem.roles[1:]

        e = ArgentaEmbed(ctx.author, title=uname)

        e.colour = discord.Colour.teal()
        e.add_field(name="User ID", value=mem.id, inline=False)
        e.add_field(name="Bot", value=mem.bot, inline=False)
        e.add_field(name="Guild join date", value=guild_join_date_str, inline=False)
        e.add_field(name="Account creation date", value=created_date_str, inline=False)

        if mem_roles:
            e.add_field(name="Roles", value=', '.join(map(str, mem_roles)), inline=False)

        e.add_field(name="Status", value=mem.status, inline=False)
        e.set_thumbnail(url=url)
        await ctx.reply(embed=e)

    @commands.command()
    @checks.is_mod()
    async def user(self, ctx, *, uid):
        """Shows information about the user with user id UID."""
        try:
            user = self.bot.get_user(int(uid))
        except ValueError:
            await ctx.reply(f"Invalid argument.")
            return

        if user is None:
            await ctx.reply(f"User with id {uid} not found.")
            return

        url = user.avatar_url
        uname = f"{user.name}#{user.discriminator}"
        created_date_str = user.created_at.strftime("%d/%m/%Y, %H:%M:%S")

        e = ArgentaEmbed(ctx.author, title=uname)
        e.colour = discord.Colour.teal()
        e.add_field(name="User ID", value=user.id, inline=False)
        e.add_field(name="Bot", value=user.bot, inline=False)
        e.add_field(name="Account creation date", value=created_date_str, inline=False)
        e.set_thumbnail(url=url)
        await ctx.reply(embed=e)

    @commands.command()
    @checks.is_mod()
    async def role(self, ctx, *, role):
        """Shows information about a role.

        <role> can be either:

        Role ID
        Role Name"""
        if isinstance(role, int):
            r = ctx.guild.get_role(role)
        else:
            r = discord.utils.find(lambda m: m.name == role, ctx.guild.roles)

        if r is None:
            await ctx.reply("Role not found.")
            return

        created_date_str = r.created_at.strftime("%d/%m/%Y, %H:%M:%S")

        e = ArgentaEmbed(ctx.author, title=r.name)
        e.colour = discord.Colour.teal()
        e.add_field(name="Role ID", value=r.id, inline=False)
        e.add_field(name="Colour", value=r.colour, inline=False)
        e.add_field(name="Number of members with this role", value=str(len(r.members)), inline=False)
        e.add_field(name="Mentionable", value=r.mentionable, inline=False)
        e.add_field(name="Role creation date", value=created_date_str, inline=False)

        await ctx.reply(embed=e)

    def is_me(self, message):
        return message.author == self.bot.user

    @commands.command()
    @checks.is_mod()
    async def purge(self, ctx):
        """Delete this bot's recent messages."""
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

    @commands.command(hidden=True)
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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def dm(self, ctx, uid, *, msg):
        user = self.bot.get_user(int(uid))
        if not user:
            await ctx.reply(f'User with ID {uid} not found.')
            return
        await user.send(msg)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, cog):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.reply(f"Extension {cog} not loaded.")

        try:
            self.bot.load_extension(cog)
            print(f"Loaded {cog}")
            await ctx.reply(f"Loaded {cog}.")
        except Exception as e:
            print(f'Failed to load extension {cog}.', file=sys.stderr)
            traceback.print_exc()
    
def setup(bot):
    bot.add_cog(Admin(bot))

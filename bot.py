import sys
import discord
import logging
from discord.ext import commands
import config
import aiohttp
import asyncio
import traceback
import datetime

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

description = """
I'm Argenta but Better
"""

log = logging.getLogger(__name__)

initial_extensions = (
    'cogs.commands',
    'cogs.dnsea',
    'cogs.warframe',
)


class Argenta(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config.BOT_PREFIX, description=description,
                         pm_help=None, help_attrs=dict(hidden=True), fetch_offline_members=False)

        self.del_msgs_on_command = True
        self.client_id = config.BOT_CLIENT_ID
        self.session = aiohttp.ClientSession(loop=self.loop)

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
                print(f"Loaded {extension}")
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    def is_me(self, message):
        return message.author == self.user

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("Sorry, you don't have the necessary permissions to use this command.")
            await asyncio.sleep(1)
            await ctx.channel.purge(limit=1, check=self.is_me)
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        await self.change_presence(status=discord.Status.online, activity=discord.Game(name="with Argenta."))
        print(f'Ready: {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command(self, ctx):
        if self.del_msgs_on_command:
            await ctx.message.delete()

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        try:
            super().run(config.BOT_TOKEN, reconnect=True)
        finally:
            pass






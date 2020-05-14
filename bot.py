import sys
import discord
import logging
from discord.ext import commands
import config
from cogs.utils import context
import aiohttp
import asyncio
import traceback
import datetime

description = """
I'm Argenta but Better
"""

log = logging.getLogger(__name__)

initial_extensions = (
    'cogs.commands',
    'cogs.dnsea',
    'cogs.warframe',
    'cogs.admin',
    'cogs.owl',
    'cogs.nsfw',
    'cogs.kpop',
)


class Argenta(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config.BOT_PREFIX, description=description,
                         pm_help=None, help_attrs=dict(hidden=True), fetch_offline_members=False)

        self.del_msgs_on_command = config.DELMSGONCMD
        self.client_id = config.BOT_CLIENT_ID
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.owner_id = 92669124332785664

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
            await ctx.send("Sorry, you don't have the necessary permissions to use this command.", delete_after=3)
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
        if isinstance(message.channel, discord.abc.PrivateChannel):
            if not self.is_owner(message.author):
                await self.process_dms(message)
        await self.process_commands(message)

    async def on_command(self, ctx):
        if self.del_msgs_on_command:
            try:
                await ctx.message.delete()
            except discord.errors.Forbidden:
                pass

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)

        if ctx.command is None:
            return

        try:
            await self.invoke(ctx)
        finally:
            # Just in case we have any outstanding DB connections
            await ctx.release()

    async def process_dms(self, message):
        dm = self.get_user(self.owner_id).dm_channel
        await dm.send(f"{message.author.name} sent a message: {message.clean_content}")

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        try:
            super().run(config.BOT_TOKEN, reconnect=True)
        finally:
            pass






from discord.ext import commands
from cogs.utils import checks
import discord


class GeneralCommands(commands.Cog):
    """Utilities that provide pseudo-RNG."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def changegame(self, ctx, game):
        await ctx.bot.change_presence(activity=discord.Game(name=game))

    @commands.command()
    @commands.is_owner()
    async def delmsgsoncmd(self, ctx):
        ctx.bot.del_msgs_on_command = not ctx.bot.del_msgs_on_command
        if ctx.bot.del_msgs_on_command:
            await ctx.send("Now deleting command invocation messages.")
        else:
            await ctx.send("Stopped deleting command invocation messages.")


def setup(bot):
    bot.add_cog(GeneralCommands(bot))

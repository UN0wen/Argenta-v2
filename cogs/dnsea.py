from discord.ext import commands
import datetime

TH_id = 265816069556404224
PT_id = 268739104999473155


def check_channel(ctx):
    return ctx.channel.id == PT_id or ctx.channel.id == TH_id


class DNSEA(commands.Cog):
    """Utilities that provide pseudo-RNG."""

    def __init__(self, bot):
        self.bot = bot
        self.TH_delete_time = datetime.timedelta(days=3)
        self.PT_delete_time = datetime.timedelta(days=1)
        self.test_delete_time = datetime.timedelta(minutes=1)

    @commands.group(pass_context=True)
    async def clean(self, ctx):
        """Displays a random thing you request."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect cleanth subcommand passed.')

    @clean.command()
    @commands.check(check_channel)
    async def verify(self, ctx):
        if ctx.channel.id == TH_id:
            delete_time = self.TH_delete_time
        else:
            delete_time = self.PT_delete_time

        time_threshold = datetime.datetime.utcnow() - delete_time
        pins = await ctx.channel.pins()
        last_pinned = pins[0]
        deleted = await ctx.channel.history(limit=1000, before=time_threshold, after=last_pinned).flatten()
        if not deleted:
            await ctx.send(f"There are no messages to be deleted.")
        else:
            await ctx.send(f"""There are {len(deleted)} message(s) to be deleted.
            First message is: <{deleted[0].jump_url}>.
            Last message is: <{deleted[-1].jump_url}>.""")

    @clean.command()
    @commands.check(check_channel)
    async def delete(self, ctx):
        if ctx.channel.id == TH_id:
            delete_time = self.TH_delete_time
        else:
            delete_time = self.PT_delete_time

        time_threshold = datetime.datetime.utcnow() - delete_time
        pins = await ctx.channel.pins()
        last_pinned = pins[0]
        deleted = await ctx.channel.purge(limit=1000, before=time_threshold, after=last_pinned, bulk=True)
        await ctx.send(f'Deleted {len(deleted)} message(s).')


def setup(bot):
    bot.add_cog(DNSEA(bot))

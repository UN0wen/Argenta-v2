from discord.ext import commands
from cogs.utils import checks
import random
import datetime
import asyncio
import logging

TH_id = 265816069556404224
PT_id = 268739104999473155

log = logging.getLogger(__name__)


class DNSEA(commands.Cog):
    """Commands made for DNSEA"""

    def __init__(self, bot):
        self.bot = bot
        self.TH_delete_time = datetime.timedelta(days=7)
        self.PT_delete_time = datetime.timedelta(days=1)
        self.test_delete_time = datetime.timedelta(minutes=1)
        self.snap_total = 0
        self.snap_list = []
        self.survivor_list = []
        self.snap_member_names = [
            'Mobochi~', 'Qing', 'icedcoffee', 'TomatoKun', 'Arc.Ciel', 'Silvie', 'Zen', 'Derick', 'smol qxuu', 'Rose', 'Jean', 'Zero', 'HoeLee', 'riko', 'Ernest', 'Nitefail', 'Aldossoul', 'WolfLover', 'Hazu', 'Mari', 'Marty', 'ᴱᵍᵍᶜᵘᵈᵈˡᵉʳ', 'Genny', 'SnowCoal31', 'Arch', 'Kura', 'YouBestWaifu', 'Gaunt', 'ibachu', 'Lucerie', 'razorgab', 'jason_rav', 'Arian', 'chubbychow', 'Folmore', 'Lazzu', 'Zesh', 'notyKet', 'Yeong', 'Keitaro', 'Mong 몽 TWICE 최고', 'Kocheng', 'Sazazary', 'Jariri☆', 'Lunch', 'Shirò', 'Yunoki', 'Clarent', 'Nippie']
        self.snap_survivor_names = [
            'Sammy', 'Valerie', 'Hie', 'Pudding', 'xhamster', 'Lance', 'Xuân Oanh', 'Valky', 'EksdDii', 'Yui', 'Gigi', 'Alice~', 'Eirawen', 'fuchi', 'Eiransu', 'Alb', 'Crook', 'Tachi', 'pchan v20.19', 'Disappointment', 'You', 'Teryshicka', 'Chitose86', 'Ereshkigal Waiting Room', 'kat', 'Nem', 'shinon', 'Thori', 'Shai', 'Lavienne', 'Custavio', 'Hept', 'CHillD', 'Reyisaki', 'Sciophe', 'NasagiChan', 'Micci', 'ace', 'Chunami', 'YairFrost', 'rukki', 'Shiraia', 'PanParanPam', 'Bear', 'Jimmy V', 'Lightnux', 'Chaika :two_hearts:', 'Beanut']
    """Clean commands"""

    @commands.group(pass_context=True)
    async def clean(self, ctx):
        """Displays a random thing you request."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect clean subcommand passed.')

    @clean.command()
    @checks.is_in_channel(TH_id, PT_id)
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
    @checks.is_in_channel(TH_id, PT_id)
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

    """Snap commands"""
    @commands.group(pass_context=True)
    async def snap(self, ctx):
        """Displays a random thing you request."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect snap subcommand passed.')

    def get_author(self, message):
        if not message.author.bot:
            return message.author

    @snap.command()
    @checks.is_admin()
    @commands.is_owner()
    async def check(self, ctx):
        author_list = await ctx.channel.history().flatten()
        snap_set = set()
        for message in author_list:
            if not message.author.bot:
                snap_set.add(message.author)
        self.snap_list = list(snap_set)
        list(filter(None.__ne__, self.snap_list))
        print(self.snap_list)
        self.snap_total = len(self.snap_list)

        random.shuffle(self.snap_list)
        self.survivor_list = self.snap_list[:len(self.snap_list)//2]
        self.snap_list = self.snap_list[len(self.snap_list)//2:]
        await ctx.send(f'Successfully initialized casualty list.')

    @snap.command()
    @checks.is_admin()
    @commands.is_owner()
    async def list(self, ctx):
        # Debugging
        author_names = []
        author_names_total = []
        for author in self.snap_list:
            if author:
                author_names.append(author.name)
        for author in self.survivor_list:
            if author:
                author_names_total.append(author.name)
        await ctx.send(f'List of people to snap: {author_names}')
        await ctx.send(f'Total number of unique posters in this channel: {self.snap_total}')
        await ctx.send(f'List of people who survived: {author_names_total}')

    @snap.command()
    @checks.is_admin()
    @commands.is_owner()
    async def kill(self, ctx):
        if not self.snap_list:
            await ctx.send(f'Run {ctx.prefix}snap check to populate list of people to be snapped.')
        else:
            fallen = ctx.guild.get_role(563349066088710144)
            avenger = ctx.guild.get_role(563349115992539208)
            citizen = ctx.guild.get_role(264072124069707798)
            endgame = ctx.guild.get_role(563905538765750293)
            dust_msg = "You've been dusted, for the good of the universe."
            survive_msg = "You have had the great privilege of being saved by the great titan."

            for member in self.snap_list:
                if member is not None:
                    if fallen not in member.roles:
                        await member.add_roles(fallen, endgame)
                        await member.remove_roles(citizen)
                        await member.send(dust_msg)
                        log.info(f"Snapped {member.name}.")
                        await asyncio.sleep(3)

            for member in self.survivor_list:
                if member is not None:
                    if avenger not in member.roles:
                        await member.add_roles(avenger, endgame)
                        await member.send(survive_msg)
                        log.info(f"Awarded {member.name}.")
                        await asyncio.sleep(3)

    @snap.command()
    @checks.is_admin()
    @commands.is_owner()
    async def reverse(self, ctx):
        fallen = ctx.guild.get_role(563349066088710144)
        avenger = ctx.guild.get_role(563349115992539208)
        citizen = ctx.guild.get_role(264072124069707798)

        for member in ctx.guild.members:
            member_roles = member.roles
            if fallen in member_roles:
                await member.remove_roles(fallen)
                await member.add_roles(citizen)
                log.info(f"Saved {member.name}.")
                await asyncio.sleep(3)

            elif avenger in member_roles:
                await member.remove_roles(avenger)
                await member.add_roles(citizen)
                log.info(f"Saved {member.name}.")
                await asyncio.sleep(3)

    @snap.command()
    @commands.is_owner()
    async def cleanup(self, ctx):
        if not self.snap_list:
            for mem_nm in self.snap_member_names:
                mem = ctx.guild.get_member_named(mem_nm)
                self.snap_list.append(mem)
            for mem_nm in self.snap_survivor_names:
                mem = ctx.guild.get_member_named(mem_nm)
                self.survivor_list.append(mem)
            await ctx.send("Loaded snap list.")

    @commands.command()
    @checks.is_in_channel(563348844075810836)
    async def free(self, ctx):
        fallen = ctx.guild.get_role(563349066088710144)
        citizen = ctx.guild.get_role(264072124069707798)
        coward = ctx.guild.get_role(563371239276806165)
        if fallen in ctx.author.roles:
            await ctx.author.remove_roles(fallen)
            await ctx.author.add_roles(coward, citizen)
            await ctx.send(f"{ctx.author.name} has fled. Pathetic.")


def setup(bot):
    bot.add_cog(DNSEA(bot))

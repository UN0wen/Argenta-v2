from discord.ext import commands
from cogs.utils import checks
import discord
import random
import aiohttp
from bs4 import BeautifulSoup, Comment
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
        self.default_channel = 244790887509393410  # saint-haven
        self.default_role = 264072124069707798
        self.snap_total = 0
        self.snap_list = []
        self.survivor_list = []
    """Clean commands"""

    @commands.group(pass_context=True)
    @checks.is_mod()
    async def clean(self, ctx):
        """Clean messages. (Only works in DNSEA)"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect clean subcommand passed.')

    @clean.command(hidden=False)
    @checks.is_mod()
    async def verify(self, ctx):
        """Verify the number of messages to delete.
        Displays the first and last message to be deleted, as well as the total number."""
        if ctx.channel.id == TH_id:
            delete_time = self.TH_delete_time
        elif ctx.channel.id == PT_id:
            delete_time = self.PT_delete_time
        else:
            await ctx.send('This command cannot be used here.')
            return

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

    @clean.command(hidden=False)
    @checks.is_mod()
    async def delete(self, ctx):
        """Delete old messages.
        Messages that are more than 7 days old in Trading House and 1 day old in PT-recruitment are deleted."""
        if ctx.channel.id == TH_id:
            delete_time = self.TH_delete_time
        elif ctx.channel.id == PT_id:
            delete_time = self.PT_delete_time
        else:
            await ctx.send('This command cannot be used here.')
            return

        time_threshold = datetime.datetime.utcnow() - delete_time
        pins = await ctx.channel.pins()
        last_pinned = pins[0]
        deleted = await ctx.channel.purge(limit=1000, before=time_threshold, after=last_pinned, bulk=True)
        await ctx.send(f'Deleted {len(deleted)} message(s).')

    @commands.group(pass_context=True)
    async def snap(self, ctx):
        """Snap commands for the Avengers Endgame event in DNSEA."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect snap subcommand passed.')

    def get_author(self, message):
        if not message.author.bot:
            return message.author

    @snap.command()
    @checks.is_admin()
    @commands.is_owner()
    async def check(self, ctx):
        """Initializes a list of users to be snapped.

        Half of all users who talked in the invoked channel will be chosen randomly to be saved."""
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
        """Lists people who will be snapped."""
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
        """The snap."""
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
        """Reverse the snap."""
        fallen = ctx.guild.get_role(563349066088710144)
        avenger = ctx.guild.get_role(563349115992539208)
        citizen = ctx.guild.get_role(264072124069707798)

        for member in ctx.guild.members:
            member_roles = member.roles
            if fallen in member_roles:
                # await member.remove_roles(fallen)
                await member.add_roles(citizen)
                log.info(f"Saved {member.name}.")
                await asyncio.sleep(1)

            elif avenger in member_roles:
                # await member.remove_roles(avenger)
                await member.add_roles(citizen)
                log.info(f"Saved {member.name}.")
                await asyncio.sleep(1)

    # @snap.command(hidden=True)
    # @commands.is_owner()
    # async def cleanup(self, ctx):
    #     if not self.snap_list:
    #         for mem_nm in self.snap_member_names:
    #             mem = ctx.guild.get_member_named(mem_nm)
    #             self.snap_list.append(mem)
    #         for mem_nm in self.snap_survivor_names:
    #             mem = ctx.guild.get_member_named(mem_nm)
    #             self.survivor_list.append(mem)
    #         await ctx.send("Loaded snap list.")

    @commands.command()
    @checks.is_in_channel(563348844075810836)
    async def free(self, ctx):
        """Let the fallen leave the soul stone as a Coward."""
        fallen = ctx.guild.get_role(563349066088710144)
        citizen = ctx.guild.get_role(264072124069707798)
        coward = ctx.guild.get_role(563371239276806165)
        if fallen in ctx.author.roles:
            await ctx.author.remove_roles(fallen)
            await ctx.author.add_roles(coward, citizen)
            await ctx.send(f"{ctx.author.name} has fled. Pathetic.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        b_roles = before.roles[1:]
        if not b_roles:
            a_roles = after.roles[1:]
            if len(a_roles) == 1 and a_roles[0].id == self.default_role:
                chan = self.bot.get_channel(self.default_channel)
                await chan.send(f"Hmph. {after.mention} has joined us.")

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    @commands.command()
    async def announcements(self, ctx, next_id):
        """Start grabbing announcements starting from ID next_id.

        Announcements are checked every 5 minutes, starting with <next_id>."""
        try:
            while not self.bot.is_closed():
                ret = await self.scrape(ctx, next_id)
                if ret:
                    log.info(f"Scraped {next_id}")
                    next_id = str(int(next_id) + 1)
                await asyncio.sleep(300)
        except asyncio.CancelledError:
            pass
        except (OSError, discord.ConnectionClosed):
            pass

    async def scrape(self, ctx, id):
        async with aiohttp.ClientSession() as session:
            url1 = f"https://sea.dragonnest.com/news/notice/all/{id}"
            html = await self.fetch(session, url1)
            if html is None:
                return None

            soup = BeautifulSoup(html, 'lxml')
            title = soup.find('th', attrs={'class': 'subject'})
            date = soup.find('th', attrs={'class': 'date'})
            content = soup.find('div', attrs={'class': 'cont'})
            type = soup.find('th', attrs={'class': 'category'})

            if "Patch" in title:
                img_url = "cogs/imgs/gamepatch.png"
            elif type == 'MAINT.':
                img_url = "cogs/imgs/mainte.png"
            else:
                img_url = "cogs/imgs/notice.png"

            string = f"**{title.string}**\n\n __{date.string}__\n"

            for child in content.children:
                if child.name == 'p':
                    if child.string is None:
                        string = self.recur_addstr(child, string)
                    elif child.strong is not None:
                        string += f"**{child.strong.string}**"
                    else:
                        string += child.string.strip()
                elif child.name == "hr":
                    string += '------------------------------------------------------------'
                elif isinstance(child, Comment):
                    pass
                else:
                    string += child

            with open(img_url, 'rb') as fp:
                await ctx.send(file=discord.File(fp))

            string = string.replace('\n\n\n\n', '\n\n')
            string = string.replace('\n\n\n', '\n')
            if len(string) > 2000:
                str_arr = string.splitlines(True)
                firstpart, secondpart = str_arr[:len(str_arr) // 2], str_arr[len(str_arr) // 2:]
                await ctx.send(" ".join(firstpart))
                await ctx.send(" ".join(secondpart))
            else:
                await ctx.send(string)
            return True

    def recur_addstr(self, root, string):
        for content in root.contents:
            if content.string is None:
                string = self.recur_addstr(content, string)
            elif content.name == 'strong':
                string += f"**{content.string}**"
            else:
                string += content.string

        return string

def setup(bot):
    bot.add_cog(DNSEA(bot))

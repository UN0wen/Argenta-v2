from discord.ext import commands
import discord
from cogs.utils import checks, db
import logging
import json
import csv
import asyncio
from calendar import month_name
from cogs.embeds.argenta_em import ArgentaEmbed

log = logging.getLogger(__name__)

# 'day', 'time', 'artist', 'album', 'type', 'title', 'streaming (spotify/apple)'

class KpopReleases(db.Table):
    def __init__(self, table_name=None):
        table = f"CREATE TABLE IF NOT EXISTS {table_name}"
        column = """year INTEGER,
        month INTEGER, 
        day INTEGER, 
        time TEXT,
        artist TEXT,
        album TEXT, 
        type TEXT,
        title TEXT,
        spotify TEXT, 
        apple TEXT, 
        PRIMARY KEY (artist, album)"""
        super().__init__(table, column)

# 'day', 'drama', 'release', 'artist',  'title', 'spotify'

class KpopOSTs(db.Table):
    def __init__(self, table_name=None):
        table = f"CREATE TABLE IF NOT EXISTS {table_name}"
        column = """year INTEGER,
        month INTEGER,
        day INTEGER, 
        drama TEXT,
        release TEXT,
        artist TEXT,
        title TEXT,
        spotify TEXT,
        PRIMARY KEY (artist, title)"""
        super().__init__(table, column)

class KpopImages(db.Table):
    def __init__(self, table_name=None):
        table = f"CREATE TABLE IF NOT EXISTS {table_name}"
        column = """artist TEXT,
        album TEXT,
        image_url TEXT,
        PRIMARY KEY (artist, album)"""
        super().__init__(table, column)

class Kpop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ost_table = KpopOSTs(table_name='kpop_ost')
        self.release_table = KpopReleases(table_name='kpop_release')
        self.images_table = KpopImages(table_name='kpop_image')
        self.emojis = ['\u23ee', '\u25c0', '\u25b6', '\u23ed', '\u274c']

    async def load_ost(self, connection):
        statement = '''INSERT INTO kpop_ost (day, drama, release, artist, title, spotify, year, month)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (artist, title) DO NOTHING'''

        with open("cogs/kpop/osts.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            for entry in data[1:]:
                entry[0] = int(entry[0])
                entry[6] = int(entry[6])
                entry[7] = int(entry[7])
            await connection.executemany(statement, data[1:])

    async def load_image(self, connection):
        statement = '''INSERT INTO kpop_image (artist, album, image_url)
        VALUES ($1, $2, $3)
        ON CONFLICT (artist, album) DO NOTHING'''

        with open("cogs/kpop/images.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            await connection.executemany(statement, data[1:])

    async def load_release(self, connection):
        statement = '''INSERT INTO kpop_release (day, time, artist,album,type,title,spotify,apple,year,month)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (artist, album) DO NOTHING'''

        with open("cogs/kpop/releases.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            for entry in data[1:]:
                entry[0] = int(entry[0])
                entry[8] = int(entry[8])
                entry[9] = int(entry[9])
            await connection.executemany(statement, data[1:])

    @commands.command()
    @commands.is_owner()
    async def reloadkpop(self, ctx):
        log.info("Preparing to reload Kpop Release database")
        connection = ctx.db

        await self.load_release(connection)
        log.info("Successfully loaded Release database")

        await self.load_ost(connection)
        log.info("Successfully loaded OST database")

        await self.load_image(connection)
        log.info("Successfully loaded images database")

        await ctx.send("Successfully reloaded Kpop database")

    @commands.group(pass_context=True)
    async def kpop(self, ctx):
        '''Kpop releases info. Contains data from 08/2017 until <current_month>'''
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect Kpop subcommand passed.')
        else:
            log.info(f"Kpop event requested for: {ctx.invoked_subcommand}.")

    async def paginator(self, ctx, embeds):
        def check(payload):
            if payload.user_id != ctx.author.id:
                return False

            if payload.message_id != message.id:
                return False

            emoji = str(payload.emoji)
            if emoji in self.emojis:
                return True
            else:
                return False

        i = 0
        message = await ctx.send(embed=embeds[i])

        for emoji in self.emojis:
            await message.add_reaction(emoji)

        emoji = ''

        log.info("Paginator starting...")
        
        while True:
            if emoji == '\u23ee':
                i = 0
            if emoji == '\u25c0':
                if i > 0:
                    i -= 1
            if emoji == '\u25b6':
                if i < len(embeds) - 1:
                    i += 1
            if emoji == '\u23ed':
                i = len(embeds)-1
            
            if emoji == '\u274c':
                try:
                    log.info("Paginator timed out.")
                    await message.clear_reactions()
                except:
                    pass
                finally:
                    break

            await message.edit(embed=embeds[i])

            try:
                payload = await self.bot.wait_for('raw_reaction_add', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                try:
                    log.info("Paginator timed out.")
                    await message.clear_reactions()
                except:
                    pass
                finally:
                    break
            
            emoji = str(payload.emoji)
            try:
                await message.remove_reaction(payload.emoji, discord.Object(id=payload.user_id))
            except:
                pass  # can't remove it so don't bother doing so

    def generate_release_embed(self, ctx, row):
        title = row['title']
        album = row['album']

        header = album if album else title

        if not header:
            header = "No name? What the fuck are they releasing"    
        
        e = ArgentaEmbed(ctx.author, title=header)

        release_date = f"{row['year']}-{row['month']}-{row['day']} {row['time']} KST"

        if row['artist']:
            e.add_field(name="Artist", value=row['artist'])

        e.add_field(name="Release Date", value=release_date)

        if title:
            e.add_field(name="Title Track", value=title)

        if album:
            e.add_field(name="Album", value=album)

        if row['type']:
            e.add_field(name='Type', value=row['type'])

        if row['spotify'] != "None":
            e.add_field(name='URL', value="Spotify")
            e.url = row['spotify']

        elif row['apple'] != "None":
            e.add_field(name='URL', value="Apple Music")
            e.url = row['apple']
        else:
            e.add_field(name='URL', value="None found")

        url = row['image_url']
        print(url)
        if url:
            e.set_image(url=url)
        e.colour = discord.Colour.dark_teal()

        return e

    @kpop.command()
    async def artist(self, ctx, num, *, name):
        '''Get the lastest <num> releases from artist <name> '''

        query = """SELECT * FROM kpop_release AS A
        LEFT OUTER JOIN kpop_image AS B 
        ON A.artist=B.artist AND A.album=B.album
        WHERE A.artist ILIKE $1
        ORDER BY
	    year DESC,
	    month DESC
        LIMIT $2;"""

        if num.lower() == "all":
            num = 9999999999
        else:
            try:
                num = int(num)
            except Exception:
                await ctx.send("Number of releases must be a number or 'all'.")
                return

        rows = await ctx.db.fetch(query, name, num)

        await ctx.send(f"{len(rows)} releases by {name} found.")

        # (day, time, artist,album,type,title,spotify,apple,year,month)
        if rows:
            if len(rows) == 1:
                log.info("Only 1 row requested, returning as an embed.")
                row = rows[0]
                e = self.generate_release_embed(ctx, row)
                await ctx.send(embed=e)
            else:
                embeds = []
                for row in rows:
                    e = self.generate_release_embed(ctx, row)
                    embeds.append(e)
                
                await self.paginator(ctx, embeds)
                
        log.info(f"Kpop artist with name {name} requested.")

    @kpop.command()
    async def release(self, ctx, release):
        '''Get all releases (title track or album name) named <release>'''

        query = """SELECT * FROM kpop_release AS A
        LEFT OUTER JOIN kpop_image AS B 
        ON A.artist=B.artist AND A.album=B.album
        WHERE A.album ILIKE $1
        OR A.title ILIKE $1
        ORDER BY
	    year DESC,
	    month DESC;"""

        rows = await ctx.db.fetch(query, release)

        await ctx.send(f"{len(rows)} releases by with name {release} found.")

        if rows:
            if len(rows) == 1:
                log.info("Only 1 row requested, returning as an embed.")
                row = rows[0]
                e = self.generate_release_embed(ctx, row)
                await ctx.send(embed=e)
            else:
                embeds = []
                for row in rows:
                    e = self.generate_release_embed(ctx, row)
                    embeds.append(e)
                
                await self.paginator(ctx, embeds)
                
        log.info(f"Kpop releases with name {release} requested.")

def setup(bot):
    bot.add_cog(Kpop(bot))

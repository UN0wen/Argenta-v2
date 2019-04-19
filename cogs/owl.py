from discord.ext import commands
import discord
from cogs.utils import checks
import datetime
import time
import logging
import json
import aiohttp

log = logging.getLogger(__name__)

api_endpoint = "https://api.overwatchleague.com/"

la_tz = datetime.timezone(-datetime.timedelta(hours=7))


class OWL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.maps = self.load_json('cogs/owl/maps.json')
        self.schedule = self.load_json('cogs/owl/schedule.json')
        self._d_events = {"live": "live-match",
                          "today": "matches"}

    async def fetch_json(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    async def get_json(self, event):
        async with aiohttp.ClientSession() as session:
            key = self._d_events.get(event, None)
            if key is not None:
                url = api_endpoint + key
                json_rsp = await self.fetch_json(session, url)
                return json_rsp

    def load_json(self, url):
        with open(url) as fd:
            return json.load(fd)

    def find_map(self, guid):
        for map in self.maps:
            if map['guid'] == guid:
                return map['name']['en_US'], map['gameModes'][0]['Name']

    @commands.group(pass_context=True)
    async def owl(self, ctx):
        """Display the status of Overwatch League matches."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Incorrect OWL subcommand passed.')
        else:
            log.info(f"OWL event requested for: {ctx.invoked_subcommand}.")

    @owl.command()
    async def live(self, ctx):
        """Display the current total and map score as well as the map pool of the current match."""
        rsp = await self.get_json('live')
        match = rsp['data']['liveMatch']
        title = f"{match['competitors'][0]['name']} - {match['competitors'][1]['name']}"

        e = discord.Embed(title=title, type="rich")
        e.add_field(name="Score", value=f"{match['scores'][0]['value']} - {match['scores'][1]['value']}", inline=False)
        if match['scores'][0]['value'] > match['scores'][1]['value']:
            url = match['competitors'][0]['logo']
        elif match['scores'][0]['value'] < match['scores'][1]['value']:
            url = match['competitors'][1]['logo']
        else:
            url = "https://i.redd.it/2918l9dw7og21.jpg"
        e.set_thumbnail(url=url)
        e.url = "https://www.twitch.tv/overwatchleague"

        for game in match['games']:
            map_info = self.find_map(game['attributes']['mapGuid'])
            name = f"{map_info[0]} - {map_info[1]}"
            if game['status'] == "CONCLUDED":
                val = f"{game['attributes']['mapScore']['team1']} - {game['attributes']['mapScore']['team2']}"
            elif game['status'] == "IN_PROGRESS":
                name = f"{map_info[0]} - {map_info[1]} (IN PROGRESS)"
                try:
                    val = f"{game['attributes']['mapScore']['team1']} - {game['attributes']['mapScore']['team2']}"
                except KeyError:
                    val = f"0 - 0"
            else:
                val = f"0 - 0"
            e.add_field(name=name, value=val, inline=False)

        await ctx.send(embed=e)

    @owl.command()
    async def today(self, ctx):
        """Displays all scores of today's matches."""
        today = datetime.datetime.now(tz=la_tz).date()
        try:
            sched = self.schedule[str(today)]
        except KeyError:
            await ctx.send("There are no Overwatch League matches today.")
            return
        title = f"Overwatch League 2019 Season - {today}"
        e = discord.Embed(title=title, type='rich')

        thumb = "https://i.redd.it/2918l9dw7og21.jpg"
        e.set_thumbnail(url=thumb)

        e.url = "https://www.twitch.tv/overwatchleague"

        for match_id in sched:
            async with aiohttp.ClientSession() as session:
                url = f"{api_endpoint}matches/{match_id}"
                match = await self.fetch_json(session, url)
                timestamp = int(match['startDate'])/1000
                dt = datetime.datetime.fromtimestamp(timestamp, tz=la_tz)
                name = f"Start time: {dt.strftime('%I:%M %p')} PST"
                comp = match['competitors'][0]['name'], match['competitors'][1]['name']

                if match['status'] == "CONCLUDED":
                    score = match['scores'][0]['value'], match['scores'][1]['value']
                    val = f"{comp[0]} {score[0]} - {score[1]} {comp[1]}"
                elif match['status'] == "IN_PROGRESS":
                    try:
                        score = match['scores'][0]['value'], match['scores'][1]['value']
                    except KeyError:
                        score = 0, 0
                    val = f"{comp[0]} {score[0]} - {score[1]} {comp[1]} (In Progress)"
                else:
                    val = f"{comp[0]} 0 - 0 {comp[1]}"

                e.add_field(name=val, value=name, inline=False)

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(OWL(bot))
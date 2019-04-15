from discord.ext import commands
from cogs.utils import checks
import logging
import aiohttp

from .embeds.alerts_em import AlertsEmbed
from .embeds.fissures import FissuresEmbed
from .embeds.sortie import SortieEmbed
from .embeds.timers import TimersEmbed
from .embeds.baro_em import BaroEmbed
from .embeds.invasion import InvasionsEmbed
log = logging.getLogger(__name__)

api_endpoint = "https://api.warframestat.us/pc/"


class Warframe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alerts_str = "alerts"
        self.cetus_str = "cetusCycle"
        self.fleet_str = "constructionProgress"
        self.earth_str = "earthCycle"
        self.fissures_str = "fissures"
        self.invasion_str = "invasions"
        self.nightwave_str = "nightwave"
        self.sortie_str = "sortie"
        self.vallis_str = "vallisCycle"
        self.baro_str = "voidTrader"
        self.timers = ["cetus", "earth", "vallis"]
        self._d_events = {"alerts": self.alerts_str,
                          "cetus": self.cetus_str,
                          "fleets": self.fleet_str,
                          "earth": self.earth_str,
                          "fissures": self.fissures_str,
                          "invasions": self.invasion_str,
                          "sortie": self.sortie_str,
                          "vallis": self.vallis_str,
                          "baro": self.baro_str
                            }
        self._d_embeds = {"alerts": "get_alerts_embed",
                          "timers": "get_timers_embed",
                          "fleets": "get_fleets_embed",
                          "fissures": "get_fissures_embed",
                          "invasions": "get_invasions_embed",
                          "sortie": "get_sortie_embed",
                          "baro": "get_baro_embed"
                            }

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

    @commands.command()
    async def wf(self, ctx, event):
        log.info(f"Wf event requested for: {event}.")
        if event == 'sorties':
            event = 'sortie'
        embed = await self.get_event_embed(event)
        await ctx.send(embed=embed)

    async def get_event_embed(self, event):
        """Get the embed for the the event_type wanted."""
        if event in self._d_embeds:
            return await getattr(self, self._d_embeds[event])(event)
        return None

    async def get_alerts_embed(self, event):
        rsp = await self.get_json(event)
        e = AlertsEmbed(rsp)
        return e

    async def get_fissures_embed(self, event):
        rsp = await self.get_json(event)
        e = FissuresEmbed(rsp)
        return e

    async def get_sortie_embed(self, event):
        rsp = await self.get_json(event)
        e = SortieEmbed(rsp)
        return e

    async def get_timers_embed(self, event):
        if event == "timers":
            cetus = await self.get_json(self.timers[0])
            earth = await self.get_json(self.timers[1])
            vallis = await self.get_json(self.timers[2])
            e = TimersEmbed(cetus, earth, vallis)
            return e

    async def get_baro_embed(self, event):
        rsp = await self.get_json(event)
        e = BaroEmbed(rsp)
        return e

    async def get_invasions_embed(self, event):
        rsp = await self.get_json(event)
        e = InvasionsEmbed(rsp)
        return e


def setup(bot):
    bot.add_cog(Warframe(bot))

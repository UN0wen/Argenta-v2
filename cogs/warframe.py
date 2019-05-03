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
from .embeds.nightwave import NightwaveEmbed
from .embeds.synthesis import SynthEmbed

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
        self.synthesis_str = "synthtargets"
        self._d_events = {"alerts": self.alerts_str,
                          "cetus": self.cetus_str,
                          "fleets": self.fleet_str,
                          "earth": self.earth_str,
                          "fissures": self.fissures_str,
                          "invasions": self.invasion_str,
                          "sortie": self.sortie_str,
                          "vallis": self.vallis_str,
                          "baro": self.baro_str,
                          "nightwave": self.nightwave_str,
                          "synthesis": self.synthesis_str
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

    @commands.group(pass_context=True)
    async def wf(self, ctx):
        """Display an event in Warframe.

        Valid events are:

        alerts: Currently active alerts.

        baro: Current baro rotation / time until next baro.

        timers: Cetus/Earth/Fortuna cycle timers.

        fissures: Currently active fissures.

        invasions: Currently active invasions.

        nightwave: Current weekly/daily rotation of Nightwave.

        sortie(s): Today's daily sortie rotation.

        Fleets: To be implemented.
        """
        log.info(f"Wf event requested.")

    @wf.command()
    async def alerts(self, ctx):
        rsp = await self.get_json("alerts")
        e = AlertsEmbed(rsp)
        await ctx.send(embed=e)

    @wf.command()
    async def fissures(self, ctx):
        rsp = await self.get_json("fissures")
        e = FissuresEmbed(rsp)
        await ctx.send(embed=e)

    @wf.command()
    async def sorties(self, ctx):
        rsp = await self.get_json("sortie")
        e = SortieEmbed(rsp)
        await ctx.send(embed=e)

    @wf.command()
    async def timers(self, ctx):
            cetus = await self.get_json(self.timers[0])
            earth = await self.get_json(self.timers[1])
            vallis = await self.get_json(self.timers[2])
            e = TimersEmbed(cetus, earth, vallis)
            await ctx.send(embed=e)

    @wf.command()
    async def baro(self, ctx):
        rsp = await self.get_json("baro")
        e = BaroEmbed(rsp)
        await ctx.send(embed=e)

    @wf.command()
    async def invasions(self, ctx):
        rsp = await self.get_json("invasions")
        e = InvasionsEmbed(rsp)
        await ctx.send(embed=e)

    @wf.command()
    async def nightwave(self, ctx):
        rsp = await self.get_json("nightwave")
        e1 = NightwaveEmbed(rsp, daily=True)
        e2 = NightwaveEmbed(rsp, daily=False)
        await ctx.send(embed=e1)
        await ctx.send(embed=e2)

    @wf.command()
    async def synthesis(self, ctx, *, name):
        async with aiohttp.ClientSession() as session:
            url = "https://api.warframestat.us/synthtargets"
            rsp = await self.fetch_json(session, url)
            e = SynthEmbed(rsp, name)
            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Warframe(bot))

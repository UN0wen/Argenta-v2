#!/usr/bin/env python

"""This module provide the SortieEmbed class used to generate an embed describing a sortie"""

# Import

from discord import Colour
from discord import Embed


class TimersEmbed(Embed):
    """Create an usable discord.py embed object describing the sorties"""

    def __init__(self, cetus, earth, vallis):
        title = "Timers"
        Embed.__init__(self, title=title, type="rich")

        self.colour = Colour.dark_orange()

        self.addCetusTimer(cetus)
        self.addEarthTimer(earth)
        self.addVallisTimer(vallis)

    def addCetusTimer(self, planet):
        """Add a field containing the mission description"""
        if planet['isDay']:
            day_night = "Day"
        else:
            day_night = "Night"

        self.add_field(name="Cetus", value=day_night + " - " + planet['timeLeft'] + " left.", inline=False)

    def addEarthTimer(self, planet):
        """Add a field containing the mission description"""
        if planet['isDay']:
            day_night = "Day"
        else:
            day_night = "Night"

        self.add_field(name="Earth", value=day_night + " - " + planet['timeLeft'] + " left.", inline=False)

    def addVallisTimer(self, planet):
        """Add a field containing the mission description"""
        if planet['isWarm']:
            day_night = "Warm"
        else:
            day_night = "Cold"

        self.add_field(name="Orb Vallis", value=day_night + " - " + planet['timeLeft'] + " left.", inline=False)

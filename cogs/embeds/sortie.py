#!/usr/bin/env python

"""This module provide the SortieEmbed class used to generate an embed describing a sortie"""

# Import

from discord import Colour
from discord import Embed


class SortieEmbed(Embed):
	"""Create an usable discord.py embed object describing the sorties"""

	def __init__(self, sortie):
		boss = sortie['boss']
		title = "Sortie: " + boss
		Embed.__init__(self, title=title, type="rich")
		if sortie['expired']:
			self.description = "Expired"
		else:
			self.description = "Ends in " + sortie['eta']
		self.colour = Colour.dark_orange()
		for mission in sortie['variants']:
			self.addFieldMission(mission)

	def addFieldMission(self, mission):
		"""Add a field containing the mission description"""
		node = mission['node']

		self.add_field(name=mission['missionType'], value=mission['modifier'] + " - " + node, inline = False)

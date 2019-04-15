#!/usr/bin/env python

#Import
import math

from discord import Colour
from discord import Embed


class InvasionEmbed(Embed):
	def __init__(self, invasion):
		title = "Invasion"
		Embed.__init__(self, title = title, type = "rich")
		self.description = invasion['node'] + " " + str(invasion['completion']) + "%"
		self.add_field(name = invasion['defendingFaction'], value = invasion['defenderReward']['asString'])
		self.colour = Colour.blue()
		if invasion['attackerReward']['items'] is not None:
			self.add_field(name=invasion['attackingFaction'], value= invasion['attackerReward']['asString'])
		else:
			self.add_field(name=invasion['attackingFaction'], value=".")


class InvasionsEmbed(Embed):
	"""Create an embed using a list of invasions 
	
	Parameters:
	-----------
	l_invasions: iterable of :class:`warframe.parser.invasions.Invasion`
	The list of invasions.
	
	platform: str [Optional]
	The platform those invasions are on.

	"""
	def __init__(self, l_invasions):
		title = "Invasions"
		Embed.__init__(self, title = title, type = "rich")
		self.description = "\n"
		self.colour = Colour.blue()
		for invasion in l_invasions:
			if invasion['completed'] is False:
				self.add_invasion(invasion)

	def add_invasion(self, invasion):
		"""Add an invasion to the embed
		
		Parameters:
		-----------

		invasion: :class:`warframe.parser.invasions.Invasion`
		The invasion we want to add.
		"""
		node = invasion['node']
		party_str = f"{invasion['attackingFaction']} vs {invasion['defendingFaction']}"
		field_name  = f"{party_str} - {node}"
		reward_str = self.getRewardStr(invasion)
		progress_str = self.getProgressStr(invasion)
		field_value = f"{reward_str}\n{progress_str}"
		self.add_field(name = field_name, value = field_value, inline = False)

	def getRewardStr(self, invasion):
		if invasion['attackerReward']['items'] is not None:
			reward_str = f"{invasion['attackerReward']['asString']} | {invasion['defenderReward']['asString']}"
		else:
			reward_str = invasion['defenderReward']['asString']
		return reward_str

	def getProgressStr(self, invasion):
		"""Return a string containing the progress of the mission"""
		count = invasion['count']
		goal = invasion['requiredRuns']
		if invasion['attackerReward']['items'] is not None:
			count_att = (goal - math.fabs(count)) / 2
			progress_att = self.getProgress(count_att, goal)
			progress_def = 100 - progress_att
		else:
			progress_def = self.getProgress(count, goal)
			progress_att = 100 - progress_def
		progress_bar = self.getProgressBar(progress_att, progress_def)
		progress_str = "{0:.1f} % {2} {1:.1f} %".format(progress_att, progress_def, progress_bar)
		return progress_str

	def getProgress(self, count, goal):
		return float((math.fabs(count) / goal)) * 100

	def getProgressBar(self, progress_att, progress_def):
		nb_char = 10
		nb_att = round(progress_att / 10)
		nb_def = nb_char - nb_att
		bar_att = self.getBar(nb_att)
		bar_def = self.getBar(nb_def)
		progress_bar = "|{0}x{1}|".format(bar_att, bar_def)
		return progress_bar

	def getBar(self, size, char = "—"):
		"""Return a bar of the size given in parameter """
		ret = ""
		for i in range(0, size):
			ret = ret + char
		return ret

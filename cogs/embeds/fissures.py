#!/usr/bin/env python

"""Provide FissuresEmbed class which is an embed listing Fissures"""

from discord import Colour
from discord import Embed


class FissuresEmbed(Embed):

	def __init__(self, fissures):
		"""Generate an embed containing the list of fissures

		Parameters:
		-----------

		l_fissures: iterable of :class:`warframe.parser.fissure.Fissure`
		The list of fissures.

		platform: str [Optional]
		The platform those fissures are on.
		"""

		title = "Fissures"
		Embed.__init__(self, title = title, type = "rich")
		self.url = "http://warframe.wikia.com/wiki/Void_Fissure"
		for fissure in fissures:
			self.add_fissure(fissure)
		self.colour = Colour.teal()

	def add_fissure(self, fissure):
		"""Add a field in the embed that contain the fissure given in parameter
		
		Parameter:
		----------

		fissure : instance of :class:`warframe.parser.fissure.Fissure`
		"""

		node = fissure['node']
		mission_type = fissure['missionType']

		fissure_type = fissure['tier']
		expiry = fissure['eta']

		field_name = "[" + fissure_type + "] " + mission_type
		field_value = node + " - " + expiry

		self.add_field(name=field_name, value=field_value, inline = False)



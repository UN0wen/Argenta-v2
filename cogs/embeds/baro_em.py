#!/usr/bin/env python

# Import
import re

from discord import Colour
from discord import Embed


class BaroEmbed(Embed):
	def __init__(self, baro):
		node = baro['location']
		baro_url = "http://warframe.wikia.com/wiki/Baro_Ki%27Teer"
		baro_image = "https://vignette.wikia.nocookie.net/warframe/images/1/12/BaroBanner.png"
		color = int("0x10C4BC", 0)
		title = f"[PC] Baro Ki'Teer - {node}"
		Embed.__init__(self, title=title, type = "rich")
		
		if baro['active']:
			self.description = f"Leave in {baro['endString']}"
		else:
			self.description = f"Arrive in {baro['startString']}"
		self.url = baro_url
		self.set_thumbnail(url=baro_image)
		self.colour = color
		self._unlocalized_str = "/Lotus/"
		self._separator = "/"
		self._placeholder = "[PH] "
		for item in baro['inventory']:
			self.addItem(item)
			
	def addItem(self, item):
		field_name = item['item']
		ducat = item['ducats']
		credit = item['credits']
		if ducat > 0:
			field_value = f"{ducat} ducats + {credit} credits"
		else:
			field_value  = f"{credit} credits"
		self.add_field(name=field_name, value=field_value)

	def getItemName(self, item, debug):
		"""Retrieve the name of the item, if unlocalised give a PH name, unless debug is set to True."""
		name = item.getName()
		if (name.startswith(self._unlocalized_str) == False or debug == True):
			return (name)
		l_name = name.split(self._separator)
		name = self._placeholder + re.sub(r'([a-z])([A-Z])', r'\1 \2', l_name[-1])
		return (name)

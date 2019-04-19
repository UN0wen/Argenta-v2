#!/usr/bin/env python

"""Provide AlertsEmbed class which is an embed listing alerts"""

from discord import Colour
from discord import Embed


class AlertsEmbed(Embed):
	
	def __init__(self, alerts):
		"""Generate an embed containing the list of alerts

		Parameters:
		-----------

		l_alerts: iterable of :class:`warframe.parser.alerts.Alerts`
		The list of alerts.

		platform: str [Optional]
		The platform those alerts are on.


		Attributes:
		-----------

		_desc_gotl: str
		The description present if the alert is a gift of the lotus
		"""

		self._desc_gotl = "Gift of The Lotus"
		title = "Alerts"
		Embed.__init__(self, title=title, type="rich")
		if alerts is not None:
			for alert in alerts:
				self.add_alert(alert)
		self.colour = Colour.gold()

	def add_alert(self, alert):
		"""Add a field in the embed containing the alert.
		
		Parameters:
		-----------
		alert: the alert to add to the embed
		"""
		node = alert['mission']['node']
		desc = alert['mission']['description']
		level = f"{alert['mission']['minEnemyLevel']} - {alert['mission']['maxEnemyLevel']}"
		faction = alert['mission']['faction']
		mission_type = alert['mission']['type']
		rewards = alert['mission']['reward']['asString']
		eta = alert['eta']

		field_value = faction + " - " + node + "\nLevel: " + level

		if desc == self._desc_gotl:
			field_name = "{Gift Of The Lotus} [" + mission_type + "] " + rewards
		else:
			field_name = "[" + mission_type + "] " + rewards
		field_value = field_value + "\nTime Remaining: " + eta
		self.add_field(name=field_name, value=field_value, inline=False)


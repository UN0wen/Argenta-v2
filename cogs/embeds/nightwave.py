#!/usr/bin/env python

# Import
from discord import Embed
from datetime import datetime, timezone, timedelta
import dateutil.parser


class NightwaveEmbed(Embed):
    def __init__(self, nw, daily=False):
        color = int("0x10C4BC", 0)
        if not daily:
            mission_str = "Weekly Challenges"
        else:
            mission_str = "Daily Challenges"
        self.daily = daily
        title = f"Nightwave Season {nw['season']} - {mission_str}"
        Embed.__init__(self, title=title, type="rich")
        self.colour = color
        for challenge in nw['activeChallenges']:
            if not daily and 'isDaily' not in challenge:
                self.addChallenge(challenge)
            elif daily and 'isDaily' in challenge:
                self.addChallenge(challenge)

    def addChallenge(self, challenge):
        field_name = challenge['title']
        desc = f"{challenge['desc']}\nReputation: {challenge['reputation']}"

        if self.daily:
            expiry = dateutil.parser.parse(challenge['expiry'])
            time_remaining = expiry - datetime.now(timezone.utc)
            print(str(time_remaining))
            time_str = f"""{time_remaining.days * 24 + time_remaining.seconds//3600}h {(time_remaining.seconds//60)%60}m {time_remaining.seconds%60}s"""
            desc += f'\nTime remaining: {time_str}'

        self.add_field(name=field_name, value=desc)

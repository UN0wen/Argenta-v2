from discord import Colour
from discord import Embed


class SynthEmbed(Embed):
    def __init__(self, synthesis, name):
        name = name.title()
        title = f"Synthesis Target - {name}"
        Embed.__init__(self, title=title, type="rich")
        if synthesis is not None:
            for target in synthesis:
                if target['name'] == name:
                    self.add_target(target)
        self.colour = Colour.gold()

    def add_target(self, target):
        """Add a field in the embed containing the target.

        Parameters:
        -----------
        target: the target to add to the embed
        """
        loc = target['locations']
        for node in loc:
            field_name = f"{node['mission'].title()} - {node['planet'].title()} ({node['type'].title()})"
            level = node['level']
            spawn_rate = node['spawn_rate']
            faction = node['faction'].title()
            field_value= f"Faction: {faction}\nLevel: {level}\nSpawn rate: {spawn_rate}"
            self.add_field(name=field_name, value=field_value, inline=False)


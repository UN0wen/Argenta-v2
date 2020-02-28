from discord import Embed
from datetime import datetime

class ArgentaEmbed(Embed):
    def __init__(self, caller=None, *args, **kwargs):
        if not caller:
            return
        super().__init__(**kwargs)
        request = f"Requested by: {caller.name} - ID: {caller.id}"
        url = str(caller.avatar_url)
        self.set_footer(text=request, icon_url=url)
        self.type = 'rich'
        self.timestamp = datetime.now()
from discord import Colour
from discord import Embed
import requests


class MarketEmbed(Embed):
    def __init__(self, t, name, url_name):
        name = name.title()
        self.id = ""
        self.assets_url = "https://warframe.market/static/assets/"
        title = f"warframe.market data - {name}"
        Embed.__init__(self, title=title, type="rich")
        self.colour = Colour.gold()
        self.url_name = url_name
        self.api_url = f"https://api.warframe.market/v1/items/{url_name}"
        self.add_desc()
        if t in ['buy', 'b']:
            self.add_buy()
        else:
            self.add_sell()

    def add_desc(self):
        rsp = requests.get(self.api_url).json()['payload']['item']
        self.id = rsp['id']
        for items in rsp['items_in_set']:
            if items['id'] == self.id:
                self.description = items['en']['description']
                self.url = f"https://warframe.market/items/{self.url_name}"
                self.set_thumbnail(url=f"{self.assets_url}{items['thumb']}")

    def add_buy(self):
        return

    def add_sell(self):
        return




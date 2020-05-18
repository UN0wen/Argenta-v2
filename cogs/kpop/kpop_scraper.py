import config
import praw
from bs4 import BeautifulSoup
import lxml
import json
import csv
from time import sleep

from calendar import month_name
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# subclass JSONEncoder


class ScheduleEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Release:
    def __init__(self):
        super().__init__()
        self.apple = "None"
        self.spotify = "None"
        self.day = self.time = self.artist = self.album = self.type = self.title = "None"
        self.month = self.year = 0

    def __str__(self):
        return f"{self.year}-{self.month} {self.day} - {self.time} - {self.artist} - {self.album} - {self.type} - {self.title} - {self.spotify} - {self.apple}"


class OST:
    def __init__(self):
        super().__init__()
        self.spotify = "None"
        self.month = self.year = 0
        self.day = self.drama = self.release = self.artist = self.title = self.spotify = "None"

    def __str__(self):
        return f"{self.year}-{self.month} {self.day} - {self.drama} - {self.release} - {self.artist} - {self.title} - {self.spotify}"


class RedditScraper:
    def __init__(self):
        super().__init__()
        self.reddit = praw.Reddit(client_id=config.REDDIT_CLIENTID,
                                  client_secret=config.REDDIT_SECRET, user_agent=config.REDDIT_USERAGENT, refresh_token=config.REDDIT_REFRESH_TOKEN)
        self.subreddit = self.reddit.subreddit("kpop")
        self.years = range(2017, 2021)
        self.months = range(1, 13)
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year

    # call this with main if you need a data dump
    def get_all_data(self):
        ost_data = []
        release_data = []

        # accumulate data
        for y in self.years:
            if y > self.current_year:
                break
            for m in self.months:
                if y == 2017 and m < 8:
                    continue
                mn = month_name[m].lower()
                try:
                    html = self.get_page(mn, y)
                    print(mn, y)
                    release, ost = self.parse_page(html, m, y)
                    release_data.append(release)
                    ost_data.append(ost)
                    sleep(.5)
                except Exception as err:
                    print(err)
                    break

        # dump data
        with open("releases.json", "w") as f:
            f.write(json.dumps(release_data, indent=2, cls=ScheduleEncoder))

        with open("osts.json", "w") as f:
            f.write(json.dumps(ost_data, indent=2, cls=ScheduleEncoder))

    # get new data as dict for the bot to update
    def get_new_data(self):
        ost_data = []
        release_data = []

        # accumulate data
        for y in self.years:
            if y > self.current_year:
                break
            elif y < self.current_year:
                continue
            for m in self.months:
                if m < self.current_month:
                    continue
                mn = month_name[m].lower()
                try:
                    html = self.get_page(mn, y)
                    print(mn, y)
                    release, ost = self.parse_page(html, m, y)
                    release_data.append(release)
                    ost_data.append(ost)
                    sleep(.5)
                except Exception as err:
                    print(err)
                    break

        # dump data
        print(ost_data)
        print(release_data)
    
    def get_page(self, month, year):
        url = f"upcoming-releases/{year}/{month}"
        html = self.subreddit.wiki[url].content_html
        return html

    def parse_page(self, html, month, year):
        soup = BeautifulSoup(html, 'lxml')

        wiki = soup.find("div", attrs={"class": "md wiki"})
        tables = wiki.find_all("table")
        releases = self.parse_schedule_table(tables[0], month, year)
        osts = self.parse_ost_table(tables[1], month, year)

        return (releases, osts)

    def parse_schedule_table(self, table, month, year):
        release_list = []
        row_marker = 0
        day = ""
        time = ""
        table_body = table.find("tbody")
        # row format 'day', 'time', 'artist', 'album', 'type', 'title', 'streaming (spotify/apple)'
        for row in table_body.find_all('tr'):
            release = Release()
            columns = row.find_all('td')

            # columns 0 and 1 might be empty, use values of prev columns if possible
            day = columns[0].get_text() if columns[0].get_text() else day
            time = columns[1].get_text() if columns[1].get_text() else time

            release.day = int(''.join(i for i in day if i.isdigit()))
            release.time = time
            release.month = month
            release.year = year
            release.artist = columns[2].get_text()
            release.album = columns[3].get_text()
            release.type = columns[4].get_text()
            release.title = columns[5].get_text()

            for link in columns[6].find_all("a"):
                if "Spotify" in link.get_text():
                    release.spotify = link["href"]
                elif "Apple" in link.get_text():
                    release.apple = link["href"]

            release_list.append(release)

        return release_list

    def parse_ost_table(self, table, month, year):
        ost_list = []
        row_marker = 0
        day = ""
        table_body = table.find("tbody")
        # row format 'day', 'drama', 'release', 'artist',  'title', 'spotify'
        for row in table_body.find_all('tr'):
            ost = OST()
            columns = row.find_all('td')

            # columns 0 and 1 might be empty, use values of prev columns if possible
            day = columns[0].get_text() if columns[0].get_text() else day
            ost.day = int(''.join(i for i in day if i.isdigit()))
            ost.drama = columns[1].get_text()
            ost.release = columns[2].get_text()
            ost.artist = columns[3].get_text()
            ost.title = columns[4].get_text()
            ost.spotify = columns[5].find(
                "a")["href"] if columns[5].get_text() else "None"
            ost.month = month
            ost.year = year
            ost_list.append(ost)

        return ost_list

    def json_to_csv(self):
        release_fields = ['day', 'time', 'artist', 'album',
                          'type', 'title', 'spotify', 'apple', 'year', 'month']
        ost_fields = ['day', 'drama', 'release', 'artist',
                      'title', 'spotify', 'year', 'month']
        with open("releases.json", "r") as f:
            release_data = json.load(f)
            with open("releases.csv", "w", encoding="utf-8", newline='') as f2:
                writer = csv.DictWriter(f2, release_fields)
                writer.writeheader()
                for month in release_data:
                    if month:
                        for entry in month:
                            try:
                                writer.writerow(entry)
                            except ValueError as err:
                                print(err)
                                break

        with open("osts.json", "r") as f:
            ost_data = json.load(f)
            with open("osts.csv", "w",  encoding="utf-8", newline='') as f2:
                writer = csv.DictWriter(f2, ost_fields)
                writer.writeheader() 
                for month in ost_data:
                    if month:
                        for entry in month:
                            try:
                                writer.writerow(entry)
                            except ValueError as err:
                                print(err)

        
class SpotifyScraper:
    def __init__(self):
        super().__init__()
        ccm = SpotifyClientCredentials(
            client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
        self.spotify = spotipy.Spotify(client_credentials_manager=ccm)

    def get_image_data(self, album):
        return album["images"][0]["url"]

    def get_all_release_data(self):
        all_data =  []
        with open("releases.json", "r") as f:
            with open("images.csv", "w",  encoding="utf-8", newline='') as f2:
                writer = csv.DictWriter(f2, ["artist", "album", "image_url"])
                writer.writeheader()

                release_data = json.load(f)
                for month in release_data:
                    if month:
                        for entry in month:
                            if entry["spotify"] != "None":
                                try:
                                    album = self.spotify.album(
                                        entry["spotify"])
                                except Exception as e:
                                    try:
                                        album = self.spotify.track(
                                            entry["spotify"])["album"]
                                    except Exception as e :
                                        continue
                                url = self.get_image_data(album)
                                image_data = {"artist": entry["artist"],
                                              "album": entry["album"],
                                              "image_url": url}
                                writer.writerow(image_data)
                                all_data.append(image_data)

        with open("images.json", "w") as f:
            f.write(json.dumps(all_data, indent=2))

    def get_track(self, track):
        return self.spotify.track(track)["album"]

if __name__ == "__main__":
    kpop = RedditScraper()

    kpop.get_new_data()
    # track = kpop.get_track("https://play.spotify.com/track/4hznPzvJbEJxcxZA6NbsWx")
    # with open("temp.json", "w", encoding="utf8") as f:
    #     json.dump(track, f, indent=2)

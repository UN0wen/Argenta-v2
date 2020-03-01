# Taken from https://github.com/jvlflame/JAV-Sort-Scrape-javlibrary/blob/master/1.%20sort_jav.py

import cloudscraper
from bs4 import BeautifulSoup 
scraper = cloudscraper.create_scraper()

def check_valid_response(html, vid_id):
    """check if the html was the page we wanted"""
    s = "<title>" + vid_id
    if s in html:
        return True
    return False


def get_correct_url(html, vid_id):
    """get the url that's the exact video we want from a link with multiple results"""
    try:
        url_portion = html.split(
            '" title="' + vid_id + ' ')[0].split('><a href=".')[1]
        return "http://www.javlibrary.com/en" + url_portion
    except:
        return None


def check_vid_id_has_dash(vid_id):
    """Check if the video id has a dash and return one with it if it doesn't"""
    if '-' not in vid_id:
        dash_split = vid_id.split(" ")
        if len(dash_split) > 1:
            vid_id = dash_split[0] + "-" + dash_split[1]
        else:
            for i in range(len(vid_id)):
                if vid_id[i] in '0123456789':
                    vid_id = vid_id[:i] + '-' + vid_id[i:]
                    break
    return vid_id


def get_javlibrary_url(vid_id):
    """get the URL of the video on javlibrary
    returns None if a URL could not be found"""
    vid_id = check_vid_id_has_dash(vid_id.upper())
    try:
        search_url = "http://www.javlibrary.com/en/vl_searchbyid.php?keyword=" + vid_id
        html = get_url_response(search_url, vid_id)

        # we didn't get a valid response
        if html == None:
            return None
        return html
    except:
        return None


def get_url_response(url, vid_id):
    """get the response from a given URL
    includes the video id to verify the URL is correct"""
    # opener = AppUrlopener()
    # response = opener.open(url)
    # contents = (response.read()).decode()
    global scraper
    contents = scraper.get(url).content.decode()
    if check_valid_response(contents, vid_id):
        return contents  # the URL was good
    else:
        # this may return None if the correct URL does not exist
        return get_url_response(get_correct_url(contents, vid_id), vid_id)


def get_image_url_from_html(html):
    """get the url of the image from the supplied html for the page"""
    return "http:" + html.split('<img id="video_jacket_img" src="')[1].split('" width')[0]

def get_metadata(html):
    return

def get_javlibrary(vid_id):
    """Return a list of values for a Jav video if found on JavLib:
    link: link to the search term on JavLibrary
    title: full name of the JAV 
    actresses: actresses participating
    cover_url: url to cover image
    genre: genres for the JAV
    label: publisher
    
    """
    html = get_javlibrary_url(vid_id)
    if not html:
        return None
    soup = BeautifulSoup(html, 'lxml')

    # title
    title = soup.title.string.split("- JAVLibrary")[0] 

    # release date
    video_date = soup.find("div", id="video_date").stripped_strings
    release_date = [v for v in video_date][1]

    # video length in minutes
    video_length = soup.find("div", id="video_length").stripped_strings
    length = [v for v in video_length][1]

    # label of the video
    video_label = soup.find("div", id="video_label").stripped_strings
    label = [v for v in video_label][1]

    # genres
    video_genres = soup.find("div", id="video_genres")
    genres = video_genres.find_all("span", "genre")
    genre_string = ", ".join([g.string for g in genres])
    
    # actresses
    video_cast = soup.find("div", id="video_cast")
    actresses = video_cast.find_all("span", "star")
    actress_string = ", ".join([a.string for a in actresses])

    # cover image
    cover_url = soup.find("img", id="video_jacket_img")['src']

    d = {}
    d['title'] = title
    d['release_date'] = release_date
    d['length'] = length 
    d['label'] = label 
    d['genre'] = genre_string
    d['actresses'] = actress_string
    d['cover_url'] = cover_url 
    return d
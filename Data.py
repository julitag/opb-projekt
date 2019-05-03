import requests
import bs4
import re
## info on setting up webdriver at https://likegeeks.com/python-web-scraping/
from selenium import webdriver

browser = webdriver.Chrome(executable_path=r"C:/Users/Gašper/Desktop/projekt OPB/chromedriver.exe") ## location of Chrome webdriver on computer
req = requests.get("https://boardgamegeek.com/browse/boardgame")
soup = bs4.BeautifulSoup(req.text, "html.parser")

## titles of top 100 games
collection = soup.select(".collection_objectname") ## select class .
titles = []
for i in collection:
    title = []
    title.extend(i.stripped_strings)
    titles.append(title[0])

## subtables, one for each game + an additional starting one
table = soup.find(lambda tag: tag.name == "table" and tag.has_attr("id") and tag["id"] == "collectionitems")
rows = table.find_all(lambda tag: tag.name == "tr")

## list of web page suffices
games = []
for row in rows[1::]:
    a = row.find("a", href = True)
    games.append(a["href"])

## game attributes
gtime = []
players = []
age = []
artists = []
designers = []
genre = []

i = 0
for game in games[:10]:
    ## web page of current game created on Chrome webdriver - Selenium
    browser.get("https://boardgamegeek.com" + game)
    s = bs4.BeautifulSoup(browser.page_source, "html.parser")

    primary = s.find_all("div", class_ = "gameplay-item-primary")
    ## number of players list
    g = []
    g.extend(primary[0].stripped_strings)
    players.append(''.join(g))

    ## time of playing list
    g = []
    g.extend(primary[1].stripped_strings)
    gtime.append(''.join(g))

    ## age list
    g = []
    g.extend(primary[2].stripped_strings)
    age.append(''.join(g))

    primary = s.find_all(class_="credits")
    ## designers
    secondary = primary[1].find_all("a", href=re.compile("designer"))
    g = []
    for name in secondary:
        g.append(name["title"])
    designers.append(g)

    ## artists
    secondary = primary[1].find_all("a", href=re.compile("artist"))
    g = []
    for name in secondary:
        g.append(name["title"])
    artists.append(g)

    i = i+1

#################################################################################

## test for Gloomhaven game
GH =[titles[0], players[0], gtime[0], age[0], artists[0], designers[0]]

""" browser.get("https://boardgamegeek.com" + games[0])
s = bs4.BeautifulSoup(browser.page_source, "html.parser")
primary = s.find_all(class_="credits")
de = primary[1].find_all("a", title=True)
de = primary[1].find_all("a", href=re.compile("artist"))
for d in de:
    print(d["title"])

primary = s.find_all("div", class_ = "credits")
a = primary[1]["title"]
g = []
g.extend(primary[1].stripped_strings) """
import requests
import bs4
import re
## navodila za nastavitev https://likegeeks.com/python-web-scraping/
from selenium import webdriver
import csv as csv
import os

browser = webdriver.Chrome("pythonpodatki\chromedriver.exe")
req = requests.get("https://boardgamegeek.com/browse/boardgame")
soup = bs4.BeautifulSoup(req.text, "html.parser")

## naslovi top 100 iger
collection = soup.select(".collection_objectname") ## select class .
titles = []
for i in collection:
    title = []
    title.extend(i.stripped_strings)
    titles.append(title[0])

## podtabele, zacetna in nato po ena za vsako izmed 100 iger
table = soup.find(lambda tag: tag.name == "table" and tag.has_attr("id") and tag["id"] == "collectionitems")
rows = table.find_all(lambda tag: tag.name == "tr")

## seznam web page koncnic
games = []
for row in rows[1::]:
    a = row.find("a", href = True)
    games.append(a["href"])

## atributi iger
gtime = []
players = []
age = []
artists = []
designers = []
genre = []

i = 0
for game in games:
    ## web page trenutne igre, ki se ga ustvari na webdriverju
    browser.get("https://boardgamegeek.com" + game)
    s = bs4.BeautifulSoup(browser.page_source, "html.parser")

    primary = s.find_all("div", class_ = "gameplay-item-primary")
    ## seznam st. igralcev
    g = []
    g.extend(primary[0].stripped_strings)
    players.append(''.join(g))

    ## dolzina igranja
    g = []
    g.extend(primary[1].stripped_strings)
    gtime.append(''.join(g))

    ## starost
    g = []
    g.extend(primary[2].stripped_strings)
    age.append(''.join(g))

    primary = s.find_all(class_="credits")
    ## designerji
    secondary = primary[1].find_all("a", href=re.compile("designer"))
    g = []
    for name in secondary:
        g.append(name["title"])
    designers.append(g)

    ## artisti
    secondary = primary[1].find_all("a", href=re.compile("artist"))
    g = []
    for name in secondary:
        g.append(name["title"])
    artists.append(g)

    i = i+1

## To show proper characters in excel you have to open new excel file and import data from games.csv using utf-8 encoding.
with open('pythonpodatki\igre.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Game", "Nr. of player", "Playing time", "Age", "Designers", "Artists"])
    for i in range(len(titles)):
        wr.writerow([titles[i], players[i], gtime[i], age[i], designers[i], artists[i]])
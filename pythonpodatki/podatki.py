import requests
import bs4
import re
## navodila za nastavitev https://likegeeks.com/python-web-scraping/
from selenium import webdriver
import csv as csv
import os

browser = webdriver.Chrome("pythonpodatki/chromedriver.exe")

## naslovi iger
titles = []
## atributi iger
mintime = []
maxtime = []
minplayers = []
maxplayers = []
release = []
age = []
genre = []
## ustvarjalci
artists = []
designers = []
publisher = []

## range(n) za top n * 100 iger
for i in range(5):
    req = requests.get("https://boardgamegeek.com/browse/boardgame/page/%s" % str(i+1))
    soup = bs4.BeautifulSoup(req.text, "html.parser")

    ## naslov in datum izdaje za naslednjih 100 iger
    collection = soup.select(".collection_objectname") ## select class .
    for i in collection:
        title = []
        title.extend(i.stripped_strings)
        titles.append(title[0])
        release.append(int(re.search(r'\d+', title[1]).group()))

    ## podtabele, zacetna in nato po ena za vsako izmed 100 iger
    table = soup.find(lambda tag: tag.name == "table" and tag.has_attr("id") and tag["id"] == "collectionitems")
    rows = table.find_all(lambda tag: tag.name == "tr")

    ## seznam web page koncnic
    games = []
    for row in rows[1::]:
        a = row.find("a", href = True)
        games.append(a["href"])
    
    for game in games:
        ## web page trenutne igre, ki se ga ustvari na webdriverju
        browser.get("https://boardgamegeek.com" + game)
        s = bs4.BeautifulSoup(browser.page_source, "html.parser")

        primary = s.find_all("div", class_ = "gameplay-item-primary")

        # min & max stevilo igralcev, if zanka za primer ko imamo tocno doloceno stevilo igralcev
        minimum = primary[0].find('span', {'ng-if': 'min > 0'})
        minplayers.append(int(minimum.text))

        maksimum = primary[0].find('span', {'ng-if': 'max>0 && min != max'})
        if maksimum != None:
            maxplayers.append(int(re.search(r'\d+', maksimum.text).group()))
        else:
            maxplayers.append(int(minimum.text))

        # min & max dolzina igranja, if zanka za primer ko se igra tocno dolocen cas
        minimum = primary[1].find('span', {'ng-if': 'min > 0'})
        mintime.append(int(minimum.text))

        maksimum = primary[1].find('span', {'ng-if': 'max>0 && min != max'})
        if maksimum != None:
            maxtime.append(int(re.search(r'\d+', maksimum.text).group()))
        else:
            maxtime.append(int(minimum.text))
        
        ## starost, if zanka za primer ko starost ni podana
        if re.search(r'\d+', primary[2].text) != None:
            age.append(int(re.search(r'\d+', primary[2].text).group()))
        else:
            age.append(None)

        primary = s.find_all(class_="feature-description")
        ## žanr
        g = primary[1].find_all("a", href=re.compile("category"))
        names = []
        for name in g:
            names.append(name["title"])
        genre.append(names)

        primary = s.find_all(class_="credits")
        ## designerji
        des = primary[1].find_all("a", href=re.compile("designer"))
        names = []
        for name in des:
            names.append(name["title"])
        designers.append(names)

        ## artisti
        art = primary[1].find_all("a", href=re.compile("artist"))
        names = []
        for name in art:
            names.append(name["title"])
        artists.append(names)

        ## založba
        pub = primary[1].find_all("a", href=re.compile("publisher"))
        publisher.append(pub[0].text)

## To show proper characters in excel you have to open new excel file and import data from games.csv using utf-8 encoding.
with open('pythonpodatki/igre.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Igra", "Min. st. igralcev", "Max. st. igralcev", "Min cas", "Max. cas", "Leto izdaje", "Min. starost"])
    for i in range(len(titles)):
        wr.writerow([titles[i], minplayers[i], maxplayers[i], mintime[i], maxtime[i], release[i], age[i]])

with open('pythonpodatki/ustvarjalci.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Game", "Designers", "Artists", "Publisher"])
    for i in range(len(titles)):
        wr.writerow([titles[i], designers[i], artists[i], publisher[i]])

with open('pythonpodatki/zvrst.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Game", "Zvrst"])
    for i in range(len(titles)):
       wr.writerow([titles[i], genre[i]])
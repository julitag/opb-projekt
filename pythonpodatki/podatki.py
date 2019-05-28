import requests
import bs4
import re
## navodila za nastavitev https://likegeeks.com/python-web-scraping/
from selenium import webdriver
import csv as csv
import os

browser = webdriver.Chrome("pythonpodatki/chromedriver.exe")

## koncnice in imena
games = []
url = []
games_exp = []
url_exp= []

## atributi iger
mintime = []
maxtime = []
minplayers = []
maxplayers = []
release = []
age = []

## atributi dodatkov
mintime_exp = []
maxtime_exp = []
minplayers_exp = []
maxplayers_exp = []
release_exp = []
age_exp = []
basic = []

## ustvarjalci
artists = set()
designers = set()
publisher = set()
artist_game = []
designer_game = []
publisher_game = []

## zvrst
genre = set()
genre_game = []

## range(n) za top n * 100 iger
for i in range(5):
    req = requests.get("https://boardgamegeek.com/browse/boardgame/page/%s" % str(i+1))
    soup = bs4.BeautifulSoup(req.text, "html.parser")

    ## naslov in leto izdaje za naslednjih 100 iger
    collection = soup.select(".collection_objectname") ## select class .
    for i in collection:
        title = []
        title.extend(i.stripped_strings)
        games.append(title[0])
        release.append(int(re.search(r'\d+', title[1]).group()))

    ## podtabele, zacetna in nato po ena za vsako izmed 100 iger
    table = soup.find(lambda tag: tag.name == "table" and tag.has_attr("id") and tag["id"] == "collectionitems")
    rows = table.find_all(lambda tag: tag.name == "tr")

    ## seznam web page koncnic iger
    for row in rows[1::]:
        a = row.find("a", href = True)
        url.append(a["href"])

# končnice, imena in letnice dodatkov iger
j = -1
for game in url[:100]:
    j = j + 1
    browser.get("https://boardgamegeek.com" + game + "/expansions")
    s = bs4.BeautifulSoup(browser.page_source, "html.parser")

    collection = s.find_all("div", class_ = "summary-item-title summary-item-title-separated")
    for i in collection:
        title = []
        title.extend(i.stripped_strings)
        games_exp.append(title[0])
        release_exp.append(int(re.search(r'\d+', title[1]).group()))
        basic.append([title[0], games[j]])

    ## seznam web page koncnic dodatkov
    for row in collection:
        a = row.find("a", href = True)
        url_exp.append(a["href"])

##################################################

j = -1
for game in url:
    j = j + 1
    ## web page trenutne igre, ki se ga ustvari na webdriverju
    browser.get("https://boardgamegeek.com" + game)
    s = bs4.BeautifulSoup(browser.page_source, "html.parser")
    primary = s.find_all("div", class_ = "gameplay-item-primary")

    # min & max stevilo igralcev, if zanka za primer ko imamo tocno doloceno stevilo igralcev
    minimum = primary[0].find('span', {'ng-if': 'min > 0'})
    if minimum != None:
        minplayers.append(int(minimum.text))
    else:
        minplayers.append(None)

    maksimum = primary[0].find('span', {'ng-if': 'max>0 && min != max'})
    if maksimum != None:
        maxplayers.append(int(re.search(r'\d+', maksimum.text).group()))
    elif minimum != None:
        maxplayers.append(int(minimum.text))
    else:
        maxplayers.append(None)

    # min & max dolzina igranja, if zanka za primer ko se igra tocno dolocen cas
    minimum = primary[1].find('span', {'ng-if': 'min > 0'})
    if minimum != None:
        mintime.append(int(minimum.text))
    else:
        mintime.append(None) # če ni podatka o trajanju igre

    maksimum = primary[1].find('span', {'ng-if': 'max>0 && min != max'})
    if maksimum != None:
        maxtime.append(int(re.search(r'\d+', maksimum.text).group()))
    elif maksimum != None:
        maxtime.append(int(minimum.text))
    else:
        maxtime.append(None) ## gloomheaven: solo scenario ma tle probleme - čeprau prej je delalo
    
    ## starost, if zanka za primer ko starost ni podana
    if re.search(r'\d+', primary[2].text) != None:
        age.append(int(re.search(r'\d+', primary[2].text).group()))
    else:
        age.append(None)

    primary = s.find_all(class_="feature-description")
    ## zvrst
    g = primary[1].find_all("a", href=re.compile("category"))
    for name in g:
        genre_game.append([games[j], name["title"]])
        genre.add(name["title"])

    primary = s.find_all(class_="credits")
    ## designerji
    des = primary[1].find_all("a", href=re.compile("designer"))
    for name in des:
        designer_game.append([games[j], name["title"]])
        designers.add(name["title"])

    ## artisti
    art = primary[1].find_all("a", href=re.compile("artist"))
    for name in art:
        artist_game.append([games[j], name["title"]])
        artists.add(name["title"])

    ## založba
    pub = primary[1].find_all("a", href=re.compile("publisher"))
    publisher_game.append([games[j], pub[0].text])
    publisher.add(pub[0].text)

#################################################

##  še dodatki
j = -1
for game in url_exp:
    j = j + 1
    ## web page trenutne igre, ki se ga ustvari na webdriverju
    browser.get("https://boardgamegeek.com" + game)
    s = bs4.BeautifulSoup(browser.page_source, "html.parser")
    primary = s.find_all("div", class_ = "gameplay-item-primary")

    # min & max stevilo igralcev, if zanka za primer ko imamo tocno doloceno stevilo igralcev
    minimum = primary[0].find('span', {'ng-if': 'min > 0'})
    if minimum != None:
        minplayers_exp.append(int(minimum.text))
    else:
        minplayers_exp.append(None)

    maksimum = primary[0].find('span', {'ng-if': 'max>0 && min != max'})
    if maksimum != None:
        maxplayers_exp.append(int(re.search(r'\d+', maksimum.text).group()))
    elif minimum != None:
        maxplayers_exp.append(int(minimum.text))
    else:
        maxplayers_exp.append(None)

    # min & max dolzina igranja, if zanka za primer ko se igra tocno dolocen cas
    minimum = primary[1].find('span', {'ng-if': 'min > 0'})
    if minimum != None:
        mintime_exp.append(int(minimum.text))
    else:
        mintime_exp.append(None) # če ni podatka o trajanju igre

    maksimum = primary[1].find('span', {'ng-if': 'max>0 && min != max'})
    if maksimum != None:
        maxtime_exp.append(int(re.search(r'\d+', maksimum.text).group()))
    elif maksimum != None:
        maxtime_exp.append(int(minimum.text))
    else:
        maxtime_exp.append(None) ## gloomheaven: solo scenario ma tle probleme - čeprau prej je delalo
    
    ## starost, if zanka za primer ko starost ni podana
    if re.search(r'\d+', primary[2].text) != None:
        age_exp.append(int(re.search(r'\d+', primary[2].text).group()))
    else:
        age_exp.append(None)

    primary = s.find_all(class_="feature-description")
    ## zvrst
    g = primary[1].find_all("a", href=re.compile("category"))
    for name in g:
        genre_game.append([games_exp[j], name["title"]])
        genre.add(name["title"])

    primary = s.find_all(class_="credits")
    ## designerji
    des = primary[1].find_all("a", href=re.compile("designer"))
    for name in des:
        designer_game.append([games_exp[j], name["title"]])
        designers.add(name["title"])

    ## artisti
    art = primary[1].find_all("a", href=re.compile("artist"))
    for name in art:
        artist_game.append([games_exp[j], name["title"]])
        artists.add(name["title"])

    ## založba
    pub = primary[1].find_all("a", href=re.compile("publisher"))
    publisher_game.append([games_exp[j], pub[0].text])
    publisher.add(pub[0].text)

## To show proper characters in excel you have to open new excel file and import data from games.csv using utf-8 encoding.
with open('pythonpodatki/igre.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Igra", "Min. st. igralcev", "Max. st. igralcev", "Min cas", "Max. cas", "Leto izdaje", "Min. starost", "Osnova/Dodatek"])
    for i in range(len(games)):
        wr.writerow([games[i], minplayers[i], maxplayers[i], mintime[i], maxtime[i], release[i], age[i], '']) 
    for i in range(len(games_exp)):
        wr.writerow([games_exp[i], minplayers_exp[i], maxplayers_exp[i], mintime_exp[i], maxtime_exp[i], release_exp[i], age_exp[i], basic[i][1]])

with open('pythonpodatki/igradodatek.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Dodatek", "Osnova"])
    for b in basic:
        wr.writerow([b[0], b[1]]) 

with open('pythonpodatki/avtor.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Avtor"])
    for artist in artists:
        wr.writerow([artist])

with open('pythonpodatki/oblikovalci.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Oblikovalec"])
    for designer in designers:
        wr.writerow([designer])

with open('pythonpodatki/zalozba.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Zalozba"])
    for pub in publisher:
        wr.writerow([pub])

with open('pythonpodatki/igraavtor.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Igra", "Avtor"])
    for i in artist_game:
        wr.writerow([i[0], i[1]])

with open('pythonpodatki/igraoblikovalec.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Igra", "Oblikovalec"])
    for i in designer_game:
        wr.writerow([i[0], i[1]])

with open('pythonpodatki/igrazalozba.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Igra", "Zalozba"])
    for i in publisher_game:
        wr.writerow([i[0], i[1]])

with open('pythonpodatki/zvrsti.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Zvrst"])
    for g in genre:
        wr.writerow([g])

with open('pythonpodatki/igrazvrst.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["Igra", "Zvrst"])
    for i in genre_game:
        wr.writerow([i[0], i[1]])
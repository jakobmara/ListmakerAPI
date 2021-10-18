from bs4 import BeautifulSoup
from requests import get
import requests

# parameters: takes search string 
# optional parameters: # of results to return (FOR NOW HARDCODED TO 3)
# output: array of objects 
#    each object contains: (URL for anime thumbnail, URL for anime, name of anime)
#
def getAnimeSearchSuggestions(queryString,numResults=6):
    url = formatURL(queryString,"anime")
    print(f"scraping: {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    
    content = soup.find("div","js-categories-seasonal js-block-list list")
    aniTable = content.find("table")
    aniEntries = aniTable.find_all("tr")[1:1+numResults] #first entry in table is just the headings

    #entries = articles.find_all("tr")
    suggestions = []
    for x in aniEntries:
        
        #uses x.url to get the description from MAL
        entryUrl = x.find("a","hoverinfo_trigger")['href']
        #entryDesc = getDesc(entryUrl)
        newEntry = {
            "title": x.find("strong").text ,
            "image": x.find("img")['data-src'],
            "url": entryUrl,
            "desc": ' '
        }


        suggestions.append(newEntry)

    for s in suggestions:
        print(s)    

    return suggestions

# parameters: takes search string to format
# optional parameter: specifies if its looking for anime or manga
# returns: query adequately formatted for URL
def formatURL(queryString,specify = "all"):
    newString = queryString.replace(" ","%20")
    newString += f"&cat={specify}"
    url = f'https://myanimelist.net/{specify}.php?q={newString}'
    return url

def getDesc(url):
    import re
    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser")
    desc = soup.find("p",{'itemprop':'description'}).text
    return desc


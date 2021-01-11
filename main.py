from config import *
import requests
from bs4 import BeautifulSoup as bs


def get_page(URL):
    response = requests.get(URL)
    if (response.status_code == 200):
        return response.content

    return ""


def get_prices(page):
    soup = bs(page, features="html.parser")
    sections = bs(str(soup.find_all("div", {'class': sort_class})[0]), features="html.parser").find_all("section")
    for e in sections:
        preis = float(str(e.find_all("span", {'class': "e-p1"})).split("<")[1].split(">")[1] \
                      + str(e.find_all("span", {'class': "e-p2"})).split("<")[1].split(">")[1])

        name = str(e.find_all("div", {'class': "e-content"})).split("<")[2].split(">")[1] \
               + " " \
               + str(e.find_all("div", {'class': "e-content"})).split("<")[5].split(">")[1]

        print(name)
        print(preis)


if __name__ == "__main__":
    get_prices(get_page(Super_URL))

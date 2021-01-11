from config import *
import requests
from bs4 import BeautifulSoup

def get_page(URL):
    response = requests.get(URL)
    if(response.status_code == 200):
        return response.content

    return ""

def get_prices(page):
    soup = BeautifulSoup(page)
    print(soup.find_all(sort_class))

if __name__ == "__main__":
    get_prices(get_page(URL))
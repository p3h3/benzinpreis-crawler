from config import *
from db_helper import DbHelper
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from time import sleep


def get_page(URL):
    response = requests.get(URL)
    if (response.status_code == 200):
        now = datetime.now()
        time = now.strftime("%d/%m/%Y %H:%M:%S")
        return response.content, time

    return ""


def get_prices(page, db_helper, time):
    soup = bs(page, features="html.parser")
    sections = bs(str(soup.find_all("div", {'class': sort_class})[0]), features="html.parser").find_all("section")

    for e in sections:
        preis = float(str(e.find_all("span", {'class': "e-p1"})).split("<")[1].split(">")[1] \
                      + str(e.find_all("span", {'class': "e-p2"})).split("<")[1].split(">")[1])

        address = str(e.find_all("div", {'class': "e-content"})).split("<")[5].split(">")[1]

        name = str(e.find_all("div", {'class': "e-content"})).split("<")[2].split(">")[1]

        dataframe = {
            "price": preis,
            "name": name,
            "address": address,
            "time": time
        }

        db_helper.insert_datapoint(dataframe, "supere5", db_name)

if __name__ == "__main__":
    # initialising database connection
    db_helper = DbHelper(db_user, db_password, db_hostname, db_name)

    try:
        while True:
            response, time = get_page(Super_URL)
            print("Inserting dataframe at " + time)
            get_prices(response, db_helper, time)

            sleep(25)
    except KeyboardInterrupt:
        db_helper.close_connection()
        print("Bye.")

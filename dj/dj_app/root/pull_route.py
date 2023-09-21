import requests
from bs4 import BeautifulSoup as bs4
from .root_class import Root_class
import xml.etree.ElementTree as ET
import pytz



def pull_route(self, flight_query):     # Still under construction. Difficult to work with API. Attempting AeroAPI
    # Much unfinished work here! Cant seem to get how to extract the clearance route from flightaware,

    flt_num = flight_query

    flight_aware = f"https://flightaware.com/live/flight/UAL{flt_num}"
    response = requests.get(flight_aware)
    try :
        soup = bs4(response.content, 'html.parser')
        # data_tag= soup.find_all('flightPageData')
        data_tag= soup.find_all("div", class_="flightpagedata")
    except :
        empty_soup = {} 
        return empty_soup
    # print(data_tag)
    print(soup.get_text())

    # Seperate trial with the API. 
    url = "https://aeroapi.flightaware.com/aeroapi"

    headers = {"Authorization": "qPRqXI2e1puzGQaGLaU387h33BImo8AA"}
    params = {"flight_number": "", 
            "date": ""}

    response = requests.get(url, headers=headers, params=params)
    print(response.url)
    print(response.status_code)
    if response.status_code==200:
        data = response.json()
        print(data)
    




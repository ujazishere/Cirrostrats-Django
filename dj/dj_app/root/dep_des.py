import pickle
import requests
from bs4 import BeautifulSoup as bs4

class Pull_dep_des:
    def __init__(self) -> None:
        pass
    
    def pull_flights(self):
        
        # add url
        response = requests.get('url')
        soup = bs4(response.content, 'html.parser')

        departure = soup('departure')
        arrival = soup('arrival')

        
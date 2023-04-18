import requests
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import pytz
import pickle

class Gate_root:
    def __init__(self,):
        eastern = pytz.timezone('US/eastern')
        now = datetime.now(eastern)
        self.latest_time = now.strftime("%#I:%M%p, %b %d.")
        self.latest_date_raw = now.strftime('%Y%m%d')
        self.latest_date_viewable = now.strftime('%b %d, %Y')

        # TODO: web splits time in 3 parts.
                # Makes it harder to pick appropriate information about flights
                # from different times of the date


    def date_time(self):
        # TODO: This one has not been used much yet.
                    # but need to be able to show on the web date and time the information was updated.
        return f'{self.latest_date_viewable}, {self.latest_time}'
    

    def request(self, url, timeout=None):
        if timeout:
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.get(url)
        return bs4(response.content, 'html.parser')


    def load_master(self):
        with open('master_UA.pkl', 'rb') as f:
            return pickle.load(f)


    def dt_conversion(self, data):
        # converts date and time string into a class object 
        return datetime.strptime(data, "%I:%M%p, %b%d")

import requests
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import pytz
import pickle

class Root_class():
    
    def __init__(self) -> None:
            pass


    def date_time(self, raw=None, viewable=None):
        eastern = pytz.timezone('US/eastern')
        now = datetime.now(eastern)
        latest_time = now.strftime("%#I:%M%p, %b %d.")
        if raw:
            return now.strftime('%Y%m%d')
        elif viewable:
            return now.strftime('%b %d, %Y')
        else:
            return latest_time
    

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
    

    def departures_ewr_UA(self):
        # returns list of all united flights as UA**** each
        # Here we extract raw united flight number departures from airport-ewr.com
        
        # morning = '?tp=6'         # When its late in night and you want to run lengthy scrape it wont work since
                                        # there are no flights. Use this morning to pull early morning flights instead
        morning = ''
        EWR_deps_url = f'https://www.airport-ewr.com/newark-departures{morning}'

        # TODO: web splits time in 3 parts.
                # Makes it harder to pick appropriate information about flights
                # from different times of the date

        
        soup = self.request(EWR_deps_url)
        raw_bs4_all_EWR_deps = soup.find_all('div', class_="flight-col flight-col__flight")[1:]
        # TODO: raw_bs4_html_ele contains delay info. Get delayed flight numbers
        # raw_bs4_html_ele = soup.find_all('div', class_="flight-row")[1:]

        #  This code pulls out all the flight numbers departing out of EWR
        all_EWR_deps = []
        for index in range(len(raw_bs4_all_EWR_deps)):
            for i in raw_bs4_all_EWR_deps[index]:
                if i != '\n':
                    all_EWR_deps.append(i.text)

        # extracting all united flights and putting them all in list to return it in the function.
        united_flights =[each for each in all_EWR_deps if 'UA' in each]
        print(f'total flights {len(all_EWR_deps)} of which UA flights: {len(united_flights)}')
        return united_flights

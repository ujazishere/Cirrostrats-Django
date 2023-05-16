import requests
from bs4 import BeautifulSoup as bs4
from .root_class import Root_class

class Pull_dep_des:
    def __init__(self) -> None:
        pass
    
    def pull_flights(self):
        
        # add url
        response = requests.get('url')
        soup = bs4(response.content, 'html.parser')


class Pull_dep_des(Root_class):
    def __init__(self) -> None:
        super().__init__()

    def pull(self, flight_query):
        flt_num = flight_query

        # date format in the url is YYYYMMDD. For testing, you can find flt_nums on https://www.airport-ewr.com/newark-departures
        use_custum_raw_date = False
        if use_custum_raw_date:
            date = 20230505
        else:
            date = self.latest_date_raw
        flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num}?date={date}&depapt=EWR"
        print(1)
        response = requests.get(flight_view)
        print(2, type(response))
        try :
            soup = bs4(response.content, 'html.parser')
            scripts = soup.find_all('script')       # scripts is a section in the html that contains departure and destination airports 
            for script in scripts:
                # looks up text 'var sdepapt' which is associated with departure airport.
                    # then splits all lines into list form then just splits the departure and destination in string form (")
                # TODO: It is important to get airport names along with identifiers to seperate international flights for metar view.
                if 'var sdepapt' in script.get_text():
                    departure = script.get_text().split('\n')[1].split('\"')[1]
                    destination = script.get_text().split('\n')[2].split('\"')[1]
            print(3)
            return dict({flt_num: [departure, destination]})
        except :
            empty_soup = {} 
            print(4)
            return empty_soup
        # typically 9th index of scripts is where departure and destination is.
            # try print(scripts[9].get_text()) for string version for parsing
        
        # print(departure, destination)


# url = Pull_dep_des().pull('492')
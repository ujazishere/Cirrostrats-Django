from concurrent.futures import ThreadPoolExecutor, as_completed
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
    
    
    def exec(self, input1, multithreader):
    # TODO: Extract this blueprint for future use.
    # executor blueprint. In this case input 1 takes in flight numbers and `multithreaders` can be item that needs to be multithreaded.
        # this will take in all the flight numbers at once and perform web scrape(`pick_flight_data()`) on all of them simultaneously
        # Multithreading
        completed = {}
        troubled = set()
            # VVI!!! The dictionary `futures` .value() is the flight number and  key is the the memory location of return from pick_flight_data()
            # Used in list comprehension for loop with multiple keys and values in the dictionary. for example:
            # {<Future at 0x7f08f203ec10 state=running>: 'UA123',
                # <Future at 0x7f08f203ed10 state=running>: 'DL789'
                        # }
        with ThreadPoolExecutor(max_workers=350) as executor:
            # First argument in submit method is the lengthy function that needs multi threading
                # second argument is each flt number that goes into that function. Together forming the futures.key()
                #note no parentheses in the first argument
            futures = {executor.submit(multithreader, flt_num): flt_num for flt_num in
                        input1}
            # futures .key() is the memory location of the task and the .value() is the flt_num associated with it
            for future in as_completed(futures):
                # again, future is the memory location of the task
                flt_num = futures[future]
                try:
                    result = future.result()        # result is the output of the task at that memory location 
                    completed.update(result)
                except Exception as e:
                    # print(f"Error scraping {flt_num}: {e}")
                    troubled.add(flt_num)
                
        # reading outlaws and dumping them
        with open('outlaws.pkl', 'rb') as f:
            outlaws = pickle.load(f)
        outlaws.update(self.outlaws_reliable)
        with open('outlaws.pkl', 'wb') as f:
            pickle.dump(outlaws, f)
            
        return dict({'completed':  completed, 'troubled': troubled})
        
        
    ''''def departures_ewr_UA(self):
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
        united_departures_newark =[each for each in all_EWR_deps if 'UA' in each]
        print(f'total flights {len(all_EWR_deps)} of which UA flights: {len(united_departures_newark)}')
        return united_departures_newark'''
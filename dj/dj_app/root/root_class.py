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
        if raw:         # format yyyymmdd
            return now.strftime('%Y%m%d')       # date format yyyymmdd
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
        
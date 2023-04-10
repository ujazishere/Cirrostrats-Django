import requests
from bs4 import BeautifulSoup as bs4
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pytz
import pickle
from time import sleep
import logging

logging.basicConfig(level=logging.INFO)

# TODO: VVI Seperate pick_flight_data and executor in a seperate class and inherit it here.
# TODO: Include description and documentation for others to read and make changes to it
# TODO: Include arrivals too
# TODO: need to be able to receive alerts:
        # for any ground stop or delays there might be at any particular airport in the National Airspace System

# Ideas:
# TODO: Have a way to store all queries made on web and analyse them later for optimization.
# TODO: the ability to chat and store queries. Essentially as an AI chatbot.
            # Include pertinent weather info based on flight number: Metar, TAF
                # Highlight weather minimums for alternate requirements;(1-2-3 rule per ETA)
                # Highlight Icing conditions in blue; LIFR in pink 
                # include gate in this packet
                # include IFR routing through flight aware. 

''' Check if departures_EWR_UA is used multiple times. It Only needs to run once unless a flight is added into the system'''
class Gate_checker:
    def __init__(self,):
        eastern = pytz.timezone('US/eastern')
        now = datetime.now(eastern)
        self.latest_time = now.strftime("%#I:%M%p, %b %d.")
        self.latest_date_raw = now.strftime('%Y%m%d')
        self.latest_date_viewable = now.strftime('%b %d, %Y')
        evening = '?tp=6'
        # evening = ''
        self.EWR_deps_url = f'https://www.airport-ewr.com/newark-departures{evening}'
        self.troubled = set()
        self.master_local = {}

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


    def departures_EWR_UA(self):
        # returns list of all united flights as UA**** each
        # Here we extract raw united flight number departures from airport-ewr.com
        
        soup = self.request(self.EWR_deps_url)
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


    def pick_flight_data(self, flt_num):
        # returns a dict with value of list that contains 3 items. Refer to return
        flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num[2:]}?date={self.latest_date_raw}&depapt=EWR"
        soup2 = self.request(flight_view, timeout=5)
        raw_bs4_scd2 = soup2.find_all('td')

        # Schedule and terminal information with a lot of other garbage:
        scd = []
        [scd.append(i.text.strip()) for i in raw_bs4_scd2 if i != '']

        scheduled = scd[2].replace('\xa0', '')
        actual = scd[3].replace('\xa0', '')
        terminal = scd[4]

        return {flt_num: [terminal, scheduled, actual]}


    def executor(self, united_flights):
        
        # takes in individual `united_flights` from departures_EWR_UA() and later `troubled`
        # gets fed into self.pick_flight_data using ThreadPool workers for multi threading.
       
        # TODO:There is a probelm with opening the master_UA.pkl file as is.
            # Troubled items will already be in this master from old data so they wont be checked and updated
            # one way to fix it is to check date and time and overwrite the old one with the latest one
        with open('master_UA.pkl', 'rb') as f:
            master = pickle.load(f)

        # note the code nested within the `with` statement. It terminates outside of the nest.
        # That is thesole purpose of `with statement`.
            # VVI!!! The dictionary `futures` .value() is the flight number and  key is the memory location of the thread
            # Used in list comprehension for lop with multiple keys and values in the dictionary. for example:
            # {
                # <Future at 0x7f08f203ec10 state=running>: 'UA123',
                # <Future at 0x7f08f203ec90 state=running>: 'AA456',
                # <Future at 0x7f08f203ed10 state=running>: 'DL789'
                        # }
        with ThreadPoolExecutor(max_workers=500) as executor:
            futures = {executor.submit(self.pick_flight_data, flt_num): flt_num for flt_num in
                        united_flights}
            
            # Still dont understand this `as_completed` sorcery, but it works. Thanks to ChatGPT
            for future in as_completed(futures):
                flt_num = futures[future]
                try:
                    result = future.result()
                    self.master_local.update(result)
                except Exception as e:
                    # print(f"Error scraping {flt_num}: {e}")
                    self.troubled.add(flt_num)
        
        # Created master_local for troubled items to be checked for and not be removed unncessarily like before.
        master.update(self.master_local)

        print('troubled:', len(self.troubled), self.troubled)

        # Dumping master dict into the root folder in order to be accessed by ewr_UA_gate func later on.
        with open('master_UA.pkl', 'wb') as f:
            pickle.dump(master, f)


    def tro(self):

        # TODO: Seperate for loop move it outside of the multiple_thread scope and give it it's own function troubled.
        # Reopening master to check troubled flights within it.
        
        # TODO:There is a probelm with opening the master_UA.pkl file as is.
            # Troubled items will already be in this master from old data so they wont be checked and updated
            # one way to fix it is to check date and time and overwrite the old one with the latest one
        with open('master_UA.pkl', 'rb') as f:
            master = pickle.load(f)
        
        # feeding self.troubled into the executor using for loop for a few times to restrict infinite troubles, if any. 
        # In a while loop a troubled item may not convert creating endless loop. Hence a for loop(max 5 attempts to minimize excessive waits)
        for i in range(3):
            if self.troubled:
                sleep(3)
                self.executor(self.troubled)
                
                #Following code essentially removes troubled items that are already in the master.
                # logic: if troubled items are not in master make a new troubled set with those. Essentially doing the job of removing master keys from troubled set
                self.troubled = {each for each in self.troubled if each not in self.master_local}
                
                # Here we check how many times we've looped so far and how many troubled items are still remaining.
                print(f'{i}th trial- troubled len:', len(self.troubled) )
            elif not self.troubled:
                # breaking since troubled is probably empty
                break


        # for flight_num, (gates, scheduled, actual) in master.items():
            # print(flight_num, gates, scheduled, actual)
        
        print(f'Troubled: {len(self.troubled)}, Master : {len(master)}', self.date_time())


    def temp_fix_to_remove_old_flights(self):
        with open('master_UA.pkl', 'rb') as f:
            master = pickle.load(f)

        to_remove = []

        for flight_num, (gate, scheduled, actual) in master.items():
            scheduled = datetime.strptime(scheduled, "%I:%M%p, %b%d") if scheduled else None
            if scheduled and scheduled.date() < datetime.now().date():
                to_remove.append(flight_num)
            else:
                pass
        
        for i in to_remove:
            del master[i]

        with open('master_UA.pkl', 'wb') as f:
            pickle.dump(master, f)


    def activator(self):
        # This funciton gets all the departure flight numbers through self.departures_EWR_UA()
            # feeds it into the executor for multithreading to extract gate and time for individual flight.
            # executor then extracts successfully done ones in master_UA.pkl
                # others get addded to self.troubled
            # We then loop through self.troubled feeding it back into the executor to repeat process.
        
        # remove old flights from master from before today
        # self.temp_fix_to_remove_old_flights()

        # Extract all United flight numbers in list form
        departures_EWR_UA = self.departures_EWR_UA()
        
        # dump master_UA.pkl with flight, gate and time info using ThreadPoolExecutor
        self.executor(departures_EWR_UA)

        # Redo the troubled flights
        if self.troubled:
            self.tro()
        

    def load_master(self):
        with open('master_UA.pkl', 'rb') as f:
            return pickle.load(f)


    def dt_conversion(self, data):
        # converts date and time string into a class object 
        return datetime.strptime(data, "%I:%M%p, %b%d")

    
    def structured_flights(self):
        master = self.load_master()
        structured_flights = []
        outlaws = []
        for flight_num, (gate, scheduled, actual) in master.items():
            if "Terminal" in gate and scheduled and actual and scheduled != 'Not Available' and actual != 'Not Available':
                
                scheduled = self.dt_conversion(scheduled)
                actual = self.dt_conversion(actual)
                
                structured_flights.append({
                    'gate': gate,
                    'flight_number': flight_num,
                    'scheduled': scheduled,
                    'actual': actual,
                })
            else:
                # TODO: Have to deal with these outlaws and feed it back into the system
                print("FALSE","gate =", gate,"flt=", flight_num,"sch=", scheduled, 'ach=', actual)
                outlaws.append({
                    'gate': gate,
                    'flight_number': flight_num,
                    'scheduled': scheduled,
                    'actual': actual,
                })
        logging.info(outlaws)
        for i in outlaws:
            print(f'OUTLAWS {outlaws}')
        
        return structured_flights
                

    # TODO: Big bug when extracting info from other sources. the data can be messy.
        # filter only reliable data and use logs to extract and track unreliable data.
    def ewr_UA_gate(self, query):
        master = self.load_master()
        print(f'master length: {len(master)}')
        
        flights = []
        outlaws = []
        for flight_num, (gate, scheduled, actual) in master.items():
            if "Terminal" in gate and scheduled and actual and scheduled != 'Not Available' and actual != 'Not Available':
                if f'{query}' in gate:
                    
                    scheduled = self.dt_conversion(scheduled)
                    actual = self.dt_conversion(actual)

                    # scheduled = datetime.strptime(scheduled, "%I:%M%p, %b%d") if scheduled else None
                    # actual = datetime.strptime(actual, "%I:%M%p, %b%d") if actual else None

                    flights.append({
                        'gate': gate,
                        'flight_number': flight_num,
                        'scheduled': scheduled,
                        'actual': actual,
                    })
            else:
                # TODO: Have to deal with these outlaws and feed it back into the system
                print("FALSE","gate =", gate,"flt=", flight_num,"sch=", scheduled, 'ach=', actual)
                outlaws.append({
                    'gate': gate,
                    'flight_number': flight_num,
                    'scheduled': scheduled,
                    'actual': actual,
                })

        # Sorts the data by 'scheduled' in descending order to get the latest date and time to the top
        flights = sorted(flights, key=lambda x:x['scheduled'], reverse=True)

        # Converting it back to string for it to show in a viewable format otherwise
            # browser craps out when it sees class object since earlier 'scheduled' item is a class object and not a string
        for dictionries in flights:
            dictionries['scheduled'] = dictionries['scheduled'].strftime("%#I:%M%p, %b%d")
            dictionries['actual'] = dictionries['actual'].strftime("%#I:%M%p, %b%d")
        
        return flights


# flights = Gate_checker('').ewr_UA_gate()
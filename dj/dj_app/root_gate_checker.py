from bs4 import BeautifulSoup as bs4
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
import pickle
from time import sleep
import logging
from .root.root_class import Gate_root
import re

logging.basicConfig(filename='debug.log', level=logging.INFO)

# TODO: Focus on readibility and simplicity. Use inheritance and models for database management.

# TODO: Include description and documentation for others to read and make changes to it
# TODO: Include: search  by flight number, for Metar, TAF
# TODO: need to be able to receive alerts if the weather deteriorates:
        # Account for any ground stop or delays there might be at any particular airport in the National Airspace System

# Ideas:
# TODO: Have a way to store all queries made on web and analyse them later for optimization. 
           # record and analyze innteractions on the web to imporve efficiency
# TODO: the ability to chat and store queries. Essentially as an AI chatbot.
            # Include pertinent weather info based on flight number: Metar, TAF
                # Highlight weather minimums for alternate requirements;(1-2-3 rule per ETA)
                # Highlight Icing conditions in blue; LIFR in pink 
                # include gate in this packet
                # include IFR routing through flight aware. 

# this class subclassess Gate_root that creates instances variables of the subclass and inherits its methods
class Gate_checker(Gate_root):
    
    def __init__(self,):

        # super method inherits all of the instance variables of the Gate_root class.
        super().__init__()
        
        # troubled is setup here so that it can be accessed locally
        self.troubled = set()
        self.master_local = []


    def departures_ewr_UA(self):
        # returns list of all united flights as UA**** each
        # Here we extract raw united flight number departures from airport-ewr.com
        
        morning = '?tp=6'
        # morning = ''
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


    def pick_flight_data(self, flt_num):
        
        # refer to self.executor() first, then come back here since this function is called by the exector
        # returns a dict with value of list that contains 3 items. Refer to the `return` item
        
        flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num[2:]}?date={self.latest_date_raw}&depapt=EWR"
        soup2 = self.request(flight_view, timeout=5)
        raw_bs4_scd2 = soup2.find_all('td')

        # Schedule and terminal information with a lot of other garbage:
        scd = []
        [scd.append(i.text.strip()) for i in raw_bs4_scd2 if i != '']

        scheduled = scd[2].replace('\xa0', '')
        actual = scd[3].replace('\xa0', '')
        gate = scd[4]
        
        return {flt_num: [gate, scheduled, actual]}
        # This is a format that resembles more to the format in the final output.
        # return {'flight_num': flt_num, 'gate': gate, 'scheduled': scheduled, 'actual': actual}
        
    # TODO: Extract this blueprint for future use.
    # executor blueprint. In this case input 1 takes in flight numbers and `multithreaders` can be item that needs to be multithreaded.
        # this will take in all the flight numbers at once and perform web scrape(`pick_flight_data()`) on all of them simultaneously
    def exec(self, input1, multithreader):
        
        completed = {}
        troubled = set()
        exec_output = dict({'completed':  completed, 'troubled': troubled})
            # VVI!!! The dictionary `futures` .value() is the flight number and  key is the the memory location of return from pick_flight_data()
            # Used in list comprehension for loop with multiple keys and values in the dictionary. for example:
            # {
                # <Future at 0x7f08f203ec10 state=running>: 'UA123',
                # <Future at 0x7f08f203ec90 state=running>: 'AA456',
                # <Future at 0x7f08f203ed10 state=running>: 'DL789'
                        # }
        with ThreadPoolExecutor(max_workers=500) as executor:
            futures = {executor.submit(multithreader, flt_num): flt_num for flt_num in
                        input1}
            
            # Still dont understand this `as_completed` sorcery, but it works. Thanks to ChatGPT
            for future in as_completed(futures):
                flt_num = futures[future]
                try:
                    result = future.result()
                    completed.update(result)
                except Exception as e:
                    # print(f"Error scraping {flt_num}: {e}")
                    troubled.add(flt_num)
        
        return exec_output


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
                self.exec(self.troubled, self.pick_flight_data())
                
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
        
        print(self.date_time(), f'Troubled: {len(self.troubled)}, Master : {len(master)}')


    def temp_fix_to_remove_old_flights(self):
        
        # might want to remove this method. It is destructive. Or just get rid of flights from 2 days ago rather than just 1 day since midnight is too close to previous day.
        
        master = self.load_master()
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
        
        # This is where the structure needs to be fixed before it enters master.pkl. This is the source of information
        
        # remove old flights from master from before today
        # self.temp_fix_to_remove_old_flights()

        # Extract all United flight numbers in list form through departures_ewr_UA()
        departures_ewr_UA = self.departures_ewr_UA()
        ex = self.exec(departures_ewr_UA, self.pick_flight_data)
        
        # Cant decide if master should be called or kept empty. When kept empty it saves disk space. When called it keeps track of old information.
        # master = self.load_master()
        master = {}
        master.update(ex['completed'])
        self.troubled.update(ex['troubled'])
        
       
        # TODO:There is a probelm with opening the master_UA.pkl file as is.
            # Troubled items will already be in this master from old data so they wont be checked and updated
            # one way to fix it is to check date and time and overwrite the old one with the latest one
        # Created master_local for troubled items to be checked for and not be removed unncessarily like before.

        print('troubled:', len(self.troubled), self.troubled)

        # Dumping master dict into the root folder in order to be accessed by ewr_UA_gate func later on.
        with open('master_UA.pkl', 'wb') as f:
            pickle.dump(master, f) 

        # Redo the troubled flights
        if self.troubled:
            self.tro()
        

    def structured_flights(self):
        master = self.load_master()
        structured_flights = []
        reliable_outlaws = []
        unreliable_outlaws = []
        # issue: too many values to unpack. Solution: unpack keys and values, use regex to make sure flight number matches.
        for flight_num, values in master.items():
            
            # Regex that matches 2 uppercase alphabets followed by digits between 4 and 4.
            reliable_flt_num = re.match(r'[A-Z]{2}\d{2,4}', flight_num)

            # if flight number is reliable and the associated values is exactly 3(i.e gate, schd, act) then:
            if reliable_flt_num and len(values) == 3:
                
                # its important that these values are nested in here since if the flight number is reliable these 3 values will exist.
                gate = values[0]
                scheduled = values[1]
                actual = values[2]
                
                if "Terminal" in gate and self.dt_conversion(scheduled) and self.dt_conversion(actual):
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
                    reliable_outlaws.append({
                        'flight_number': flight_num,
                        'gate': gate,
                        'scheduled': scheduled,
                        'actual': actual,
                    })
            else:
                unreliable_outlaws.append(dict({"flight_number": flight_num, "values": values}))
                    
        outlaws = dict({
            self.date_time() : []
        })
        
        # Better if the file is read, extracted and appended to extracted as a new file.
        with open('outlaws.pkl', 'wb') as f:
            pickle.dump(outlaws, f)
        return structured_flights
                

    def ewr_UA_gate(self, query=None):
    # TODO: Big bug when extracting info from other sources. the data can be messy.
        # filter only reliable data and use logs to extract and track unreliable data.
        # This is an atttempt to structure the data such that its not  prone to as many errors
        structured_flights = self.structured_flights()    
        # Stacking query items together
        flights = []
        for i in structured_flights:
            if f'{query}' in i['gate']:
                flights.append({
                    'gate': i['gate'],
                    'flight_number': i['flight_number'],
                    'scheduled': i['scheduled'],
                    'actual': i['actual'],
                })

        # Sorts the date by 'scheduled' in descending order to get the latest date and time to the top
        flights = sorted(flights, key=lambda x:x['scheduled'], reverse=True)

        # Converting it back to string for it to show in a viewable format otherwise
            # browser craps out when it sees class object for date since earlier 'scheduled' item is a class object and not a string
        for dictionries in flights:
            dictionries['scheduled'] = dictionries['scheduled'].strftime("%#I:%M%p, %b%d")
            dictionries['actual'] = dictionries['actual'].strftime("%#I:%M%p, %b%d")
        
        return flights


class GateCheckerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.gc = Gate_checker()

    
    # run method is the inherited. It gets called as
    def run(self):
        self.gc.activator()
    
# flights = Gate_checker('').ewr_UA_gate()
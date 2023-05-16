from concurrent.futures import ThreadPoolExecutor, as_completed
from .root_class import Root_class
import time
from datetime import datetime
import pickle

class Gate_Scrape(Root_class):
    def __init__(self) -> None:
        pass
        super().__init__()

        # troubled is setup here so that it can be accessed locally
        self.troubled = set()
        self.master_local = []
    
    def pick_flight_data(self, flt_num):
        
        # refer to self.exec() first, then come back here since this function is called by the exector
        # returns a dict with value of list that contains 3 items. Refer to the `return` item
        airline_code = flt_num[:2]      # first 2 characters of airline code eg. UA, DL
        flight_number_without_airline_code = flt_num[2:]
        raw_date = self.latest_date_raw
        
        flight_view = f"https://www.flightview.com/flight-tracker/{airline_code}/{flight_number_without_airline_code}?date={raw_date}&depapt=EWR"
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


    def exec(self, input1, multithreader):
    # TODO: Extract this blueprint for future use.
    # executor blueprint. In this case input 1 takes in flight numbers and `multithreaders` can be item that needs to be multithreaded.
        # this will take in all the flight numbers at once and perform web scrape(`pick_flight_data()`) on all of them simultaneously
        # Multithreading
        completed = {}
        troubled = set()
        exec_output = dict({'completed':  completed, 'troubled': troubled})
            # VVI!!! The dictionary `futures` .value() is the flight number and  key is the the memory location of return from pick_flight_data()
            # Used in list comprehension for loop with multiple keys and values in the dictionary. for example:
            # {ujas vaghani
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

        # Reopening master to check troubled flights within it.
        
        # TODO:There is a probelm with opening the master_UA.pkl file as is.
            # Troubled items will already be in this master from old data so they wont be checked and updated
            # one way to fix it is to check date and time and overwrite the old one with the latest one
        master = self.load_master()
        
        # feeding self.troubled into the executor using for loop for a few times to restrict infinite troubles, if any. 
        # In a while loop a troubled item may not convert creating endless loop. Hence a for loop(max 5 attempts to minimize excessive waits)
        for i in range(3):
            if self.troubled:
                time.sleep(3)
                ex = self.exec(self.troubled, self.pick_flight_data)
                master.update(ex['completed'])
                self.troubled = set(ex['troubled'])     # emptying out troubled and refilling it with new troubled items

                #Following code essentially removes troubled items that are already in the master.
                # logic: if troubled items are not in master make a new troubled set with those. Essentially doing the job of removing master keys from troubled set
                self.troubled = {each for each in self.troubled if each not in self.master_local}
                
                # Here we check how many times we've looped so far and how many troubled items are still remaining.
                print(f'{i}th trial- troubled len:', len(self.troubled) )
            elif not self.troubled:
                # breaking since troubled is probably empty
                break
        
        with open('master_UA.pkl', 'wb') as f:
            pickle.dump(master, f) 
        
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
        
        # TODO:This is where the structure needs to be fixed before it enters master.pkl. This is the source of information
        
        # remove old flights from master from before today
        # self.temp_fix_to_remove_old_flights()

        # Extract all United flight numbers in list form through departures_ewr_UA()
        departures_ewr_UA = self.departures_ewr_UA()
        
        # with open('departures_ewr_UA.pkl', 'rb') as f:
            # pickle.dump(departures_ewr_UA, f)
        
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
        
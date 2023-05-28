import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .root_class import Root_class
import time
from datetime import datetime
import pickle
import pytz
# from models import Flight       # This doesnt work because models is in the upper directory


# TODO: web splits time in 3 parts.
        # Makes it harder to pick appropriate information about flights
        # from different times of the date
        # only solution is to work with models and API/XML

                
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
        
        eastern = pytz.timezone('US/eastern')
        now = datetime.now(eastern)
        raw_date = now.strftime('%Y%m%d')           # formaatted as YYYYMMDD
        
        flight_view = f"https://www.flightview.com/flight-tracker/{airline_code}/{flight_number_without_airline_code}?date={raw_date}&depapt=EWR"
        soup2 = self.request(flight_view, timeout=5)
        raw_bs4_scd2 = soup2.find_all('td')

        # Schedule and terminal information with a lot of other garbage:
        scd = []
        [scd.append(i.text.strip()) for i in raw_bs4_scd2 if i != '']

        scheduled = scd[2].replace('\xa0', '')
        actual = scd[3].replace('\xa0', '')
        
        gate = scd[4]
        
        # Flight.objects.
        
        # return {flt_num: [gate, scheduled, actual]}

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
        completed_flights = ex['completed']
        troubled_flights = ex['troubled']
        # Cant decide if master should be called or kept empty. When kept empty it saves disk space. When called it keeps track of old information.
        # master = self.load_master()
        master = {}
        master.update(completed_flights)
        self.troubled.update(troubled_flights)
        
       
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
        
class Gate_scrape_thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.gc = Gate_Scrape()

    
    # run method is the inherited. It gets called as
    def run(self):
        
        # self.gc.activator()
        while True:
            self.gc.activator()
            
            eastern = pytz.timezone('US/eastern')           # Time stamp is local to this Loop. Avoid moving it around
            now = datetime.now(eastern)
            latest_time = now.strftime("%#I:%M%p, %b %d.")
            print('Pulled Gate Scrape at:', latest_time)
            
            time.sleep(600)        # TODO: Requires stops between 11:55pm and 4am while also pulling flights from morning once.
# flights = Gate_checker('').ewr_UA_gate()
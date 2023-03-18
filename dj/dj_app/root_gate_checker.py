import requests
from bs4 import BeautifulSoup as bs4
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pytz
import pickle

# TODO: need to be able to receive alerts for any ground stop or delays there might be at any particular airport in the National Airspace System
# TODO: Include description and documentation for others to read and make changed to it

''' get_UA_flight_nums is used multiple times which might not be necessary'''
class Gate_checker:
    def __init__(self, gate=None):
        self.gate = gate
        eastern = pytz.timezone('US/eastern')
        now = datetime.now(eastern)
        self.latest_time = now.strftime('%H:%M:%S')
        self.latest_date_raw = now.strftime('%Y%m%d')
        self.latest_date_viewable = now.strftime('%b %d, %Y')
        self.EWR_deps_url = 'https://www.airport-ewr.com/newark-departures'
        # TODO: web splits time in 3 or so parts which makes it harder to pick appropriate information about flights
        #  from different times of the date

    def get_UA_flight_nums(self):
        response = requests.get(self.EWR_deps_url)
        soup = bs4(response.content, 'html.parser')
        raw_bs4_flight_nums = soup.find_all('div', class_="flight-col flight-col__flight")[1:]
        # TODO: raw_bs4_html_ele contains delay info. Get delayed flight numbers
        # raw_bs4_html_ele = soup.find_all('div', class_="flight-row")[1:]
        flight_nums = []
        for index in range(len(raw_bs4_flight_nums)):
            for i in raw_bs4_flight_nums[index]:
                if i != '\n':
                    flight_nums.append(i.text)

        united_flights = []
        [united_flights.append(i) for i in flight_nums if 'UA' in i]
        print(f'total flights {len(flight_nums)} of which UA flights: {len(united_flights)}')
        return united_flights

    def pick_flight_data(self, flt_num):
        flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num[2:]}?date={self.latest_date_raw}&depapt=EWR"
        response2 = requests.get(flight_view, timeout=5)
        soup2 = bs4(response2.content, 'html.parser')
        raw_bs4_scd2 = soup2.find_all('td')

        # Schedule and terminal information with a lot of other garbage too:
        scd = []
        [scd.append(i.text.strip()) for i in raw_bs4_scd2 if i != '']

        scheduled = scd[2].replace('\xa0', '')
        actual = scd[3].replace('\xa0', '')
        terminal = scd[4]

        return {flt_num: [terminal, scheduled, actual]}

    def multiple_thread(self):
        # TODO: add argument to add both UA flights and troubled in there to scrape then remove ones that are done from the troubled
        
        united_flts = self.get_UA_flight_nums()
        master = {}
        troubled = set()
        
        def executor(flights):
            with ThreadPoolExecutor(max_workers=500) as executor:
                futures = {executor.submit(self.pick_flight_data, flt_num): flt_num for flt_num in
                            flights}
                for future in as_completed(futures):
                    flt_num = futures[future]
                    try:
                        result = future.result()
                        master.update(result)
                    except Exception as e:
                        # print(f"Error scraping {flt_num}: {e}")
                        troubled.add(flt_num)
            print('troubled:', len(troubled))
        
        executor(united_flts)
        # re-feeding troubled flights back into the executor
        for i in range(5):
            if troubled:
                executor(troubled)
                
                # if master keys are not in troubled set then making a new master dictionary. Essentially doing the job of removing troubled items from master
                # master = {k:v for k,v in master.items() if not k in troubled}
                
                # if troubled items are not in master making a new troubled set. Essentially doing the job of removing master keys from troubled set
                troubled = {x for x in troubled if x not in master}
                print(f'{i}th- troubled len:', len(troubled) )
            else:
                print('breaking since troubled is probably empty')
                break

        print(f'Troubled: {len(troubled)}, Master : {len(master)}')
        for flight_num, (gates, scheduled, actual) in master.items():
            print(flight_num, gates, scheduled, actual)
        
        # Dumping master dict into the root folder in order to be accessed by ewr_UA_gate func later on.
        # This is done becasue I couldn't find a way to access it outside of the class.
        with open('master_UA.pkl', 'wb') as f:
            pickle.dump(master, f)

    def ewr_UA_gate(self):
        with open('master_UA.pkl', 'rb') as f:
            master = pickle.load(f)
        curated = []
        for flight_num, (gate, scheduled, actual) in master.items():
            if f'{self.gate}' in gate:
                curated.append({
                    'gate': gate,
                    'flight_number': flight_num,
                    'scheduled': scheduled,
                    'actual': actual,
                })
        return curated
            
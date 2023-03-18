import requests
from bs4 import BeautifulSoup as bs4
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pytz
import pickle


# gate = 'C101'


class Gate_checker:
    def __init__(self, gate=None):
        self.gate = gate
        eastern = pytz.timezone('US/eastern')
        now = datetime.now(eastern)
        self.latest_time = now.strftime('%H:%M:%S')
        self.latest_date_raw = now.strftime('%Y%m%d')
        self.latest_date_viewable = now.strftime('%b %d, %Y')
        self.EWR_deps_url = 'https://www.airport-ewr.com/newark-departures?tp=6'
        # TODO: web splits time in 3 or so parts which makes it harder to pick appropriate information about flights
        #  from different times of the dat
        self.master = {}
        self.troubled = set()

    def get_UA_flight_nums(self):
        response = requests.get(self.EWR_deps_url)
        soup = bs4(response.content, 'html.parser')
        raw_bs4_flight_nums = soup.find_all('div', class_="flight-col flight-col__flight")[1:]
        # TODO: raw_bs4_html_ele contains delay info. Get delayed flight numbers
        # raw_bs4_html_ele = soup.find_all('div', class_="flight-row")[1:]
        print(f'raw items found: {len(raw_bs4_flight_nums)}')
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
        # TODO: add argument to add both UA flights and troubled in there to scrap then remove ones that are done
        #  from the troubled
        if len(self.get_UA_flight_nums()) > 10:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(self.pick_flight_data, flt_num): flt_num for flt_num in
                           self.get_UA_flight_nums()}
                for future in as_completed(futures):
                    flt_num = futures[future]
                    try:
                        result = future.result()
                        self.master.update(result)
                    except Exception as e:
                        print(f"Error scraping {flt_num}: {e}")
                        self.troubled.add(flt_num)
            print(f'Troubled: {len(self.troubled)}, Master : {len(self.master)}')
            for a, b in self.master.items():
                print(a, b[0])
        else:
            for i in self.get_UA_flight_nums():
                self.pick_flight_data(i)
        with open('masater_UA.pkl', 'wb') as f:
            pickle.dump(self.master, f)

    def ewr_UA_gate(self):
        with open('master_UA.pkl', 'rb') as f:
            master = pickle.load(f)
        curated = {}
        print(type(self.gate))
        for a, b in master.items():
            if f'{self.gate}' in b[0]:
                curated.update(dict({a: b}))
        if curated:
            print(curated)
        else:
            print('Nothing to show. Come back later.')


Gate_checker().get_UA_flight_nums()
Gate_checker().multiple_thread()

while True:
    gate = input('What gate?')
    if gate:
        Gate_checker(gate).ewr_UA_gate()
    else:
        break

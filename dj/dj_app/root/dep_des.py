import requests
from bs4 import BeautifulSoup as bs4
from .root_class import Root_class
import xml.etree.ElementTree as ET
import pytz

'''
This Script pulls the departur and destination when provided with the flight number.
An attempt to extract clearance route has been initiated but unreliable.
    Beter to work with API or XML see TODO UV** 
'''

class Pull_flight_info(Root_class):
    def __init__(self) -> None:
        # Super method inherits the init method of the superclass. In this case`Root_class`.
        super().__init__()

    def pull_UA(self, query_in_list_form):
        query = ' '.join(query_in_list_form)
        
        flt_num = query.split()[1]
        # airport = query.split()[2]

        #  TODO: pull information on flight numners from the info web and use that to pll info through flightview.
        # attempt to only pull departure and destination from the united from the info web.
        info = f"https://united-airlines.flight-status.info/ua-{flt_num}"               # This web probably contains incorrect information.
        flight_view = "https://www.flightview.com/flight-tracker/UA/492?date=20230702&depapt=EWR"
        flight_stats_url = f"https://www.flightstats.com/v2/flight-details/UA/{flt_num}?year=2023&month=7&date=2"
        soup = self.request(info)

        # Airport distance and duration can be misleading. Be careful with using these. 
        # table = soup.find('div', {'class': 'a2'})
        distane_and_duration = soup.find('ul', {'class': 'a3_n'})
        distance_duration = [i.text for i in distane_and_duration if 'Flight D' in i.text]
        airport_id = soup.find_all('div', {'class': 'a2_ak'})
        airport_id = [i.text for i in airport_id if 'ICAO' in i.text]
        departure_ID = airport_id[0].split()[2]
        destination_ID = airport_id[1].split()[2]

        times = soup.find_all('div', {'class': 'a2_b'})          # scheduled and actual times in local time zone
        times = [i.text for i in times if 'Scheduled' in i.text]
        departure_times = ' '.join(times[0].replace('\n','').split())
        scheduled_departure_time = departure_times[:9] + ' ' + departure_times[9:27]
        actual_departure_time = departure_times[28:34] + ' ' + departure_times[34:]
        destination_times = ' '.join(times[1].replace('\n','').split())
        scheduled_arrival_time = destination_times[:9] + ' ' + destination_times[9:27]
        actual_arrival_time = destination_times[28:34] + ' ' + destination_times[34:]

        gate = soup.find_all('div', {'class': 'a2_c'})              # the data from the gate is also probably misleading.
        gate = [i.text.replace('\n', '') for i in gate]
        departure_gate = gate[0]
        destination_gate = gate[1]

        # time = soup.find('div', {'class': 'a2_b'})

        nas_delays = self.nas_status()
        dep_delay = None
        destination_delay = None
        for each_airport in nas_delays['affected_airports']:
            if departure_ID == each_airport:
                for k, v in nas_delays.items():
                    pass
                    

        return {'flight_number': f'UA{flt_num}',            # This flt_num is probably misleading since the UA attached manually. Try pulling it from the flightstats web
                 'departure_ID': departure_ID,
                 'destination_ID':destination_ID, 
                 'departure_gate': departure_gate,
                 'scheduled_departure_time': scheduled_departure_time,
                 'actual_departure_time': actual_departure_time,
                 'destination_gate': destination_gate,
                 'scheduled_arrival_time': scheduled_arrival_time,
                 'actual_arrival_time': actual_arrival_time,
                 }

    def nas_status(self):
        '''
        import pickle
        with open('et_root_eg_1.pkl', 'wb') as f:
            pickle.dump(root, f)
        '''
        
        '''
        import requests
        from bs4 import BeautifulSoup as bs4
        from .root_class import Root_class
        import xml.etree.ElementTree as ET
        import pytz
        '''

        nas = "https://nasstatus.faa.gov/api/airport-status-information"
        response = requests.get(nas)
        xml_data = response.content

        root = ET.fromstring(xml_data)

        update_time = root[0].text

        affected_airports = [i.text for i in root.iter('ARPT')]
        affected_airports.sort()

        ground_stop_packet = []
        count = 0
        for programs in root.iter('Program'):
            count += 1
            for each_program in programs:
                ground_stop_packet.append([count, each_program.tag, each_program.text])
        
        ground_delay_packet = []
        gd = root.iter('Ground_Delay')
        for i in gd:
            for y in i:
                ground_delay_packet.append([y.tag, y.text])

        arr_dep_del_list = []
        addl = root.iter('Arrival_Departure_Delay_List')
        for i in addl:
            for y in i:
                for x in y:
                    if x.tag == 'Arrival_Departure':
                        arr_dep_del_list.append([x.tag, x.attrib])
                    else:
                        arr_dep_del_list.append([x.tag, x.text])
                    for a in x:
                        arr_dep_del_list.append([a.tag, a.text])

        """
        all_intel = {}
        count = 0
        name= []
        for individual_delay_type in root.iter('Delay_type'):
            name.append(individual_delay_type.find('Name'))
            name_local = individual_delay_type.find('Name')
            for list_type in individual_delay_type:
                for ty in list_type:
                    for i in ty:
                        count += 1
                        all_intel.update(dict({count:[name_local.text, individual_delay_type.tag, individual_delay_type.text,
                    list_type.tag, i.tag, i.text]}))
        """
        return {'update_time': update_time,
                'affected_airports': affected_airports,
                'gsp': ground_stop_packet, 
                'gdp': ground_delay_packet,
                'addl': arr_dep_del_list,
                }

    def pull_dep_des(self, query_in_list_form):             # not used yet. Plan on using it such that only reliable and useful information is pulled.

        query = ' '.join(query_in_list_form)

        flt_num = query.split()[1]
        airport = query.split()[2]
        print(flt_num, airport)

        # date format in the url is YYYYMMDD. For testing, you can find flt_nums on https://www.airport-ewr.com/newark-departures
        use_custum_raw_date = False
        if use_custum_raw_date:
            date = 20230505
        else:
            date = self.date_time(raw=True)     # Root_class inheritance
        flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num}?date={date}&depapt={airport}"

        try :
            soup = self.request(flight_view)
            scripts = soup.find_all('script')       # scripts is a section in the html that contains departure and destination airports 
            for script in scripts:
                # looks up text 'var sdepapt' which is associated with departure airport.
                    # then splits all lines into list form then just splits the departure and destination in string form (")
                # TODO: It is important to get airport names along with identifiers to seperate international flights for metar view.
                if 'var sdepapt' in script.get_text():
                    departure = script.get_text().split('\n')[1].split('\"')[1]
                    destination = script.get_text().split('\n')[2].split('\"')[1]
            # print(scripts[-3].get_text())       #this is where you can find departure and destination times
                    # departure_time = 
            return dict({flt_num: [departure, destination]})
        except :
            empty_soup = {} 
            return empty_soup

        # typically 9th index of scripts is where departure and destination is.
            # try print(scripts[9].get_text()) for string version for parsing
        
        # print(departure, destination)

    def pull_route(self, flight_query):     # Still under construction. Difficult to work with API. Attempting AeroAPI
        # Much unfinished work here! Cant seem to get how to extract the clearance route from flightaware,

        flt_num = flight_query

        flight_aware = f"https://flightaware.com/live/flight/UAL{flt_num}"
        response = requests.get(flight_aware)
        try :
            soup = bs4(response.content, 'html.parser')
            # data_tag= soup.find_all('flightPageData')
            data_tag= soup.find_all("div", class_="flightpagedata")
        except :
            empty_soup = {} 
            return empty_soup
        # print(data_tag)
        print(soup.get_text())

        # Seperate trial with the API. 
        url = "https://aeroapi.flightaware.com/aeroapi"

        headers = {"Authorization": "qPRqXI2e1puzGQaGLaU387h33BImo8AA"}
        params = {"flight_number": "", 
                "date": ""}

        response = requests.get(url, headers=headers, params=params)
        print(response.url)
        print(response.status_code)
        if response.status_code==200:
            data = response.json()
            print(data)
        




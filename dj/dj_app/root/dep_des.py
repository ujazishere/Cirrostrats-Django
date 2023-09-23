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
        date = self.date_time(raw=True)     # Root_class inheritance format yyyymmdd

        #  TODO: pull information on flight numners from the info web and use that to pull info through flightview.
        # attempt to only pull departure and destination from the united from the info web.
        # TODO: Use Flightstats for scheduled times conversion
        info = f"https://united-airlines.flight-status.info/ua-{flt_num}"               # This web probably contains incorrect information.
        flight_view = "https://www.flightview.com/flight-tracker/UA/492?date=20230702&depapt=EWR"   # check pull_dep_des 
        flight_stats_url = f"https://www.flightstats.com/v2/flight-tracker/UA/{flt_num}?year={date[:4]}&month={date[4:6]}&date={date[-2:]}"
        soup = self.request(info)
        
        soup_fs = self.request(flight_stats_url)
        fs_juice = soup_fs.select('[class*="TicketContainer"]')     # This is the whole packet not needed now
        fs_time_zone = soup_fs.select('[class*="TimeGroupContainer"]')
        departure_time_zone = fs_time_zone[0].get_text()        #  format is HH:MM XXX timezone(eg.EST)
        departure_time_zone = "STD " + departure_time_zone[9:18]
        departure_estimated_or_actual = departure_time_zone[18:]
        arrival_time_zone = fs_time_zone[1].get_text()
        arrival_time_zone = "STA " + arrival_time_zone[9:18]
        arrival_estimated_or_actual = arrival_time_zone[18:]


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

        nas_packet = self.gs_sorting(departure_ID, destination_ID)
        soup_fv = self.pull_dep_des(query_in_list_form, departure_ID)

        return {'flight_number': f'UA{flt_num}',            # This flt_num is probably misleading since the UA attached manually. Try pulling it from the flightstats web
                 'departure_ID': departure_ID,
                 'destination_ID':destination_ID,
                 'departure_gate': departure_gate,
                 'scheduled_departure_time': scheduled_departure_time,
                 'actual_departure_time': actual_departure_time,
                 'destination_gate': destination_gate,
                 'scheduled_arrival_time': scheduled_arrival_time,
                 'actual_arrival_time': actual_arrival_time,
                 'nas_packet': nas_packet
                 }


    def gs_sorting(self,dep_ID, dest_ID):
        # TODO: airport closures remaining
        departure_ID = dep_ID[1:]       # Stripping off the 'K' since NAS uses 3 letter airport ID
        destination_ID = dest_ID[1:]

        nas_delays = self.nas_status()
        airport_closures = nas_delays['Airport Closure']
        ground_stop_packet = nas_delays['ground_stop_packet']
        ground_delay_packet = nas_delays['ground_delay_packet']
        arr_dep_del_list = nas_delays['arr_dep_del_list']

        departure_affected = {}
        destination_affected = {}


        affected_ground_stop = []
        for i in airport_closures:
            if i[0] == 'ARPT':
                airport_identifier = i[1]
                affected_ground_stop.append(airport_identifier)
                if airport_identifier == departure_ID or airport_identifier == destination_ID:
                    airport_index = airport_closures.index(i)
                    reason = airport_closures[airport_index+1][1]
                    start = airport_closures[airport_index+2][1]
                    reopen = airport_closures[airport_index+3][1]
                    if airport_identifier == departure_ID:
                        departure_affected.update({'Airport Closure':{'Departure': airport_identifier,
                                                'Reason': reason,
                                                'Start': start,
                                                'Reopen': reopen}})
                    if airport_identifier == destination_ID:
                        destination_affected.update({'Airport Closure':{'Destination': airport_identifier,
                                                'Reason': reason,
                                                'Start': start,
                                                'Reopen': reopen}})

        affected_ground_delay_packet = []
        for i in ground_delay_packet:
            if i[0] == 'ARPT':
                airport_identifier = i[1]
                affected_ground_delay_packet.append(airport_identifier)
                if airport_identifier == departure_ID or airport_identifier == destination_ID:
                    airport_index = ground_delay_packet.index(i)
                    reason = ground_delay_packet[airport_index+1][1]
                    average_delay = ground_delay_packet[airport_index+2][1]
                    max_delay = ground_delay_packet[airport_index+3][1]
                    if airport_identifier == departure_ID:
                        departure_affected.update({'Ground Delay':{'Departure': airport_identifier,
                                                'Reason': reason,
                                                'Average Delay': average_delay,
                                                'Maximum Delay': max_delay}})
                    if airport_identifier == destination_ID:
                        destination_affected.update({'Ground Delay':{'Destination': airport_identifier,
                                                'Reason': reason,
                                                'Average Delay': average_delay,
                                                'Maximum Delay': max_delay}})

                                                
        affected_ground_stop_packet = []
        for i in ground_stop_packet:
            if i[0] == 'ARPT':
                airport_identifier = i[1]
                affected_ground_stop_packet.append(airport_identifier)
                if airport_identifier == departure_ID or airport_identifier == destination_ID:
                    airport_index = ground_stop_packet.index(i)
                    reason = ground_stop_packet[airport_index+1][1]
                    end_time = ground_stop_packet[airport_index+2][1]
                    if airport_identifier == departure_ID:
                        departure_affected.update({'Ground Stop':{'Departure': airport_identifier,
                                                'Reason': reason,
                                                'End Time': end_time}})
                    if airport_identifier == destination_ID:
                        destination_affected.update({'Ground Stop':{'Destination': airport_identifier,
                                                'Reason': reason,
                                                'End Time': end_time}})

        affected_arr_dep_del_list = []
        for i in arr_dep_del_list:
            if i[0] == 'ARPT':
                airport_identifier = i[1]
                affected_arr_dep_del_list.append(airport_identifier)
                if airport_identifier == departure_ID or airport_identifier == destination_ID:
                    airport_index = arr_dep_del_list.index(i)
                    reason = arr_dep_del_list[airport_index+1][1]
                    arr_or_dep = arr_dep_del_list[airport_index+2][1]
                    min_delay = arr_dep_del_list[airport_index+3][1]
                    max_delay = arr_dep_del_list[airport_index+4][1]
                    trend = arr_dep_del_list[airport_index+5][1]
                    if airport_identifier == departure_ID:
                        departure_affected.update({'Arrival/Departure Delay':{'Departure': airport_identifier,
                                                'Reason': reason,
                                                'Type': arr_or_dep['Type'],
                                                'Minimum': min_delay,
                                                'Maximum': max_delay,
                                                'Trend': trend}})
                    if airport_identifier == destination_ID:
                        destination_affected.update({'Arrival/Departure Delay':{'Destination': airport_identifier,
                                                'Reason': reason,
                                                'Type': arr_or_dep['Type'],
                                                'Minimum': min_delay,
                                                'Maximum': max_delay,
                                                'Trend': trend}})

        return {'departure_affected': departure_affected,
                'destination_affected': destination_affected}


    def nas_status(self):
        '''
        import pickle
        with open('et_root_eg_1.pkl', 'wb') as f:
            pickle.dump(root, f)
        with open('et_root_eg_1.pkl', 'rb') as f:
            root = pickle.load(f)
        '''

        '''
        import requests
        from bs4 import BeautifulSoup as bs4
        from dj.dj_app.root.root_class import Root_class
        import xml.etree.ElementTree as ET
        import pytz
        '''
        nas = "https://nasstatus.faa.gov/api/airport-status-information"
        response = requests.get(nas)
        xml_data = response.content

        root = ET.fromstring(xml_data) 
        '''
        # These upto pickle load is dummy file. comment them out to get the actual NAS packet.
        import pickle

        with open('ewr_delay_packet_experimantal.pkl', 'rb') as f:
            root = pickle.load(f)
        '''
        update_time = root[0].text

        affected_airports = [i.text for i in root.iter('ARPT')]
        affected_airports = list(set(affected_airports))
        affected_airports.sort()

        airport_closures = []
        closure = root.iter('Airport_Closure_List')
        for i in closure:
            for y in i:
                for x in y:
                    airport_closures.append([x.tag, x.text])

        ground_stop_packet = []
        count = 0
        for programs in root.iter('Program'):
            count += 1
            for each_program in programs:
                ground_stop_packet.append([each_program.tag, each_program.text])

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

        return {'update_time': update_time,
                'affected_airports': affected_airports,
                'ground_stop_packet': ground_stop_packet, 
                'ground_delay_packet': ground_delay_packet,
                'arr_dep_del_list': arr_dep_del_list,
                'Airport Closure': airport_closures
                }


    def pull_dep_des(self, query_in_list_form, airport):             # not used yet. Plan on using it such that only reliable and useful information is pulled.

        query = ' '.join(query_in_list_form)

        flt_num = query.split()[1]
        if len(query.split()) > 2:
            airport = query.split()[2]
        else:
            pass

        # date format in the url is YYYYMMDD. For testing, you can find flt_nums on https://www.airport-ewr.com/newark-departures
        use_custum_raw_date = False
        if use_custum_raw_date:
            date = 20230505
        else:
            date = self.date_time(raw=True)     # Root_class inheritance format yyyymmdd
        flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num}?date={date}&depapt={airport[1:]}"

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


class NAS_template:
    def __init__(self,
                 update_time=None,
                 affected_airports=None,
                 ground_stop_packet=None,
                 ground_delay_packet=None,
                 arr_dep_del_list=None,
                 airport_closures=None,

                ) -> None:
        pass
    def output(self):
        return {'Update Time': self.update_time,
                'Affected Airports': self.affected_airports,
                'Ground Stop': self.ground_stop_packet,
                'Ground Delay': self.ground_delay_packet,
                'Arrival/Departure Delay': self.arr_dep_del_list,
                'Airport Closure': self.airport_closures,
                }
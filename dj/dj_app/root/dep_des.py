import requests
from bs4 import BeautifulSoup as bs4
from .root_class import Root_class
import xml.etree.ElementTree as ET
import re
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


    def pull_UA(self, query):
        if type(query) == list:
             query = query[1]
            
        # flt_num = query.split()[1]
        flt_num = query
        # airport = query.split()[2]        This was for when passing `i flt_num airport` as search
        date = self.date_time(raw=True)     # Root_class inheritance format yyyymmdd
        
        #  TODO: pull information on flight numners from the info web and use that to pull info through flightview.
        # attempt to only pull departure and destination from the united from the info web.
        # TODO: Use Flightstats for scheduled times conversion
        flight_view = "https://www.flightview.com/flight-tracker/UA/492?date=20230702&depapt=EWR"   # check pull_dep_des 

        flight_stats_url = f"https://www.flightstats.com/v2/flight-tracker/UA/{flt_num}?year={date[:4]}&month={date[4:6]}&date={date[-2:]}"
        soup_fs = self.request(flight_stats_url)
        
        
        # fs_juice = soup_fs.select('[class*="TicketContainer"]')     # This is the whole packet not needed now
        fs_time_zone = soup_fs.select('[class*="TimeGroupContainer"]')
        if fs_time_zone:
            departure_time_zone = fs_time_zone[0].get_text()        #  format is HH:MM XXX timezone(eg.EST)
            departure_time_zone = "STD " + departure_time_zone[9:18]
            # departure_estimated_or_actual = departure_time_zone[18:]
            arrival_time_zone = fs_time_zone[1].get_text()
            arrival_time_zone = "STA " + arrival_time_zone[9:18]
            # arrival_estimated_or_actual = arrival_time_zone[18:]
        else:
            departure_time_zone = None
            arrival_time_zone = None

        # info = f"https://united-airlines.flight-status.info/ua-{flt_num}"               # This web probably contains incorrect information.
        # soup = self.request(info)
        # Airport distance and duration can be misleading. Be careful with using these. 
        # airport_id = soup.find_all('div', {'class': 'a2_ak'})
        # airport_id = [i.text for i in airport_id if 'ICAO' in i.text]
        # departure_ID = airport_id[0].split()[2]
        # destination_ID = airport_id[1].split()[2]

        
        # fa_data = self.flight_aware_data(query)     # TODO: This shouldn't be here. move it to views.py 

        # Matching flightaware departure and destination with base for accuracy
        print('Success at pull_UA for scheduled_dep and arr with time zone')
        bulk_flight_deet = {'flight_number': f'UA{flt_num}',            # This flt_num is probably misleading since the UA attached manually. Try pulling it from the flightstats web
                #  'departure_ID': departure_ID,          # From united-flights.info web.
                #  'destination_ID':destination_ID,       # From united-flights.info web.

                 'scheduled_departure_time': departure_time_zone,
                 'scheduled_arrival_time': arrival_time_zone,
                                            }

        return bulk_flight_deet


    def united_flight_status_info_scrape(self, query):

        flt_num = query
        info = f"https://united-airlines.flight-status.info/ua-{flt_num}"               # This web probably contains incorrect information.
        soup = self.request(info)
        # Airport distance and duration can be misleading. Be careful with using these. 
        # table = soup.find('div', {'class': 'a2'})
        airport_id = soup.find_all('div', {'class': 'a2_ak'})
        airport_id = [i.text for i in airport_id if 'ICAO' in i.text]
        departure_ID = airport_id[0].split()[2]
        destination_ID = airport_id[1].split()[2]
        print('Success at united_flight_stat scrape for dep and des ID')

        return {'departure_ID': departure_ID,
                'destination_ID': destination_ID}



    def gs_sorting(self,dep_ID, dest_ID):
        # TODO: airport closures remaining
        departure_ID = dep_ID[1:]       # Stripping off the 'K' since NAS uses 3 letter airport ID
        destination_ID = dest_ID[1:]

        nas_delays = self.nas_status()          # Doing the scraping here
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

        print('Done NAS through gs_sorting')
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
        
        print('done NAS pull through nas_status')
        return {'update_time': update_time,
                'affected_airports': affected_airports,
                'ground_stop_packet': ground_stop_packet, 
                'ground_delay_packet': ground_delay_packet,
                'arr_dep_del_list': arr_dep_del_list,
                'Airport Closure': airport_closures
                }


    def pull_dep_des(self, query, airport=None):             # not used yet. Plan on using it such that only reliable and useful information is pulled.

        flt_num = query

        # date format in the url is YYYYMMDD. For testing, you can find flt_nums on https://www.airport-ewr.com/newark-departures
        use_custom_dummy_data = False
        if use_custom_dummy_data:
            date = 20230505
        else:
            date = str(self.date_time(raw=True))     # Root_class inheritance format yyyymmdd
        flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num}?date={date}&depapt={airport[1:]}"
        soup = self.request(flight_view)
        try :
            leg_data = soup.find_all('div', class_='leg')   # Has all the departure and destination data
            departure_gate = leg_data[0].find_all('tr', class_='even')[1].text[17:]
            # departure_gate = departure_gate[26:-1]
            arrival_gate = leg_data[0].find_all('tr', class_='even')[4].text[17:]
            # arrival_gate = arrival_gate[26:-1]
            if 'Terminal' in departure_gate:
                departure_gate = departure_gate.replace('Terminal', '')
            if 'Terminal' in arrival_gate:
                arrival_gate = arrival_gate.replace('Terminal', '')

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
            # return dict({flt_num: [departure, destination]})
            
            if 'min' in departure_gate:      # This acocunts for faulty hrs and mins in string
                departure_gate = None
            if 'min' in arrival_gate:
                arrival_gate = None
            print('success at pull_dep_des for gate info')
            return {'departure_gate': departure_gate,
                    'arrival_gate': arrival_gate,
                    }
            
        except :
            empty_soup = {'departure_gate': 'None',
                          'arrival_gate': 'None'} 
            print('unsuccessful at pull_dep_des for gate info')
            return empty_soup

        # typically 9th index of scripts is where departure and destination is.
            # try print(scripts[9].get_text()) for string version for parsing
        
        # print(departure, destination)

    def flight_aware_data(self, query):

        apiKey = "V2M5XJKNC5L1oJb0Dxukt0HJ7c8cxXDQ"
        apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
        auth_header = {'x-apikey':apiKey}

        """
        airport = 'KSFO'
        payload = {'max_pages': 2}
        auth_header = {'x-apikey':apiKey}
        response = requests.get(apiUrl + f"airports/{airport}/flights",
            params=payload, headers=auth_header)
        
        # fa_flight_id = ""
        # response = requests.get(apiUrl + f"flights/{fa_flight_id}/route", headers=auth_header)
        
        """

        response = requests.get(apiUrl + f"flights/UAL{query}", headers=auth_header)

        route = None        # Declaring not available unless available throught flights
        filed_altitude, filed_ete = None, None
        if response.status_code == 200:
            flights = response.json()['flights']

            """
            # these flights are across 10 days and hence iter across them
            for i in range(len(flights)):
                fa_flight_id = flights[i]['fa_flight_id']
                origin = flights[i]['origin']['code_icao']
                destination = flights[i]['destination']['code_icao']
                scheduled_out = flights[i]['scheduled_out']
                estimated_out = flights[i]['estimated_out']
                actual_out = flights[i]['actual_out']
                scheduled_off = flights[i]['scheduled_off']
                estimated_off = flights[i]['estimated_off']
                actual_off = flights[i]['actual_off']
                scheduled_on = flights[i]['scheduled_on']
                estimated_on = flights[i]['estimated_on']
                actual_on = flights[i]['actual_on']
                scheduled_in = flights[i]['scheduled_in']
                estimated_in = flights[i]['estimated_in']
                actual_in = flights[i]['actual_in']
                
                route = flights[i]['route']
                gate_origin = flights[i]['gate_origin']
                gate_destination = flights[i]['gate_destination']
                terminal_origin = flights[i]['terminal_origin']
                terminal_destination = flights[i]['terminal_destination']
                registration = flights[i]['registration']
                departure_delay = flights[i]['departure_delay']
                arrival_delay = flights[i]['arrival_delay']
                filed_ete = flights[i]['filed_ete']
                filed_altitude = flights[i]['filed_altitude']
            """

            if flights:
                for i in range(3):
                    if flights[i]['route']:
                        origin = flights[i]['origin']['code_icao']
                        destination = flights[i]['destination']['code_icao']
                        registration = flights[i]['registration']
                        print(origin)
                        scheduled_out_fa = flights[i]['scheduled_out']
                        scheduled_out = re.search("T(\d{2}:\d{2})", scheduled_out_fa).group(1).replace(":","") + "Z"
                        estimated_out = flights[i]['estimated_out']
                        estimated_out = re.search("T(\d{2}:\d{2})", estimated_out).group(1).replace(":","") + "Z"

                        scheduled_in = flights[i]['scheduled_in']
                        scheduled_in = re.search("T(\d{2}:\d{2})", scheduled_in).group(1).replace(":","") + "Z"
                        estimated_in = flights[i]['estimated_in']
                        estimated_in = re.search("T(\d{2}:\d{2})", estimated_in).group(1).replace(":","") + "Z"

                        route = flights[i]['route']
                        filed_altitude =  "FL" + str(flights[i]['filed_altitude'])
                        filed_ete = flights[i]['filed_ete']

                        rs = route.split()
                        if len(rs) > 1:
                            rh = []
                            for i in rs:
                                rh.append(f"%20{rs[rs.index(i)]}")
                            rh = ''.join(rh)
                        sv = f"https://skyvector.com/?fpl=%20{origin}{rh}%20{destination}"

                        sv = f"https://skyvector.com/api/lchart?fpl=%20{origin}{rh}%20{destination}"
                        print(sv)     

                        break

                    else:
                        filed_ete, filed_altitude, route, estimated_in = [None] * 4
                        scheduled_in, estimated_out, scheduled_out = [None] * 3
                        registration, destination, origin, sv = [None] * 4

            else:
                filed_ete, filed_altitude, route, estimated_in = [None] * 4
                scheduled_in, estimated_out, scheduled_out = [None] * 3
                registration, destination, origin, sv = [None] * 4

            print('done f_a_data')
            return {
                    'origin':origin, 
                    'destination':destination, 
                    'registration':registration, 
                    'scheduled_out':scheduled_out, 
                    'estimated_out':estimated_out, 
                    'scheduled_in':scheduled_in, 
                    'estimated_in':estimated_in, 
                    'route':route, 
                    'filed_altitude':filed_altitude, 
                    'filed_ete':filed_ete,
                    'sv': sv,
                    # 'scheduled_out_fa': scheduled_out_fa
                            }
                           
        else:
            print(response.status_code)
        

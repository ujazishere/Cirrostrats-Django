import requests
from .root_class import Root_class
import re


class Flight_aware_pull(Root_class):
    def __init__(self) -> None:
        attrs = ['origin','destination','registration',
                 'scheduled_out','estimated_out','scheduled_in',
                 'estimated_in','route','filed_altitude','filed_ete','sv',]
        self.attrs = dict(zip(attrs,[None]*len(attrs)))
        self.current_utc = self.date_time(raw_utc=True)

    def initial_pull(self, query):
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
        
        if response.status_code == 200:
            return response.json()['flights']
        else:
            print('RESPONSE STATUS CODE NOT 200!!!', response.status_code)
            return None    
    
        
def fa_data_pull_test(query,):
    print('in fa_data_pulllll')
    flights = Flight_aware_pull().initial_pull(query)
    current_UTC = Flight_aware_pull().current_utc
    route = None        # Declaring not available unless available throught flights
    filed_altitude, filed_ete = None, None

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
        for i in range(3):      # There are typically 15 of these for multiple dates
            if flights[i]['route']:
                origin = flights[i]['origin']['code_icao']
                destination = flights[i]['destination']['code_icao']
                registration = flights[i]['registration']
                scheduled_out_fa = flights[i]['scheduled_out']
                print(scheduled_out_fa)
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

                # sv = f"https://skyvector.comi/api/lchart?fpl=%20{origin}{rh}%20{destination}"

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
                       
    


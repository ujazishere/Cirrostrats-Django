import requests
import pickle
from .root_class import Root_class
import re

class Flight_aware_pull(Root_class):
    def __init__(self) -> None:
        attrs = ['origin','destination','registration',
                 'scheduled_out','estimated_out','scheduled_in',
                 'estimated_in','route','filed_altitude','filed_ete','sv',]
        
        self.attrs = dict(zip(attrs,[None]*len(attrs)))
        
        self.current_utc = self.date_time(raw_utc=True)

    def initial_pull(self, airline_code=None, query=None):
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
        if not airline_code:
            airline_code = 'UAL'
        response = requests.get(apiUrl + f"flights/{airline_code}{query}", headers=auth_header) 
        
        if response.status_code == 200:
            return response.json()['flights']
        else:
            print('RESPONSE STATUS CODE NOT 200!!!', response.status_code)
            return None    


def flight_aware_data_pull(airline_code=None, query=None,):
    
    
    if not airline_code:
        airline_code = 'UAL'
    
    pull_dummy = False

    if pull_dummy:
        # Use this to recall a dummy flight packet:
        print('\n CALLING DUMMY FILE IN flight_aware_data_pull \n')
        with open ('dummy_flight_aware_packet.pkl', 'rb') as f:
            flights = pickle.load(f)
    else:
        fa_object = Flight_aware_pull()
        flights = fa_object.initial_pull(airline_code=airline_code,query=query)
    
    current_UTC = Flight_aware_pull().current_utc
    route = None        # Declaring not available unless available throught flights
    filed_altitude, filed_ete = None, None
    
    # Use this to dump a dummy flight packet:
    # with open('dummy_flight_aware_packet.pkl', 'wb') as f:
        # pickle.dump(flights,f)

    """
    Prototype for reducing the code
        You will need to delete the 'sv' key since its not associated with flight_aware.
        this will associate all keys with associated flight_aware values as long as 
            neither of them are None. if either value is None it'll clean all values back to none 

    for i in range(len(flights)):
        print(i)
        for a, b in flights[i].items():     #looping through each of ~15 dicts within a list
            if a in fa_object.attrs.keys():
                if type(b) == dict:
                    fa_object.attrs[a] = b['code'] 
                else:
                    fa_object.attrs[a] = b
        if not None in  fa_object.attrs.values():
            print(i)
            break
        for keys,vals in fa_object.attrs.items():
            if not vals:
                print(keys, vals)
                print('vals are none')
                for y in fa_object.attrs.keys():
                    fa_object.attrs[y]=None 
        
    """

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

    if flights:     # sometimes flights returns empty list.
        for i in range(3):      # There are typically 15 of these for multiple dates
            scheduled_out_raw_fa = flights[i]['scheduled_out']
            date_out = scheduled_out_raw_fa[:10].replace('-', '')       # This needs to be checked with current UTC time

            if flights[i]['route']:
                
                origin = flights[i]['origin']['code_icao']
                destination = flights[i]['destination']['code_icao']
                registration = flights[i]['registration']

                scheduled_out_raw_fa = flights[i]['scheduled_out']
                date_out = scheduled_out_raw_fa[:10].replace('-', '')       # This needs to be checked with current UTC time
                print('Current_UTC', current_UTC)
                print('Date_out', date_out)
                
                if current_UTC == date_out:
                    pass

                scheduled_out = re.search("T(\d{2}:\d{2})", scheduled_out_raw_fa).group(1).replace(":","") + "Z"
                estimated_out = flights[i]['estimated_out']     # Rename this to date or time or both 
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

                # sv = f"https://skyvector.comi/api/lchart?fpl=%20{origin}{rh}%20{destination}"     # This is for api

                print('\n Successfully completed FlightAware pull ')
                break

            else:
                return fa_object.attrs
                print('FLIGHT_AWARE_DATA UNSUCCESSFUL')

    else:
        return fa_object.attrs
        print('FLIGHT_AWARE_DATA UNSUCCESSFUL')


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
            # 'scheduled_out_raw_fa': scheduled_out_raw_fa
                    }
                       
    


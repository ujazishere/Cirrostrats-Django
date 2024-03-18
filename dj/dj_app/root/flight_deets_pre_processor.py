import pickle
from .weather_parse import Weather_parse
from .root_class import Root_class, Pull_class
from .dep_des import Pull_flight_info
import json
flt_info = Pull_flight_info()


def resp_initial_returns(resp_dict: dict, airline_code, flight_number_query,):
    # see use of this function in view.py for document
    pc = Pull_class(flight_number_query)
    flight_aware_data = flt_info.fa_data_pull()
    for url,resp in resp_dict.items():
        if "flight-status.com" in str(url):
            soup = pc.requests_processing(resp,bs=True)
            united_dep_dest = flt_info.united_departure_destination_scrape(pre_process=soup)
            # print(united_dep_dest)
        elif "flightstats.com" in str(url):
            soup = pc.requests_processing(resp,bs=True)
            flight_stats_arr_dep_time_zone = flt_info.fs_dep_arr_timezone_pull(flt_num_query=flight_number_query,pre_process=soup)
            # print(flight_stats_arr_dep_time_zone)


        elif "flightaware" in str(url):
            fa_return = json.loads(resp)
            fa_return = fa_return['flights']
            flight_aware_data = flt_info.fa_data_pull(airline_code=airline_code, flt_num=flight_number_query,pre_process=fa_return)
            # print(flight_aware_data)
        elif "aviationstack" in str(url):       #TODO: aviation stack needs work
            pass
            # soup = pc.requests_processing(resp,json=True)
            # aviation_stack_data = flt_info.aviation_stack_pull(airline_code=airline_code, flt_num=flight_number_query)
            # print(aviation_stack_data)
    

    return united_dep_dest, flight_stats_arr_dep_time_zone, flight_aware_data,
            #  aviation_stack_data


def resp_sec_returns(resp_dict,dep_airport_id,dest_airport_id):
    gate_info = None        # Declared this here. in case if gate info is not scraped variable will atleast exist. used to avoid definition error
    pc = Pull_class(dep_airport_id=dep_airport_id)
    for url,resp in resp_dict.items():
        if f"metar?ids={dep_airport_id}" in str(url):
            dep_metar = pc.requests_processing(resp,awc=True)
        elif f"taf?ids={dep_airport_id}" in str(url):
            dep_taf = pc.requests_processing(resp,awc=True)
        elif f"clowd.io/api/{dep_airport_id}" in str(url):          # TODO: Need to account for arrival dep vs arrival datis
            dep_datis = resp     # Apparently this is being returned within a list is being fed as is. Accounted for.
        elif f"metar?ids={dest_airport_id}" in str(url):
            dest_metar = pc.requests_processing(resp,awc=True)
        elif f"taf?ids={dest_airport_id}" in str(url):
            dest_taf = pc.requests_processing(resp,awc=True)
        elif f"clowd.io/api/{dest_airport_id}" in str(url):         # TODO: Need to account for arrival datis vs dep
            dest_datis = resp         # Apparently this is being returned within a list. Is accounted for.


        elif f"&depapt={dep_airport_id[1:]}" in str(url):
            gate_info = pc.requests_processing(resp,bs=True)
            print(gate_info,"gate info is here")

            
        elif f"faa.gov/api/airport-status-information" in str(url):
            nas_data = resp
            nas_data = flt_info.nas_final_packet(dep_ID=dep_airport_id,dest_ID=dest_airport_id)

            
        else:
            pass

    # Raw weather sent for preprocessing 
    wp = Weather_parse()            
    dep_weather = {"datis":dep_datis,"metar":dep_metar,"taf":dep_taf}
    dep_weather = wp.processed_weather(weather_raw=dep_weather)
    
    dest_weather = {"datis":dest_datis,"metar":dest_metar,"taf":dest_taf}
    dest_weather = wp.processed_weather(weather_raw=dest_weather)

    wpp = {"dep_weather":dep_weather,"dest_weather":dest_weather}

    wpp = wp.nested_weather_dict_explosion(wpp)     # Doing this to avoid nested weather dictionaries


    gate_info = flt_info.flight_view_gate_info(pre_process=gate_info)

    # giving the nested weather dict explosion to simplify the front end
    return {**wpp,**gate_info}


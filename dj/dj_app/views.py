import pickle
import json
import asyncio,aiohttp
from django.views.decorators.http import require_GET
# from concurrent.futures import ThreadPoolExecutor, as_completed           # Causing issues on AWS
from django.shortcuts import render
from django.http import HttpResponse
from .root.dummy_files_call import dummy_imports
from .root.gate_checker import Gate_checker
from .root.root_class import Root_class, Pull_class, Source_links_and_api
from .root.gate_scrape import Gate_scrape_thread
from .root.weather_parse import Weather_parse
from .root.dep_des import Pull_flight_info
from .root.flight_deets_pre_processor import resp_initial_returns,resp_sec_returns,response_filter
from time import sleep
from django.shortcuts import render
from django.http import JsonResponse
# This will throw error if the file is not found. Change the EC2 file to this name.
import os

'''
views.py runs as soon as the base web is requested. Hence, GateCheckerThread() is run in the background right away.
It will then run 
'''

# TODO: move this out, have it streamlined without having to change bool everytime.
    # >> Have made progress on this by making the Switches_n_auth file and adding it to the .gitignore.
# Caution. If this file doesn't exist make one that contains this variable and make it a bool. 
# Keep it false to avoid errors with from sending email errors as it is attached to UJ's personal email creds.
# Before you remove this make sure you account for its use: Used for sending email notifications. Email creds are in Switches_n_auth.
try:        # TODO: Find a better way other than try and except
    from .root.Switch_n_auth import run_lengthy_web_scrape
except Exception as e:
    print('Couldnt find swithc_n_auth! ERROR:',e)
    run_lengthy_web_scrape = False
if run_lengthy_web_scrape:
    print('Running Lengthy web scrape')
    gc_thread = Gate_scrape_thread()
    gc_thread.start()

current_time = Gate_checker().date_time()


async def home(request):
    # Homepage first skips a "POST", goes to else and returns home.html since the query is not submitted yet.
    if request.method == "POST":
        main_query = request.POST.get('query', '')

        # This one adds similar queries to the admin panel in SearchQuerys.
        # Make it such that the duplicates are grouped using maybe unique occourances.
        # search_query = SearchQuery(query=main_query)      # Adds search queries to the database
        # search_query.save()       # you've got to save it otherwise it wont save

        # This bit will send an email notification with the query. Catered for EC2 deployment only!
        # For this to work on google you have to switch on two factor auth
        # You also need to go into the security--> 2factor auth--> app password and generate password for it
        # TODO: start this on a parallel thread so that it doesn't interfere with and add to user wait time
        # Maybe juststore these queries on a separate file and send email of synopsis
        if run_lengthy_web_scrape:
            Root_class().send_email(body_to_send=main_query)
        return await parse_query(request, main_query)

    else:
        return render(request, 'home.html')


async def parse_query(request, main_query):
    """
    Checkout note `unit testing seems crucial.txt` for the parsing logic
    """

    # Global variable since it is used outside of the if statement in case it was not triggered. purpose: Handeling Error
    query_in_list_form = []
    # if .split() method is used outside here it can return since empty strings cannot be split.

    if main_query == '':        # query is empty then return all gates
        print('Empty query')
        return gate_info(request, main_query='')
    if 'DUMM' in main_query.upper():
        return dummy(request)
    if 'ext d' in main_query:
        airport = main_query.split()[-1]
        return extra_dummy(request, airport)

    if main_query != '':
        # splits query. Necessary operation to avoid complexity. Its a quick fix for a deeper more wider issue.
        query_in_list_form = main_query.split()

        # TODO: Log the extent of query reach deep within this code, also log its occurrances to find impossible statements and frequent searches.
        # If query is only one word or item. else statement for more than 1 is outside of this indent. bring it in as an elif statement to this if.
        if len(query_in_list_form) == 1:

            # this is string form instead of list
            query = query_in_list_form[0].upper()
            # TODO: find a better way to handle this. Maybe regex. Need a system that classifies the query and assigns it a dedicated function like flight_deet or gate query.
            # Accounting for flight number query with leading alphabets
            if query[:2] == 'UA' or query[:3] == 'GJS':
                if query[0] == 'G':     # if GJS instead of UA: else its UA
                    # Its GJS
                    airline_code, flt_digits = query[:3], query[3:]
                else:
                    airline_code = None
                    flt_digits = query[2:]       # Its UA
                print('\nSearching for:', airline_code, flt_digits)
                return await flight_deets(request, airline_code=airline_code, flight_number_query=flt_digits)

            # flight or gate info page returns
            elif len(query) == 4 or len(query) == 3 or len(query) == 2:

                if query.isdigit():
                    query = int(query)
                    if 1 <= query <= 35 or 40 <= query <= 136:              # Accounting for EWR gates for gate query
                        return gate_info(request, main_query=str(query))
                    else:                                                   # Accounting for fligh number
                        return await flight_deets(request, airline_code=None, flight_number_query=query)
                else:
                    if len(query) == 4 and query[0] == 'K':
                        weather_query_airport = query
                        # Making query uppercase for it to be compatible
                        weather_query_airport = weather_query_airport.upper()
                        return weather_display(request, weather_query_airport)
                    else:           # tpical gate query with length of 2-4 alphanumerics
                        print('gate query')
                        return gate_info(request, main_query=str(query))
            # Accounting for 1 letter only. Gate query.
            elif 'A' in query or 'B' in query or 'C' in query or len(query) == 1:
                # When the length of query_in_list_form is only 1 it returns gates table for that particular query.
                gate_query = query
                return gate_info(request, main_query=gate_query)
            else:   # return gate
                gate_query = query
                return gate_info(request, main_query=gate_query)

        # its really an else statement but stated >1 here for situational awareness. This is more than one word query.
        elif len(query_in_list_form) > 1:
            # Making it uppercase for compatibility issues and error handling
            first_letter = query_in_list_form[0].upper()
            if first_letter == 'W':
                weather_query_airport = query_in_list_form[1]
                # Making query uppercase for it to be compatible
                weather_query_airport = weather_query_airport.upper()
                return weather_display(request, weather_query_airport)
            else:
                return gate_info(request, main_query=' '.join(query_in_list_form))


def gate_info(request, main_query):
    gate = main_query
    # In the database all the gates are uppercase so making the query uppercase
    gate = gate.upper()
    current_time = Root_class().date_time()

    # This is a list full of dictionararies returned by err_UA_gate depending on what user requested..
    # Each dictionary has 4 key value pair.eg. gate:c10,flight_number:UA4433,scheduled:20:34 and so on
    gate_data_table = Gate_checker().ewr_UA_gate(gate)
    

    # This can be a json to be delivered to the frontend
    data_out = {'gate_data_table': gate_data_table, 'gate': gate, 'current_time': current_time}

    # showing info if the info is found else it falls back to `No flights found for {{gate}}`on flight_info.html
    if gate_data_table:
        # print(gate_data_table)
        return render(request, 'flight_info.html', data_out)
    else:       # Returns all gates since query is empty. Maybe this is not necessary. TODO: Try deleting else statement.
        return render(request, 'flight_info.html', {'gate': gate})


async def flight_deets(request,airline_code=None, flight_number_query=None, ):
    
    
    # You dont have to turn this off(False) running lengthy scrape will automatically enable fa pull
    if run_lengthy_web_scrape:
        bypass_fa = False
    else:
        bypass_fa = True        


    bulk_flight_deets = {}

    # TODO: Priority: Each individual scrape should be separate function. Also separate scrape from api fetch
    ''' *****VVI******  
    Logic: resp_dict gets all information fetched from root_class.Pull_class().async_pull(). Look it up and come back.
    pre-processes it using resp_initial_returns and resp_sec_returns for inclusion in the bulk_flight_deets..
    first async response returs origin and destination through united's flight-status since their argument only
    takes in flightnumber and it als, also gets scheduled times in local time zones through flightstats,
    and the packet from flightaware.
    This origin and destination is then used to make another async request that requires additional arguments
    This is the second resp_dict that returns weather and nas in the resp_sec,
    '''

    sl = Source_links_and_api()
    pc = Pull_class(airline_code=airline_code,flt_num=flight_number_query)
    if bypass_fa:

        resp_dict:dict = await pc.async_pull([sl.ua_dep_dest_flight_status(flight_number_query),
                                              sl.flight_stats_url(flight_number_query),])
        # """
        # This is just for testing
        # fa_test_path = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\fa_test.pkl"
        # with open(fa_test_path, 'rb') as f:
            # resp = pickle.load(f)
            # fa_resp = json.loads(resp)
        # resp_dict.update({'https://aeroapi.flightaware.com/aeroapi/flights/UAL4433':fa_resp})
        # """
    else:
        resp_dict:dict = await pc.async_pull([sl.ua_dep_dest_flight_status(flight_number_query),
                                              sl.flight_stats_url(flight_number_query),
                                              sl.flight_aware_w_auth(airline_code,flight_number_query),
                                              ])
    # /// End of the first async await, next one is for weather and nas ///.

    # flight_deet preprocessing. fetched initial raw data gets fed into their respective pre_processors through this function that iterates through the dict
    resp_initial = resp_initial_returns(resp_dict=resp_dict,airline_code=airline_code,flight_number_query=flight_number_query)
    # assigning the resp_initial to their respective variables that will be fed into bulk_flight_deets and..
    # the departure and destination gets used for weather and nas pulls in the second half of the response pu

    united_dep_dest, flight_stats_arr_dep_time_zone, fa_data= resp_initial
    # united_dep_dest,flight_stats_arr_dep_time_zone,flight_aware_data,aviation_stack_data = resp_initial

    # This will init the flight_view for gate info
    if fa_data['origin']:           # Flightaware data is prefered as source for otherdata.
        pc = Pull_class(flight_number_query,fa_data['origin'],fa_data['destination'])
        wl_dict = pc.weather_links(fa_data['origin'],fa_data['destination'])
        # OR get the flightaware data for origin and destination airport ID as primary then united's info.
        # also get flight-stats data. Compare them all for information.

        # fetching weather, nas and gate info since those required departure, destination
        # TODO: Probably take out nas_data from here and put it in the initial pulls.
        resp_dict:dict = await pc.async_pull(list(wl_dict.values())+[sl.nas(),])

        # /// End of the second and last async await.

        
        # Weather and nas information processing
        resp_sec = resp_sec_returns(resp_dict,fa_data['origin'],fa_data['destination']) 

        weather_dict = resp_sec
        gate_returns = Pull_flight_info().flight_view_gate_info(flt_num=flight_number_query,airport=fa_data['origin'])
        bulk_flight_deets = {**united_dep_dest, **flight_stats_arr_dep_time_zone, 
                            **weather_dict, **fa_data, **gate_returns}
    elif united_dep_dest['departure_ID']:       # If flightaware data is not available use this scraped data. Very unstable. TODO: Change this. Have 3 sources for redundencies
        pc = Pull_class(flight_number_query,united_dep_dest['departure_ID'],united_dep_dest['destination_ID'])
        wl_dict = pc.weather_links(united_dep_dest['departure_ID'],united_dep_dest['destination_ID'])
        # OR get the flightaware data for origin and destination airport ID as primary then united's info.
        # also get flight-stats data. Compare them all for information.

        # fetching weather, nas and gate info since those required departure, destination
        # TODO: Probably take out nas_data from here and put it in the initial pulls.
        resp_dict:dict = await pc.async_pull(list(wl_dict.values())+[sl.nas()])

        # /// End of the second and last async await.

        
        # Weather and nas information processing
        resp_sec = resp_sec_returns(resp_dict,united_dep_dest['departure_ID'],united_dep_dest['destination_ID']) 

        weather_dict = resp_sec
        gate_returns = Pull_flight_info().flight_view_gate_info(flt_num=flight_number_query,airport=united_dep_dest['departure_ID'])
        bulk_flight_deets = {**united_dep_dest, **flight_stats_arr_dep_time_zone, 
                            **weather_dict, **fa_data, **gate_returns}

    else:
        print('No Departure/Destination ID')
        bulk_flight_deets = {**united_dep_dest, **flight_stats_arr_dep_time_zone, 
                            **fa_data, }
    # More streamlined to merge dict than just the typical update method of dict. update wont take multiple dictionaries



    # If youre looking for without_futures() that was used prior to the async implementation..
        #  you fan find it in Async milestone on hash dd7ebd0efa3b5a62798c88bcfe77cc43f8c0048c
        # It was an inefficient fucntion to bypass the futures error on EC2

    return render(request, 'flight_deet.html', bulk_flight_deets)


async def ua_dep_dest_flight_status(request,flight_number):
    pc = Pull_class(flt_num=flight_number)
    sl = Source_links_and_api()
    flt_info = Pull_flight_info()
    
    link = sl.ua_dep_dest_flight_status(flight_number)
    resp_dict:dict = await pc.async_pull([link])

    resp = response_filter(resp_dict,"flight-status.com")
    united_dep_dest = flt_info.united_departure_destination_scrape(pre_process=resp)

    return united_dep_dest


async def flight_stats_url(request,flight_number):
    # sl.flight_stats_url(flight_number_query),])
    pc = Pull_class(flt_num=flight_number)
    sl = Source_links_and_api()
    flt_info = Pull_flight_info()
    
    link = sl.flight_stats_url(flight_number)
    resp_dict:dict = await pc.async_pull([link])

    resp = response_filter(resp_dict,"flightstats.com")
    fs_departure_arr_time_zone = flt_info.fs_dep_arr_timezone_pull(pre_process=resp)

    return fs_departure_arr_time_zone

    
async def flight_aware_w_auth(request,airline_code,flight_number):
    # sl.flight_stats_url(flight_number_query),])
    pc = Pull_class(flt_num=flight_number)
    sl = Source_links_and_api()
    flt_info = Pull_flight_info()
    
    
    link = sl.flight_aware_w_auth(airline_code,flight_number)
    resp_dict:dict = await pc.async_pull([link])

    resp = response_filter(resp_dict,"json",)
    fa_return = resp['flights']
    flight_aware_data = flt_info.fa_data_pull(airline_code=airline_code, flt_num=flight_number,pre_process=fa_return)

    # Accounted for gate through flight aware. gives terminal and gate as separate key value pairs.
    return flight_aware_data

# TODO: Need to account for aviation stack


async def metar(request, )








def weather_display(request, weather_query):

    # remove leading and trailing spaces. Seems precautionary.
    weather_query = weather_query.strip()
    airport = weather_query[-4:]

    weather = Weather_parse()
    # TODO: Need to be able to add the ability to see the departure as well as the arrival datis
    # weather = weather.scrape(weather_query, datis_arr=True)
    weather = weather.processed_weather(query=weather_query, )

    weather_page_data = {}

    weather_page_data['airport'] = airport

    weather_page_data['D_ATIS'] = weather['D-ATIS']
    weather_page_data['METAR'] = weather['METAR']
    weather_page_data['TAF'] = weather['TAF']

    weather_page_data['datis_zt'] = weather['D-ATIS_zt']
    weather_page_data['metar_zt'] = weather['METAR_zt']
    weather_page_data['taf_zt'] = weather['TAF_zt']
    weather_page_data['trr'] = weather_page_data
    return render(request, 'weather_info.html', weather_page_data)


class Menu_pages:
    def __init__(self) -> None:
        pass


def contact(request):
    return render(request, 'contact.html')


def ourstory(request):
    return render(request, 'ourstory.html')


def source(request):
    return render(request, 'source.html')


def gate_check(request):
    return render(request, 'gate_check.html')


def flight_lookup(request):
    return render(request, 'home.html', {'flight_lookup': True})


def weather(request):
    return render(request, 'weather.html')


def guide(request):
    return render(request, 'guide.html')


def report_an_issue(request):
    return render(request, 'report_an_issue.html')


def live_map(request):
    return render(request, 'live_map.html')


def dummy(request):
    dummy_imports_tuple = dummy_imports()

    bulk_flight_deets = dummy_imports_tuple[0]
    print(bulk_flight_deets.keys())

    # within dummy
    print('Going to flight_deet.html through dummy() function in views.py')

    return render(request, 'flight_deet.html', bulk_flight_deets)


def extra_dummy(request, airport):
    # This page is returned by using `ext d` in the search bar
    # Renders the page and html states it gets the data from data_v
    return (render(request, 'extra_dummy.html', {'airport': airport}))

# This function gets loaded within the dummy2 page whilst dummy2 func gets rendered.
# the fetch area in js acts as url. it will somehow get plugged into the urls.py's data_v line with the airport
# that airport then gets plugged in here. request is the WSGI thing and second argument is what you need
@require_GET
def nas_data(request, airport):
    print('Within nas_data func w decorator that allows for pulling this functions data in backgroung once page is loaded up',request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(0.5)

    dummy_imports_tuple = dummy_imports()
    bulk_flight_deets = dummy_imports_tuple[0]

    data_return = bulk_flight_deets['nas_departure_affected']
    # print(data_return.keys())

    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


@require_GET
def weather_data(request, airport):

    print('Inside weather_data views func', request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(1)
    
    dummy_imports_tuple = dummy_imports()
    bulk_flight_deets = dummy_imports_tuple[0]

    weather_extracts = {}
    weather_extracts['dep_weather'] = {
        'D-ATIS': [bulk_flight_deets['dep_weather']['D-ATIS_zt'], bulk_flight_deets['dep_datis']]}
    weather_extracts['dep_weather'].update(
        {'METAR': [bulk_flight_deets['dep_weather']['METAR_zt'], bulk_flight_deets['dep_metar'],]})
    weather_extracts['dep_weather'].update(
        {'TAF': [bulk_flight_deets['dep_weather']['TAF_zt'], bulk_flight_deets['dep_taf']]})

    weather_extracts['dest_weather'] = bulk_flight_deets['dest_weather']
    

    def actual_weather_pull():
        weather = Weather_parse()
        weather = weather.processed_weather(airport, )

        weather_page_data = {}

        weather_page_data['airport'] = airport

        weather_page_data['D_ATIS'] = weather['D-ATIS']
        weather_page_data['METAR'] = weather['METAR']
        weather_page_data['TAF'] = weather['TAF']

        weather_page_data['datis_zt'] = weather['D-ATIS_zt']
        weather_page_data['metar_zt'] = weather['METAR_zt']
        weather_page_data['taf_zt'] = weather['TAF_zt']
        # weather_page_data['trr'] = weather_page_data
        return weather_page_data

    # data_return = actual_weather_pull()
    data_return = weather_extracts
    # print(data_return.keys())

    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


@require_GET
def summary_box(request, airport):

    print('Insidee summary_box func', request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(1.5)

    dummy_imports_tuple = dummy_imports()
    bulk_flight_deets = dummy_imports_tuple[0]

    data_return = bulk_flight_deets['nas_departure_affected']
    # print(data_return.keys())

    data_return = bulk_flight_deets
    print(data_return.keys())

    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


@require_GET
def data_v(request, airport):

    print('data_v called')
    print('within data_v', request, airport)
    airport = 'KEWR'        # declaring it regardless
    bulk_flight_deets = dummy_imports()

    # return render(request, 'weather_info.html')
    return JsonResponse(bulk_flight_deets)

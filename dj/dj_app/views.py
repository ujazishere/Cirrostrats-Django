import pickle
import asyncio, aiohttp
from django.views.decorators.http import require_GET
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.shortcuts import render
from django.http import HttpResponse
from .root.gate_checker import Gate_checker
from .root.root_class import Root_class
from .root.gate_scrape import Gate_scrape_thread
from .root.weather_parse import Weather_parse
from .root.dep_des import Pull_flight_info
from time import sleep
from django.shortcuts import render
from django.http import JsonResponse
import os

'''
views.py runs as soon as the base web is requested. Hence, GateCheckerThread() is run in the background right away.
It will then run 
'''

# TODO: move this out, have it streamlined without having to change bool everytime
    # Before you remove this make sure you account for its use: Used for sending email notifications
run_lengthy_web_scrape = False 

if run_lengthy_web_scrape:
    print('Running Lengthy web scrape')
    gc_thread = Gate_scrape_thread()
    gc_thread.start()

current_time = Gate_checker().date_time()


def home(request):
    # Homepage first skips a "POST", goes to else and returns home.html since the query is not submitted yet.
    if request.method == "POST":
        main_query = request.POST.get('query','')
        
        # This one adds similar queries to the admin panel in SearchQuerys.
        # Make it such that the duplicates are grouped using maybe unique occourances.
        # search_query = SearchQuery(query=main_query)      # Adds search queries to the database
        # search_query.save()       # you've got to save it otherwise it wont save

        # This bit will send an email notification with the query. Catered for EC2 deployment only!
        # For this to work on google you have to switch on two factor auth
            # You also need to go into the security--> 2factor auth--> app password and generate password for it  
        # TODO: start this on a parallel thread so that it doesn't interfere with and add to user wait time
        if run_lengthy_web_scrape:
            Root_class().send_email(body_to_send=main_query)
        return parse_query(request, main_query)

    else:
        return render(request, 'home.html')


def parse_query(request, main_query):

    """
    Checkout note `unit testing seems crucial.txt` for the parsing logic
    """

    query_in_list_form = []     # Global variable since it is used outside of the if statement in case it was not triggered. purpose: Handeling Error
                                    # if .split() method is used outside here it can return since empty strings cannot be split.

    if main_query == '':        # query is empty then return all gates
        print('Empty query: Inside just prior to the gate_info func')
        return gate_info(request, main_query='')
    if 'DUMM' in main_query.upper():
        return dummy(request)
    if 'ext d' in main_query:
        airport = main_query.split()[-1]
        return dummy2(request, airport)

    if main_query != '':
        query_in_list_form = main_query.split()     # splits query. Necessary operation to avoid complexity. Its a quick fix for a deeper more wider issue.

        # TODO: Log the extent of query reach deep within this code, also log its occurrances to find impossible statements and frequent searches.
        if len(query_in_list_form) == 1:            # If query is only one word or item. else statement for more than 1 is outside of this indent. bring it in as an elif statement to this if.

            query = query_in_list_form[0].upper()           # this is string form instead of list
            # TODO: find a better way to handle this. Maybe regex. Need a system that classifies the query and assigns it a dedicated function like flight_deet or gate query.
            if query[:2] == 'UA' or query[:3] == 'GJS':         # Accounting for flight number query with leading alphabets 
                if query[0] == 'G':     # if GJS instead of UA: else its UA
                    airline_code, flt_digits = query[:3], query[3:]          # Its GJS
                else:
                    airline_code = None
                    flt_digits = query[2:]       # Its UA
                print('\nSearching for:', airline_code,flt_digits)
                return flight_deets(request, airline_code=airline_code,flight_number_query=flt_digits)

            elif len(query) == 4 or len(query) == 3 or len(query) == 2:     # flight or gate info page returns

                if query.isdigit():
                    query = int(query)
                    if 1 <= query <= 35 or 40 <= query <= 136:              # Accounting for EWR gates for gate query
                        return gate_info(request, main_query=str(query))
                    else:                                                   # Accounting for fligh number
                        return flight_deets(request,airline_code=None,flight_number_query=query)
                else:
                    if len(query) == 4 and query[0] == 'K':
                        weather_query_airport  = query
                        weather_query_airport = weather_query_airport.upper()       # Making query uppercase for it to be compatible
                        return weather_display(request, weather_query_airport)
                    else:           # tpical gate query with length of 2-4 alphanumerics
                        print('gate query')
                        return gate_info(request, main_query=str(query))
            elif 'A' in query or 'B' in query or 'C' in query or len(query) == 1:     # Accounting for 1 letter only. Gate query.
                # When the length of query_in_list_form is only 1 it returns gates table for that particular query.
                gate_query = query
                return gate_info(request, main_query=gate_query)
            else:   # return gate 
                gate_query = query
                return gate_info(request, main_query=gate_query)


        elif len(query_in_list_form) > 1:           # its really an else statement but stated >1 here for situational awareness. This is more than one word query.
            first_letter = query_in_list_form[0].upper()        # Making it uppercase for compatibility issues and error handling
            if first_letter == 'W':
                weather_query_airport  = query_in_list_form[1]
                weather_query_airport = weather_query_airport.upper()       # Making query uppercase for it to be compatible
                return weather_display(request, weather_query_airport)
            else:
                return gate_info(request, main_query=' '.join(query_in_list_form))

            '''
            # Attempting to pull all airports for easier search access
            florida_airports = airports['Florida'][1]
            for each_airport in florida_airports:
                if each_query in each_airport:
                    print(each_airport)
                flights = Gate_checker().departures_ewr_UA()
                print(3)
                for flt in flights:
                    # print(flt)
                    if each_query in flt:
                        print(4)
                        return flight_deets(request, abs_query, flt)
                    else:
                        # return a static html saying no information found for flight number ****
                        pass'''


def gate_info(request, main_query):
    gate = main_query
    # In the database all the gates are uppercase so making the query uppercase    
    gate = gate.upper()

    # Dictionary format a list with one or many dictionaries each dictionary containing 4 items:gate,flight,scheduled,actual

    current_time = Gate_checker().date_time()
    gate_data_table = Gate_checker().ewr_UA_gate(gate)

    # showing info if the info is found else it falls back to `No flights found for {{gate}}`on flight_info.html
    if gate_data_table: 
        # print(gate_data_table)
        return render(request, 'flight_info.html',{'gate_data_table': gate_data_table, 'gate': gate, 'current_time': current_time})
    else:       # Returns all gates since query is empty. Maybe this is not necessary. TODO: Try deleting else statement.
        return render(request, 'flight_info.html', {'gate': gate})


def flight_deets(request,airline_code=None, flight_number_query=None, ):
    bypass_fa = True
    if run_lengthy_web_scrape:
        bypass_fa = False           # to restrict fa api use: for local use keep it False. 

    flt_info = Pull_flight_info()           # from dep_des.py file
    weather = Weather_parse()         # from MET_TAF_parse.py
    
    # This is a inefficient fucntion to bypass the futures error.
    # TODO: sort this out for async feature and parallel processing 
    def without_futures():
        bulk_flight_deets = {}
        bulk_flight_deets.update(flt_info.fs_dep_arr_timezone_pull(flight_number_query))
        if not bypass_fa:       # bypassing flight_aware pull if bypass data == True
            bulk_flight_deets.update(flt_info.fa_data_pull(airline_code,flight_number_query))
        else:
            print("BYPASSING FLIGHTAWARE DATA")
            bulk_flight_deets['origin'] = ''
        bulk_flight_deets.update(flt_info.united_departure_destination_scrape(flight_number_query))

        # united dep and destination airports are inaccurate at times. This assigns flight_aware origin and destination
            # as feed in for weather, NAS and gate instead of UA dep and des feed thats to be
            # used in case flightaware cannot be accessed.
        if bulk_flight_deets['origin']:
            UA_departure_ID,UA_destination_ID = bulk_flight_deets['origin'], bulk_flight_deets['destination']
        else:        
            UA_departure_ID, UA_destination_ID = bulk_flight_deets['departure_ID'], bulk_flight_deets['destination_ID']
        bulk_flight_deets['dep_weather'] = weather.processed_weather(UA_departure_ID)
        # datis_arr as true in this case since its for the destination/arr datis.
        bulk_flight_deets['dest_weather'] = weather.processed_weather(UA_destination_ID,datis_arr=True)
        bulk_flight_deets.update(flt_info.nas_final_packet(UA_departure_ID, UA_destination_ID))
        bulk_flight_deets.update(flt_info.flight_view_gate_info(flight_number_query, UA_departure_ID))
        
        # This whole area removes the need for for loop in html making it easier to 
            # work with css styling and readibility.
        def nested_weather_dict_explosion():
            
            # Departure weather
            dep_datis = bulk_flight_deets['dep_weather']['D-ATIS']
            dep_metar = bulk_flight_deets['dep_weather']['METAR']
            dep_taf = bulk_flight_deets['dep_weather']['TAF']
            bulk_flight_deets['dep_datis']= dep_datis
            bulk_flight_deets['dep_metar']= dep_metar
            bulk_flight_deets['dep_taf']= dep_taf
            
            dep_datis_zt = bulk_flight_deets['dep_weather']['D-ATIS_zt']
            dep_metar_zt = bulk_flight_deets['dep_weather']['METAR_zt']
            dep_taf_zt = bulk_flight_deets['dep_weather']['TAF_zt']
            bulk_flight_deets['dep_datis_zt']= dep_datis_zt
            bulk_flight_deets['dep_metar_zt']= dep_metar_zt
            bulk_flight_deets['dep_taf_zt']= dep_taf_zt
            
            # Destionation Weather
            dest_datis = bulk_flight_deets['dest_weather']['D-ATIS']
            dest_metar = bulk_flight_deets['dest_weather']['METAR']
            dest_taf = bulk_flight_deets['dest_weather']['TAF']
            bulk_flight_deets['dest_datis']= dest_datis
            bulk_flight_deets['dest_metar']= dest_metar
            bulk_flight_deets['dest_taf']= dest_taf

            dest_datis_zt = bulk_flight_deets['dest_weather']['D-ATIS_zt']
            dest_metar_zt = bulk_flight_deets['dest_weather']['METAR_zt']
            dest_taf_zt = bulk_flight_deets['dest_weather']['TAF_zt']
            bulk_flight_deets['dest_datis_zt']= dest_datis_zt
            bulk_flight_deets['dest_metar_zt']= dest_metar_zt
            bulk_flight_deets['dest_taf_zt']= dest_taf_zt
            
        nested_weather_dict_explosion()
        return bulk_flight_deets
    
    bulk_flight_deets = without_futures()


    """
    
    async def get_tasks(session):
        tasks = []
        for airport_id in all_datis_airports:
            url = f"https://datis.clowd.io/api/{airport_id}"
            tasks.append(asyncio.create_task(session.get(url)))
        return tasks

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = await get_tasks(session)
            # Upto here the tasks are created which is very light.

            # Actual pull work is done using as_completed 
            datis_resp = []
            for task in asyncio.as_completed(tasks):        # use .gather() instead of .as_completed for background completion
                resp = await task 
                jj = await resp.json()
                datis_raw = 'n/a'
                if type(jj) == list and 'datis' in jj[0].keys():
                    datis_raw = jj[0]['datis']
                datis_resp.append(datis_raw)
            return datis_resp

    # Works regardless of the syntax error. Not sut why its showing syntax error
    all_76_datis = await asyncio.ensure_future(main())

    
    """


    """
    # This code is the parallel processing futures implementation. 
        # It is creating issues on EC2 as of 12/21/2023. Hence it is commented out.

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures1 = executor.submit(flt_info.fs_dep_arr_timezone_pull, flight_number_query)
        futures2 = executor.submit(flt_info.fa_data_pull, airline_code, flight_number_query)
        futures_dep_des = executor.submit(flt_info.united_departure_destination_scrape, flight_number_query)
    
    results = []
    for future in as_completed([futures1,futures2, futures_dep_des]):
        results.append(future.result())
    bulk_flight_deets = {}
    for i in results:
        if 'origin' in i.keys():
            flight_aware_data_pull = i
        else:
            bulk_flight_deets.update(i)
    
    UA_departure_ID, UA_destination_ID = bulk_flight_deets['departure_ID'], bulk_flight_deets['destination_ID']

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures3 = executor.submit(weather.scrape, UA_departure_ID)
        futures4 = executor.submit(weather.scrape, UA_destination_ID)
        futures5 = executor.submit(flt_info.nas_final_packet, UA_departure_ID, UA_destination_ID) # NAS
        futures6 = executor.submit(flt_info.flight_view_gate_info, flight_number_query, UA_departure_ID) # Takes forever to load

    for future in as_completed([futures5,futures6]):
        bulk_flight_deets.update(future.result())
    bulk_flight_deets['dep_weather'] = futures3.result()
    bulk_flight_deets['dest_weather'] = futures4.result()

    fa_departure_ID, fa_destination_ID = flight_aware_data_pull['origin'], flight_aware_data_pull['destination']
    # Here associating None values for fa_data seems unnecessary. could rather use it and dump unreliable data.
    if  UA_departure_ID != fa_departure_ID and UA_destination_ID != fa_destination_ID:
        for keys in flight_aware_data_pull.keys():
            flight_aware_data_pull[keys]= None

    bulk_flight_deets.update(flight_aware_data_pull)
    """

    return render(request, 'flight_deet.html', bulk_flight_deets)


def weather_display(request,weather_query):

    weather_query = weather_query.strip()       # remove leading and trailing spaces. Seems precautionary.
    airport = weather_query[-4:]

    weather = Weather_parse()
    # TODO: Need to be able to add the ability to see the departure as well as the arrival datis
    # weather = weather.scrape(weather_query, datis_arr=True)
    weather = weather.processed_weather(weather_query, )

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
    
    print('Within dummy func views.py')
    ismail = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/"
    ujas = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\\"
    luis = r""

    currentWorking = os.getcwd() + "/dj/"
    dummy_path_to_be_used = currentWorking
    print(dummy_path_to_be_used)

    bulk_flight_deets_path = dummy_path_to_be_used + r"latest_bulk_11_30.pkl"
    bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))
    
    ind = dummy_path_to_be_used + r"raw_weather_dummy_dataKIND.pkl"
    ord = dummy_path_to_be_used + r"raw_weather_dummy_dataKORD.pkl"
    with open(ind, 'rb') as f:
        dep_weather = pickle.load(f)
    with open(ord, 'rb') as f:
        dest_weather = pickle.load(f)
    
    weather = Weather_parse()
    bulk_flight_deets['dep_weather'] = weather.processed_weather(dummy=dep_weather)
    weather = Weather_parse()
    bulk_flight_deets['dest_weather'] = weather.processed_weather(dummy=dest_weather)
    
    # These seperate out all the wather for ease of work for design. for loops are harder to work with in html
    dep_atis = bulk_flight_deets['dep_weather']['D-ATIS']
    dep_metar = bulk_flight_deets['dep_weather']['METAR']
    dep_taf = bulk_flight_deets['dep_weather']['TAF']
    bulk_flight_deets['dep_datis']= dep_atis
    bulk_flight_deets['dep_metar']= dep_metar
    bulk_flight_deets['dep_taf']= dep_taf
    dest_datis = bulk_flight_deets['dest_weather']['D-ATIS']
    dest_metar = bulk_flight_deets['dest_weather']['METAR']
    dest_taf = bulk_flight_deets['dest_weather']['TAF']
    bulk_flight_deets['dest_datis']= dest_datis
    bulk_flight_deets['dest_metar']= dest_metar
    bulk_flight_deets['dest_taf']= dest_taf
    print('Going to dummy flight_deet.html')
    return render(request, 'flight_deet.html', bulk_flight_deets)


def dummy2(request, airport):
    # This page is returned by using `ext d` in the search bar
    currentWorking = os.getcwd() + "/"
    print(currentWorking)
    print("dummy2 area")

    # Renders the page and html states it gets the data from data_v
    return(render(request, 'dummy2.html',{'airport': airport}))

    

# This function gets loaded within the dummy2 page whilst dummy2 func gets rendered.
# the fetch area in js acts as url. it will somehow get plugged into the urls.py's data_v line with the airport
# that airport then gets plugged in here. request is the WSGI thing and second argument is what you need
@require_GET
def nas_data(request, airport):

    print('within nas_data func w decorator',request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(1.5)
    
    ismail = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/"
    ujas = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\\"
    luis = r""

    currentWorking = os.getcwd() + "/dj/"
    dummy_path_to_be_used = currentWorking
    def bulk_pre_assigned():
        bulk_flight_deets_path = dummy_path_to_be_used + r"latest_bulk_11_30.pkl"
        bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))
        
        # print('OLD with html highlights', bulk_flight_deets)
        ind = dummy_path_to_be_used + r"raw_weather_dummy_dataKIND.pkl"
        ord = dummy_path_to_be_used + r"raw_weather_dummy_dataKORD.pkl"
        with open(ind, 'rb') as f:
            dep_weather = pickle.load(f)
        with open(ord, 'rb') as f:
            dest_weather = pickle.load(f)
        
        weather = Weather_parse()
        bulk_flight_deets['dep_weather'] = weather.processed_weather(dummy=dep_weather)
        weather = Weather_parse()
        bulk_flight_deets['dest_weather'] = weather.processed_weather(dummy=dest_weather)

        
        # These seperate out all the wather for ease of work for design. for loops are harder to work with in html
        def bunch():
            dep_atis = bulk_flight_deets['dep_weather']['D-ATIS']
            dep_metar = bulk_flight_deets['dep_weather']['METAR']
            dep_taf = bulk_flight_deets['dep_weather']['TAF']
            bulk_flight_deets['dep_datis']= dep_atis
            bulk_flight_deets['dep_metar']= dep_metar
            bulk_flight_deets['dep_taf']= dep_taf
            dest_datis = bulk_flight_deets['dest_weather']['D-ATIS']
            dest_metar = bulk_flight_deets['dest_weather']['METAR']
            dest_taf = bulk_flight_deets['dest_weather']['TAF']
            bulk_flight_deets['dest_datis']= dest_datis
            bulk_flight_deets['dest_metar']= dest_metar
            bulk_flight_deets['dest_taf']= dest_taf
            return bulk_flight_deets
        return bunch()


    # data_return = provide_weather()
    data_return = bulk_pre_assigned()['nas_departure_affected']
    # print(data_return.keys())
    
    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


@require_GET
def weather_data(request, airport):

    print('Inside weather_data views func',request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(2.5)

    ismail = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/"
    ujas = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\\"
    luis = r""

    currentWorking = os.getcwd() + "/dj/"
    print('CURRENT WORKING DIRECTOR', currentWorking)

    dummy_path_to_be_used = currentWorking

    def bulk_pre_assigned():
        bulk_flight_deets_path = dummy_path_to_be_used + r"latest_bulk_11_30.pkl"
        bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))
        
        # print('OLD with html highlights', bulk_flight_deets)
        ind = dummy_path_to_be_used + r"raw_weather_dummy_dataKIND.pkl"
        ord = dummy_path_to_be_used + r"raw_weather_dummy_dataKORD.pkl"
        with open(ind, 'rb') as f:
            dep_weather = pickle.load(f)
        with open(ord, 'rb') as f:
            dest_weather = pickle.load(f)
        
        weather = Weather_parse()
        bulk_flight_deets['dep_weather'] = weather.processed_weather(dummy=dep_weather)
        weather = Weather_parse()
        bulk_flight_deets['dest_weather'] = weather.processed_weather(dummy=dest_weather)

        # These seperate out all the wather for ease of work for design. for loops are harder to work with in html
        def bunch():
            dep_atis = bulk_flight_deets['dep_weather']['D-ATIS']
            dep_metar = bulk_flight_deets['dep_weather']['METAR']
            dep_taf = bulk_flight_deets['dep_weather']['TAF']
            bulk_flight_deets['dep_datis']= dep_atis
            bulk_flight_deets['dep_metar']= dep_metar
            bulk_flight_deets['dep_taf']= dep_taf
            
            dest_datis = bulk_flight_deets['dest_weather']['D-ATIS']
            dest_metar = bulk_flight_deets['dest_weather']['METAR']
            dest_taf = bulk_flight_deets['dest_weather']['TAF']
            bulk_flight_deets['dest_datis']= dest_datis
            bulk_flight_deets['dest_metar']= dest_metar
            bulk_flight_deets['dest_taf']= dest_taf



            weather_extracts = {}
            weather_extracts['dep_weather'] = {'D-ATIS': [bulk_flight_deets['dep_weather']['D-ATIS_zt'], bulk_flight_deets['dep_datis']]}
            weather_extracts['dep_weather'].update({'METAR': [bulk_flight_deets['dep_weather']['METAR_zt'], bulk_flight_deets['dep_metar'],]})
            weather_extracts['dep_weather'].update({'TAF': [bulk_flight_deets['dep_weather']['TAF_zt'], bulk_flight_deets['dep_taf']]})

            weather_extracts['dest_weather'] = bulk_flight_deets['dest_weather']
            # print(weather_extracts['dep_weather'])
            return weather_extracts


        return bunch()


    def provide_weather():
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
    
    # data_return = provide_weather()
    data_return = bulk_pre_assigned()
    # print(data_return.keys())
    
    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


@require_GET
def summary_box(request, airport):

    print('Insidee summary_box func',request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(5)

    ismail = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/"
    ujas = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\\"
    luis = r""

    currentWorking = os.getcwd() + "/dj/"
    dummy_path_to_be_used = currentWorking

    def bulk_pre_assigned():
        bulk_flight_deets_path = dummy_path_to_be_used + r"latest_bulk_11_30.pkl"
        bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))
        
        # print('OLD with html highlights', bulk_flight_deets)
        ind = dummy_path_to_be_used + r"raw_weather_dummy_dataKIND.pkl"
        ord = dummy_path_to_be_used + r"raw_weather_dummy_dataKORD.pkl"
        with open(ind, 'rb') as f:
            dep_weather = pickle.load(f)
        with open(ord, 'rb') as f:
            dest_weather = pickle.load(f)
        
        weather = Weather_parse()
        bulk_flight_deets['dep_weather'] = weather.processed_weather(dummy=dep_weather)
        weather = Weather_parse()
        bulk_flight_deets['dest_weather'] = weather.processed_weather(dummy=dest_weather)
        
        return bulk_flight_deets
        
        # These seperate out all the wather for ease of work for design. for loops are harder to work with in html

    # data_return = provide_weather()
    data_return = bulk_pre_assigned()
    print(data_return.keys())
    
    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


@require_GET
def data_v(request, airport):

    print('within data_v',request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(1)

    ismail = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/"
    ujas = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\\"
    luis = r""

    currentWorking = os.getcwd() + "/dj/"
    dummy_path_to_be_used = currentWorking
    
    def bulk_pre_assigned():
        bulk_flight_deets_path = dummy_path_to_be_used + r"latest_bulk_11_30.pkl"
        bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))
        
        # print('OLD with html highlights', bulk_flight_deets)
        ind = dummy_path_to_be_used + r"raw_weather_dummy_dataKIND.pkl"
        ord = dummy_path_to_be_used + r"raw_weather_dummy_dataKORD.pkl"
        with open(ind, 'rb') as f:
            dep_weather = pickle.load(f)
        with open(ord, 'rb') as f:
            dest_weather = pickle.load(f)
        
        weather = Weather_parse()
        bulk_flight_deets['dep_weather'] = weather.processed_weather(dummy=dep_weather)
        weather = Weather_parse()
        bulk_flight_deets['dest_weather'] = weather.processed_weather(dummy=dest_weather)

        # These seperate out all the wather for ease of work for design. for loops are harder to work with in html
        def bunch():
            dep_atis = bulk_flight_deets['dep_weather']['D-ATIS']
            dep_metar = bulk_flight_deets['dep_weather']['METAR']
            dep_taf = bulk_flight_deets['dep_weather']['TAF']
            bulk_flight_deets['dep_datis']= dep_atis
            bulk_flight_deets['dep_metar']= dep_metar
            bulk_flight_deets['dep_taf']= dep_taf
            dest_datis = bulk_flight_deets['dest_weather']['D-ATIS']
            dest_metar = bulk_flight_deets['dest_weather']['METAR']
            dest_taf = bulk_flight_deets['dest_weather']['TAF']
            bulk_flight_deets['dest_datis']= dest_datis
            bulk_flight_deets['dest_metar']= dest_metar
            bulk_flight_deets['dest_taf']= dest_taf
            return bulk_flight_deets
        return bunch()


    def provide_weather():
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
    
    # data_return = provide_weather()
    data_return = bulk_pre_assigned()
    # print(data_return.keys())
    
    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


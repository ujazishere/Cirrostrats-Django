import pickle
import asyncio
from django.views.decorators.http import require_GET
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.shortcuts import render
from django.http import HttpResponse
from .root.gate_checker import Gate_checker
from .root.root_class import Root_class
from .root.gate_scrape import Gate_scrape_thread
from .root.MET_TAF_parse import Metar_taf_parse
from .root.dep_des import Pull_flight_info
from time import sleep
from django.shortcuts import render
from django.http import JsonResponse
import smtplib

'''
views.py runs as soon as the base web is requested. Hence, GateCheckerThread() is run in the background right away.
It will then run 
'''

# TODO: move this out so EC2 deployment is is streamlined without having to change this everytime
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
        # Make it such that the duplicates are grouped using maybe unique.
        # search_query = SearchQuery(query=main_query)      # Adds search queries to the database
        # search_query.save()       # you've got to save it otherwise it wont save

        # This bit will send an email notification with the query. Catered for EC2 deployment only!
        # For this to work on google you have to switch on two factor auth
            # You also need to go into the security--> 2factor auth--> app password and generate password for it  
        if run_lengthy_web_scrape:
            Root_class().send_email(body_to_send=main_query)
        return parse_query(request, main_query)

    else:
        return render(request, 'home.html')


def parse_query(request, main_query):
    main_query = main_query
    query_in_list_form = []     # Global variable since it is used outside of the if statement in case it was not triggered. purpose: Handeling Error
                                    # if .split() method is used outside here it can return since empty strings cannot be split.
                                    
    if main_query == '':        # query is empty then return all gates
        print('Empty query: Inside just prior to the gate_info func')
        return gate_info(request, main_query='')
    if 'DUMM' in main_query.upper():
        return dummy(request)
    if main_query == 'ext d':
        return dummy2(request)
    
    if main_query != '':
        query_in_list_form = main_query.split()
        if len(query_in_list_form) == 1:            # If query is only one word or item  
            query = query_in_list_form[0].upper()           # this is string form instead of list
            if query[:2] == 'UA' or query[:3] == 'GJS':         # Accounting for flight number query with leads 
                airline_code = None         
                if query[0] == 'G':
                    airline_code, flgiht_digits = query[:3], query[3:]          # Its GJS
                else:
                    flgiht_digits = query[2:]       # Its UA
                print('\nSearching for:', airline_code,flgiht_digits)
                return flight_deets(request, airline_code=airline_code,flight_number_query=flgiht_digits)
            elif 'A' in query or 'B' in query or 'C' in query or len(query) == 1:     # Accounting for 1 letter only. Gate query.
                # When the length of query_in_list_form is only 1 it returns gates table for that particular query.
                gate_query = query
                return gate_info(request, main_query=gate_query)
            elif len(query) == 4 or len(query) == 3 or len(query) == 2:
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
                        return metar_display(request, weather_query_airport)
                    else:    
                        print('impossible gate query return')
                        Root_class().send_email(body_to_send=f"impossible gate query return: `{main_query}`")
                        return gate_info(request, main_query=str(query))
            else:
                gate_query = query
                return gate_info(request, main_query=gate_query)


    if len(query_in_list_form) > 1:
        first_letter = query_in_list_form[0].upper()        # Making it uppercase for compatibility issues and error handling
        if first_letter == 'W':
            weather_query_airport  = query_in_list_form[1]
            weather_query_airport = weather_query_airport.upper()       # Making query uppercase for it to be compatible
            return metar_display(request, weather_query_airport)

        if first_letter == 'I':        
            return flight_deets(request,airline_code=None,query_in_list_form=query_in_list_form)
        else:       # If the query is not recognized:
            return gate_info(request, main_query=main_query)
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


def dummy(request):

    try:
        bulk_flight_deets_path = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\latest_bulk_11_30.pkl"
        bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))
    except:
        bulk_flight_deets = pickle.load(open(r'/Users/ismailsakhani/Desktop/Cirrostrats/dj/latest_bulk_11_30.pkl', 'rb'))
    
    # print('OLD with html highlights', bulk_flight_deets)
    try: # UJ PC PATH
        ind = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\raw_weather_dummy_dataKIND.pkl"
        ord = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\raw_weather_dummy_dataKORD.pkl"
        with open(ind, 'rb') as f:
            dep_weather = pickle.load(f)
        with open(ord, 'rb') as f:
            dest_weather = pickle.load(f)
        
        weather = Metar_taf_parse()
        bulk_flight_deets['dep_weather'] = weather.scrape(dummy=dep_weather)
        weather = Metar_taf_parse()
        bulk_flight_deets['dest_weather'] = weather.scrape(dummy=dest_weather)

    except Exception as e:     # ISMAIL MAC PATH
        print(e)
        is_ind = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/raw_weather_dummy_dataKIND.pkl"
        is_ord = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/raw_weather_dummy_dataKORD.pkl"
        with open(is_ind, 'rb') as f:
            dep_weather = pickle.load(f)
        with open(is_ord, 'rb') as f:
            dest_weather = pickle.load(f)
        weather = Metar_taf_parse()
        bulk_flight_deets['dep_weather'] = weather.scrape(dummy=dep_weather)
        weather = Metar_taf_parse()
        bulk_flight_deets['dest_weather'] = weather.scrape(dummy=dest_weather)
    
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
    return render(request, 'flight_deet.html', bulk_flight_deets)


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
    else:       # Returns all gates since query is empty. Maybe this is not necessary. Try deleting else statement.
        return render(request, 'flight_info.html', {'gate': gate})


def flight_deets(request,airline_code=None, flight_number_query=None, bypass_fa=False):
    
    bypass_fa = False

    flt_info = Pull_flight_info()           # from dep_des.py file
    weather = Metar_taf_parse()         # from MET_TAF_parse.py
    
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
        bulk_flight_deets['dep_weather'] = weather.scrape(UA_departure_ID)
        # datis_arr as true in this case since its for the destination/arr datis.
        bulk_flight_deets['dest_weather'] = weather.scrape(UA_destination_ID,datis_arr=None)
        print(bulk_flight_deets['dep_weather'])
        bulk_flight_deets.update(flt_info.nas_final_packet(UA_departure_ID, UA_destination_ID))
        bulk_flight_deets.update(flt_info.flight_view_gate_info(flight_number_query, UA_departure_ID))
        
        # This whole area removes the need for for loop in html making it easier to 
            # work with css styling and readibility.
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
    
    bulk_flight_deets = without_futures()
    # """

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

    # Extracting metar for a dummy file
    # with open('latest_bulk_11_28.pkl', 'wb') as f:
        # print("**DUMPING BULK_FLIGHT_DEETS AS latest_bulk PKL FILE**")
        # pickle.dump(bulk_flight_deets, f)
    # extracting metar for a dummy file
    # with open('lifr.pkl', 'wb') as f:
        # pickle.dump(bulk_flight_deets, f)
    
    return render(request, 'flight_deet.html', bulk_flight_deets)


def metar_display(request,weather_query):
    
    weather_query = weather_query.strip()       # remove leading and trailing spaces. Seems precautionary.
    airport = weather_query[-4:]
    
    weather = Metar_taf_parse()
    # TODO: Need to be able to add the ability to see the departure as well as the arrival datis
    # weather = weather.scrape(weather_query, datis_arr=True)
    weather = weather.scrape(weather_query, )
    
    weather_page_data = {}
    
    weather_page_data['airport'] = airport
    weather_page_data['datis'] = weather['D-ATIS']
    weather_page_data['metar'] = weather['METAR']
    weather_page_data['taf'] = weather['TAF']
    
    return render(request, 'metar_info.html', weather_page_data)


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

def dummy2(request):
    # This page is returned by using `ext d` in the search bar
    print("dummy2 area")
    # Renders the page and html states it gets the data from data_v
    return(render(request, 'dummy2.html'))
    


# This function gets loaded within the dummy2 page whilst dummy2 func gets rendered.
@require_GET
def data_v(request):        
    
    sleep(0.9)
    try:
        bulk_flight_deets_path = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\latest_bulk_11_30.pkl"
        bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))
    except:
        bulk_flight_deets = pickle.load(open('/Users/ismailsakhani/Desktop/Cirrostrats/dj/latest_bulk_11_30.pkl', 'rb'))
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
    for a, b in bulk_flight_deets.items():
        print(a,type(b))
        if a=='registration':
            print(b)
    return JsonResponse(bulk_flight_deets)
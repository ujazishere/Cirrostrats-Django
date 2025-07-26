# quick code for jupyter
# from dj.dj_app.views import awc_weather
# await awc_weather(None,"EWR","STL")
from .root.process_query import airlineCodeQueryParse
import pickle
from django.views.decorators.http import require_GET
# from concurrent.futures import ThreadPoolExecutor, as_completed           # Causing issues on AWS
from django.shortcuts import render
from django.http import HttpResponse
from .root.test_data_imports import test_data_imports
from .root.gate_checker import Gate_checker
from .root.root_class import Root_class, Pull_class, Source_links_and_api
from .root.weather_parse import Weather_parse
from .root.dep_des import Pull_flight_info
from .root.flight_deets_pre_processor import resp_initial_returns,resp_sec_returns,response_filter
from time import sleep, time
from decouple import config
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
import asyncio

import re
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
run_lengthy_web_scrape = True if config("run_lengthy_web_scrape") == '1' else False

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

        # print(1)
        # TODO: This await line is for testing locally if the email deal works. get rid of it before you push and incluse ismail's email.com
        # Canot await this smtp item for send mail. use aiosmtplib library for it
        # await Root_class().send_email(body_to_send=main_query)
        # print(3)
        # actual
        if run_lengthy_web_scrape:
            Root_class().send_email(body_to_send=main_query)
        return await QueryParser(request, main_query)

    else:
        return render(request, 'home.html')


async def QueryParser(request, main_query):
    """
    Checkout note `unit testing seems crucial.txt` for the parsing logic
    """

    # Global variable since it is used outside of the if statement in case it was not triggered. purpose: Handeling Error
    query_in_list_form = []
    # if .split() method is used outside here it can return since empty strings cannot be split.

    if 'DUMM' in main_query.upper():
        print('returning dummy')
        return dummy(request)
    
    if main_query == '':        #TODO 10/19/2024: Empty query should not be possible. It shouldn't be clicked.
        print('Empty query')
        return gate_info(request, main_query='')
    elif main_query != '':
        # splits query. Necessary operation to avoid complexity. Its a quick fix for a deeper more wider issue.
        query_in_list_form = main_query.split()

        # TODO: Log the extent of query reach deep within this code, also log its occurrances to find impossible statements and frequent searches.
        # If query is only one word or item. else statement for more than 1 is outside of this indent. bring it in as an elif statement to this if.
        if len(query_in_list_form) == 1:
            
            # this is string form instead of list
            one_word_query = query_in_list_form[0].upper()
            # Accounting for flight number query with leading alphabets
            if one_word_query.startswith(('UA', 'UAL', 'GJS')):
                airline_code, flt_digits = airlineCodeQueryParse(one_word_query)
                print('\nSearching for:', airline_code, flt_digits)
                return await flight_deets(request, airline_code=airline_code, flight_number_query=flt_digits)

            # flight or gate info page returns
            elif len(one_word_query) in (2,3,4):
                if one_word_query.isdigit():
                    digit_query = int(one_word_query)
                    # TODO 10/29/24: Following needs to be depricated. search and drop down should exist for this in react.
                    if 1 <= digit_query <= 35 or 40 <= digit_query <= 136:      # Accounting for EWR gates for gate query
                        print('Newark gate query')
                        return gate_info(request, main_query=str(digit_query))
                    else:   # if this digit is not an EWR gate it is a all digit flight number query
                        airline_code, flt_digits = airlineCodeQueryParse("UA" + one_word_query)
                        print('\nSearching digits only:', airline_code, flt_digits)
                        return await flight_deets(request, airline_code=airline_code, flight_number_query=flt_digits)
                else:
                    if len(one_word_query) == 4 and one_word_query.isalpha():       # TODO: Dangerous. wont show airport with digits in it.
                        if one_word_query[0] == 'K' or one_word_query[0] == 'C':
                            weather_query_airport = one_word_query
                            # Making query uppercase for it to be compatible
                            weather_query_airport = weather_query_airport.upper()
                            return weather_info(request, weather_query_airport)
                        else:
                            return gate_info(request, main_query=str(one_word_query))
                    else:           # tpical gate query with length of 2-4 alphanumerics
                        return gate_info(request, main_query=str(one_word_query))
            # Accounting for 1 letter only. Gate query.
            elif 'A' in one_word_query or 'B' in one_word_query or 'C' in one_word_query or len(one_word_query) == 1:
                # When the length of query_in_list_form is only 1 it returns gates table for that particular query.
                gate_query = one_word_query
                print('terminal query with either A,B,C or length of 1')
                return gate_info(request, main_query=gate_query)
            else:   # return gate
                gate_query = one_word_query
                print('returning gate query final')
                # return gate_info(request, main_query=gate_query)
        else:
            return gate_info(request, main_query='')


def gate_info(request, main_query):
    
    gc = Gate_checker()
    gate = main_query.upper()
    flight_rows = gc.ewr_gate_query(gate=gate)
    # Assuming flight_rows is a list of dictionaries
    for flight in flight_rows:
        scheduled = datetime.strptime(flight['Scheduled'], '%B %d, %Y %H:%M')
        flight['Scheduled'] = scheduled.strftime('%B %d %H:%M')
    return render(request, 'flight_info.html', {'gate_data_table': flight_rows, 'gate': gate})


async def flight_deets(request,airline_code=None, flight_number_query=None, ):
    # TODO COMMENT OUT OR DELETE bypass_fa LINE WHEN MAKING THE COMMIT
    bypass_fa = not run_lengthy_web_scrape      # when run_lengthy_web_scrape is on this is False activating flight_aware fetch.
    # bypass_fa = False        # To fetch and use flight_aware_data make this False. API intensive.
    bulk_flight_deets = {}

    sl = Source_links_and_api()
    pc = Pull_class(airline_code=airline_code,flt_num=flight_number_query)
    
    # If flightaware is to be bypassed this code will remove the flightaware link
    links = [sl.flight_stats_url(flight_number_query)]
    if not bypass_fa:
        links.append(sl.flight_aware_w_auth(airline_code, flight_number_query))
    
    # First async pull and processing.
    try: 
        resp_dict = await pc.async_pull(links)          # Actual fetching happens here.
    except Exception as e:
        Root_class.send_email(body_to_send=str(f' Error in Django async_pull: {e}'))
        resp_dict = None
    resp_initial = resp_initial_returns(resp_dict=resp_dict, airline_code=airline_code, flight_number_query=flight_number_query)

    print('DONE WITH resp_initial_returns: ')
    # TODO: fix a better fix here. This was just a quick fix.
    # This origin and destination is from flight_stats since it was not found through flight_aware or united_dep_dest. This is just a temperory fix.
    united_dep_dest, flight_stats_arr_dep_time_zone, fa_data = resp_initial
    if not united_dep_dest:
        united_dep_dest = {}
        if flight_stats_arr_dep_time_zone:
            united_dep_dest['departure_ID'], united_dep_dest['destination_ID'] = flight_stats_arr_dep_time_zone.get('flightStatsOrigin'), flight_stats_arr_dep_time_zone.get('flightStatsDestination')
        print("No united_dep_des! Making fs origin and destination as United_dep_des",united_dep_dest)
    elif united_dep_dest['departure_ID'] == None:
        print('No Departure ID')
        if flight_stats_arr_dep_time_zone:
            united_dep_dest['departure_ID'], united_dep_dest['destination_ID'] = flight_stats_arr_dep_time_zone.get('flightStatsOrigin'), flight_stats_arr_dep_time_zone.get('flightStatsDestination')

    # Second async pull and processing
    if fa_data['origin']:
        origin, destination = fa_data['origin'], fa_data['destination']
    elif united_dep_dest and united_dep_dest.get('departure_ID'):
        origin, destination = united_dep_dest['departure_ID'], united_dep_dest['destination_ID']
    else:
        bulk_flight_deets = {**united_dep_dest, **fa_data}
        if flight_stats_arr_dep_time_zone:
            bulk_flight_deets.update(flight_stats_arr_dep_time_zone)
        return render(request, 'flight_deet.html', bulk_flight_deets)

    pc = Pull_class(flight_number_query, origin, destination)
    wl_dict = pc.weather_links(origin, destination)
    try:
        resp_dict = await pc.async_pull(list(wl_dict.values()) + [sl.nas()])
    except Exception as e:
        Root_class.send_email(body_to_send=str(f' Error in Django secondary async_pull: {e}'))
        resp_dict = None

    # Process weather and NAS info synchronously
    resp_sec = resp_sec_returns(resp_dict, origin, destination)
    weather_dict = resp_sec

    # Get gate info synchronously
    try:
        gate_returns = await asyncio.to_thread(Pull_flight_info().flight_view_gate_info, flt_num=flight_number_query, departure_airport=origin)
    except Exception as e:
        Root_class.send_email(body_to_send=str(f' Error in Django flight_view_gate_info: {e}'))

    bulk_flight_deets = {**united_dep_dest, **flight_stats_arr_dep_time_zone, 
                        **weather_dict, **fa_data, **gate_returns}
    return render(request, 'flight_deet.html', bulk_flight_deets)


async def ua_dep_dest_flight_status(request,flight_number):     # dep and destination id pull
    pc = Pull_class(flt_num=flight_number)
    sl = Source_links_and_api()
    flt_info = Pull_flight_info()
    
    link = sl.ua_dep_dest_flight_status(flight_number)
    resp_dict:dict = await pc.async_pull([link])

    resp = response_filter(resp_dict,"flight-status.com")
    united_dep_dest = flt_info.united_departure_destination_scrape(pre_process=resp)

    return united_dep_dest


async def flight_stats_url(request,flight_number):      # time zone pull
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


async def awc_and_nas(request, departure_id,destination_id):
    # Only for use on fastapi w react. Temporary! read below
    # this is a temporary fix to not change resp_sec_returns. clean that codebase when able
    # the separated funcs nas and awc are the ones that need to be done.

    pc = Pull_class()
    sl = Source_links_and_api()
    wp = Weather_parse()
    
    # This is  to be used if using separate functions. This is an attempt to reduce code duplication.
    # link = sl.awc_weather(metar_or_taf="metar",airport_id=airport_id)
    # resp = response_filter(resp_dict,"awc",)


    wl_dict = sl.weather_links(departure_id,destination_id)

    resp_dict:dict = await pc.async_pull(list(wl_dict.values()))
    resp_sec = resp_sec_returns(resp_dict,departure_id,destination_id) 
    weather_dict = resp_sec

    return weather_dict

async def awc_weather(request, departure_id,destination_id):

    pc = Pull_class()
    sl = Source_links_and_api()
    wp = Weather_parse()
    
    # This is  to be used if using separate functions. This is an attempt to reduce code duplication.
    # link = sl.awc_weather(metar_or_taf="metar",airport_id=airport_id)
    # resp = response_filter(resp_dict,"awc",)


    wl_dict = sl.weather_links(departure_id,destination_id)

    resp_dict:dict = await pc.async_pull(list(wl_dict.values()))
    resp_sec = resp_sec_returns(resp_dict,departure_id,destination_id) 
    weather_dict = resp_sec

    return weather_dict



async def nas(request, departure_id,destination_id):

    # Probably wont work. If it doesnt its probably because of the reesp_sec_returns
    # does not account for just nas instead going whole mile to get and process weather(unnecessary)
    pc = Pull_class()
    sl = Source_links_and_api()
    
    resp_dict:dict = await pc.async_pull([sl.nas])
    resp_sec = resp_sec_returns(resp_dict,departure_id,destination_id) 
    nas_returns = resp_sec

    return nas_returns















# TODO: GET RID OF THIS!! ITS NOT NECESSARY. ITS NOT USING ASYN CAPABILITY. ACCOUNT FOR WEATHER PULL THROUGH ONE FUNCTION
            # REDUCE CODE DUPLICATION. THIS IS FEEDING INTO ITS OWN WEATHER.HTML FILE
            # RATHER, HAVE IT SUCH THAT IT wewatherData.js takes this function.
            # 
def weather_info(request, weather_query):

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

    weather_and_nas_packet = weather_page_data
    pfi = Pull_flight_info()
    nas_affected = pfi.nas_final_packet(dep_ID=airport,dest_ID="")

    weather_and_nas_packet['nas_departure_affected'] = nas_affected['nas_departure_affected']
    print("\nWithin weather_display and NAS is ...", weather_and_nas_packet['nas_departure_affected'])
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
    test_data_imports_tuple = test_data_imports()

    bulk_flight_deets = test_data_imports_tuple[0]
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

    print('within nas_data func w decorator', request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(0.5)

    test_data_imports_tuple = test_data_imports()
    bulk_flight_deets = test_data_imports_tuple[0]

    data_return = bulk_flight_deets['nas_departure_affected']
    # print(data_return.keys())

    # return render(request, 'weather_info.html')
    return JsonResponse(data_return)


@require_GET
def weather_data(request, airport):

    print('Inside weather_data views func', request, airport)
    airport = 'KEWR'        # declaring it regardless
    sleep(1)
    
    test_data_imports_tuple = test_data_imports()
    bulk_flight_deets = test_data_imports_tuple[0]

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

    test_data_imports_tuple = test_data_imports()
    bulk_flight_deets = test_data_imports_tuple[0]

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
    bulk_flight_deets = test_data_imports()

    # return render(request, 'weather_info.html')
    return JsonResponse(bulk_flight_deets)

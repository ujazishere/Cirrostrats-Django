import pickle
# quick code for jupyter
# from dj.dj_app.views import awc_weather
# await awc_weather(None,"EWR","STL")
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
    bulk_flight_deets = {'departure_ID': 'KORD', 'destination_ID': 'KMEM', 'flight_number': 'UA4399', 'scheduled_departure_time': '14:25 CDT', 'scheduled_arrival_time': '16:14 CDT', 'dep_metar': 'KORD 311751Z 11006KT 10SM SCT090 BKN250 11/03 <span class="box_around_text">A2994</span> RMK AO2 SLP143 T01110028 10111 20039 58017 $\n', 'dep_datis': 'ORD <span class="box_around_text">ATIS INFO E</span> 1751Z. 11006KT 10SM SCT090 BKN250 11/03 <span class="box_around_text">A2994</span> (TWO NINER NINER FOUR) RMK AO2 SLP143 10111 20039 58017. ARR EXP VECTORS <span class="box_around_text">ILS RWY 10C APCH, VISUAL APCH RWY 9L, VISUAL APCH RWY 10R.</span> PILOTS EXP 2 INTCP THE <span class="box_around_text">ILS Y RY 10R FNA CRS. SIMUL APCHS IN USE.</span> READBACK ALL RWY HOLD SHORT INSTRUCTIONS. DEPS EXP RWYS 9C FROM F F 9200 FT AVL, 10L FROM DD. 10,093 FT AVBL. ATTN PILOTS. <span class="box_around_text">SIMUL PARL DEPS IN USE.</span> EXP TO INITIALLY FLY RWY. HDG ON DEP. PILOTS MUST READ BACK DRCTN OF TURNS BY ATC.. RWY 4L, 22R CLSD. PILOTS USE CTN FOR BIRD ACTIVITY IN THE VICINITY OF THE ARPT. USE CAUTION FOR MEN AND EQUIP AT NUMEROUS SITES ON THE FIELD. WHEN READY TO TAXI CONTACT GND METERING ON FREQ 121.67. ...ADVS YOU HAVE INFO E.', 'dep_taf': 'KORD 311720Z 3118/0124 07008KT P6SM FEW020 SCT100 \n  <br>\xa0\xa0\xa0\xa0FM312300 05011KT 6SM -RA SCT015 OVC035 \n  TEMPO 0101/0104 <span class="red_text_color">2SM</span> TSRA BR <span class="red_text_color">BKN007</span> <span class="yellow_highlight">OVC015</span>CB \n  <br>\xa0\xa0\xa0\xa0FM010400 04011G17KT 5SM -SHRA BR <span class="red_text_color">OVC006</span> \n  <br>\xa0\xa0\xa0\xa0FM011100 04012G18KT P6SM SCT008 <span class="yellow_highlight">OVC012</span> \n  <br>\xa0\xa0\xa0\xa0FM011800 04012G18KT 6SM -SHRA <span class="red_text_color">BKN008</span> <span class="yellow_highlight">OVC012</span> \n  PROB30 0120/0124 <span class="red_text_color">2SM</span> TSRA BR <span class="red_text_color">OVC008</span>CB\n', 'dep_metar_zt': '37 mins ago', 'dep_datis_zt': '37 mins ago', 'dep_taf_zt': '68 mins ago', 'dest_datis': 'MEM <span class="box_around_text">ATIS INFO J</span> 1754Z. 21012G21KT 10SM FEW037 BKN050 23/15 <span class="box_around_text">A2995</span> (TWO NINER NINER FIVE) RMK AO2 SLP138 10239 20161 58013. SIMUL VISUAL APCHS IN USE RY 18L, 18R, 27. SIMUL DEPS IN USE RY 18R 18C 18L. 18L. TWY K BTN TERMINAL RAMP AND TWY C CLSD. TWY J NORTH 1000 FOOT CLSD. RY 18L, 36R PAPI OTS. RWY 36C ALS NOT MONITORED. BIRD ACTIVITY RPTD IN THE VC OF THE ARPT. READBACK ALL RWY HOLD SHORT INSTRUCTIONS. CONSOLIDATED WAKE TURBULENCE . STANDARDS IN EFFECT. AT GATES 18, 20, 22, 23, 40 CTC GC FOR PUSHBACK.. ...ADVS YOU HAVE INFO J.', 'dest_metar': 'KMEM 311754Z 21012G21KT 10SM FEW037 BKN050 23/15 <span class="box_around_text">A2995</span> RMK AO2 SLP138 T02280150 10239 20161 58013 $\n', 'dest_taf': 'KMEM 311738Z 3118/0124 21012G22KT P6SM SCT035 BKN060 \n  <br>\xa0\xa0\xa0\xa0FM312300 21010G18KT P6SM BKN060 OVC200 \n  <br>\xa0\xa0\xa0\xa0FM010300 20011G20KT P6SM BKN070 OVC150 WS020/22045KT \n  <br>\xa0\xa0\xa0\xa0FM011300 20012G20KT P6SM FEW015 BKN022 \n  TEMPO 0113/0116 <span class="yellow_highlight">BKN015</span> \n  <br>\xa0\xa0\xa0\xa0FM011800 21013G22KT P6SM BKN035\n', 'dest_datis_zt': '34 mins ago', 'dest_metar_zt': '34 mins ago', 'dest_taf_zt': '50 mins ago', 'departure_gate': '\n2 - F11\n', 'arrival_gate': '\n13\n', 'nas_departure_affected': {}, 'nas_destination_affected': {}, 'origin': 'KORD', 'destination': 'KMEM', 'registration': 'N578GJ', 'scheduled_out': '1925Z', 'estimated_out': '1925Z', 'scheduled_in': '2114Z', 'estimated_in': '2125Z', 'terminal_origin': '2', 'terminal_destination': None, 'gate_origin': 'F11', 'gate_destination': '13', 'filed_altitude': 'FL360', 'filed_ete': 6000, 'route': 'CMSKY CARYN CYBIL PXV WLDER1', 'sv': 'https://skyvector.com/?fpl=%20KORD%20CMSKY%20CARYN%20CYBIL%20PXV%20WLDER1%20KMEM'}
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

    print('within nas_data func w decorator', request, airport)
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

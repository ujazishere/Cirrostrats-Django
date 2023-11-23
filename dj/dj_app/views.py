import pickle
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.shortcuts import render
from django.http import HttpResponse
from .models import SearchQuery
from .root.gate_checker import Gate_checker
from .root.gate_scrape import Gate_scrape_thread
from .root.MET_TAF_parse import Weather_display
from .root.dep_des import Pull_flight_info
from time import sleep
from django.shortcuts import render
from django.http import JsonResponse

run_lengthy_web_scrape = False

if run_lengthy_web_scrape:
    print('Running Lengthy web scrape')
    gc_thread = Gate_scrape_thread()
    gc_thread.start()

current_time = Gate_checker().date_time()


async def home(request):
    if request.method == "POST":
        main_query = request.POST.get('query', '')
        return  parse_query(request, main_query)
    else:
        return render(request, 'home.html')


def parse_query(request, main_query):
    main_query = main_query
    query_in_list_form = []

    if main_query == '':
        return gate_info(request, main_query='')
    if 'DUMM' in main_query.upper():
        return dummy(request)
    if main_query == 'ext d':
        return dummy2(request)
    
    if main_query != '':
        query_in_list_form = main_query.split()
        if len(query_in_list_form) == 1:
            query = query_in_list_form[0].upper()
            if query[:2] == 'UA':
                flight_initials = query[:2]
                flgiht_digits = query[2:]
                return flight_deets(request, flgiht_digits)
            elif 'A' in query or 'B' in query or 'C' in query or len(query) == 1:
                gate_query = query
                return gate_info(request, main_query=gate_query)
            elif len(query) == 4 or len(query) == 3 or len(query) == 2:
                if query.isdigit():
                    query = int(query)
                    if 1 <= query <= 35 or 40 <= query <= 136:
                        return gate_info(request, main_query=str(query))
                    else:
                        return flight_deets(request, query)
                else:
                    return gate_info(request, main_query=str(query))

    if len(query_in_list_form) > 1:
        first_letter = query_in_list_form[0].upper()
        if first_letter == 'W':
            weather_query_airport = query_in_list_form[1]
            weather_query_airport = weather_query_airport.upper()
            return metar_display(request, weather_query_airport)

        if first_letter == 'I':
            return flight_deets(request, query_in_list_form)
        else:
            return gate_info(request, main_query=main_query)


def dummy(request):
    try:
        bulk_flight_deets = pickle.load(open('dummy_flight_deet.pkl', 'rb'))
    except:
        bulk_flight_deets = pickle.load(open('/Users/ismailsakhani/Desktop/Cirrostrats/dj/dummy_flight_deet.pkl', 'rb'))
    print(bulk_flight_deets)
    return render(request, 'flight_deet.html', bulk_flight_deets)


def gate_info(request, main_query):
    gate = main_query
    gate = gate.upper()

    current_time = Gate_checker().date_time()
    gate_data_table = Gate_checker().ewr_UA_gate(gate)

    if gate_data_table:
        return render(request, 'flight_info.html',
                      {'gate_data_table': gate_data_table, 'gate': gate, 'current_time': current_time})
    else:
        return render(request, 'flight_info.html', {'gate': gate})


async def flight_deets(request, query):
    print(query)
    flt_info = Pull_flight_info()
    weather = Weather_display()

    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures1 = loop.run_in_executor(executor, flt_info.pull_UA, query)
        futures2 = loop.run_in_executor(executor, flt_info.flight_aware_data, query)
        futures_dep_des = loop.run_in_executor(executor, flt_info.united_flight_status_info_scrape, query)

    results = await asyncio.gather(futures1, futures2, futures_dep_des)
    bulk_flight_deets = {}
    for i in results:
        if 'origin' in i.keys():
            flight_aware_data_pull = i
        else:
            bulk_flight_deets.update(i)

    departure_ID, destination_ID = bulk_flight_deets['departure_ID'], bulk_flight_deets['destination_ID']
    fa_departure_ID, fa_destination_ID = flight_aware_data_pull['origin'], flight_aware_data_pull['destination']

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures3 = loop.run_in_executor(executor, weather.scrape, departure_ID)
        futures4 = loop.run_in_executor(executor, weather.scrape, destination_ID)
        futures5 = loop.run_in_executor(executor, flt_info.gs_sorting, departure_ID, destination_ID)
        futures6 = loop.run_in_executor(executor, flt_info.pull_dep_des, query, departure_ID)

    additional_results = await asyncio.gather(futures5, futures6)
    for result in additional_results:
        bulk_flight_deets.update(result)

    bulk_flight_deets['dep_weather'] = await loop.run_in_executor(None, futures3.result)
    bulk_flight_deets['dest_weather'] = await loop.run_in_executor(None, futures4.result)

    if departure_ID != fa_departure_ID and destination_ID != fa_destination_ID:
        for keys in flight_aware_data_pull.keys():
            flight_aware_data_pull[keys] = None

    bulk_flight_deets.update(flight_aware_data_pull)
    return render(request, 'flight_deet.html', bulk_flight_deets)



def metar_display(request, weather_query):
    weather_query = weather_query.strip()
    airport = weather_query[-4:]

    weather = Weather_display()
    weather = weather.scrape(weather_query)

    return render(request, 'metar_info.html', {'airport': airport, 'weather': weather})


# Other views remain the same

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
    
    my_dictionary = {
        'name': 'John',
        'age': 25,
        'city': 'New York',
        'occupation': 'Software Engineer',
        'is_student': False
    }

    return JsonResponse(my_dictionary)

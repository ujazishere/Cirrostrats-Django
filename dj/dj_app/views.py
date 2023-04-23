from django.shortcuts import render
from django.http import HttpResponse
from .root_gate_checker import Gate_checker, GateCheckerThread
from .root.MET_TAF_parse import Weather_display

# TODO: Deploy the ability to chat and store queries.
# TODO: When User first accesses the web the date and time of the latest master should be displayed 

'''
views.py runs as soon as the base web is requested. Hence, GateCheckerThread() is run the background right away.
It will then run 
'''
run_lengthy_web_scrape = False

if run_lengthy_web_scrape:
    gc_thread = GateCheckerThread()
    gc_thread.start()


def home(request):
    
    # Homepage first skips a "POST", goes to else and returns home.html
    
    if request.method == "POST":
        # query = request.POST.get('query','')
        # if query.upper() in:
        return parse_query(request)
    else:
        return render(request, 'home.html', {'loading': True})


def parse_query(request):
    # query is a string type. 
    query = request.POST.get('query','').upper()
    
    # Here add `and` to include digits for gate information. Maybe use unique values of gate for display.for eachgate in all unique gates if query in eachgate..

    if len(query) <= 4:
        # in this section query becomes gate and is fed into flight_into.
        gate = query
        return flight_info(request,gate)
    elif "met" in query.lower():
        weather_query = query
        return metar_display(request, weather_query)
    else:
        print(query)
        return flight_info(request, query)


def flight_info(request,gate):
    print('Getting flight infor for gate:', gate)

    # Dictionary format a list with one or many dictionaries each dictionary containing 4 items:gate,flight,scheduled,actual

    flights = Gate_checker().ewr_UA_gate(gate)
    
    # showing info if the info is found else it falls back to `No flights found for {{gate}}`on flight_info.html
    if flights: 
        print(flights)
        return render(request, 'flight_info.html',{'flights': flights, 'gate': gate})
    else:
        return render(request, 'flight_info.html', {'gate': gate})


def metar_display(request,weather_query):
    weather = Weather_display()
    weather = weather.scrape(weather_query)
    print('test1')
    airport = weather_query[-4:]
    print(airport)
    print(weather)
    return render(request, 'metar_info.html', {'airport': airport, 'weather': weather})


def about(request):
    return render(request, 'home.html')
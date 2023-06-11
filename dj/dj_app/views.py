from django.shortcuts import render
from .models import SearchQuery
from .root.gate_checker import Gate_checker
from .root.gate_scrape import Gate_scrape_thread
from .root.MET_TAF_parse import Weather_display
from .root.dep_des import Pull_flight_info
from .root.flt_deet import airports


'''
views.py runs as soon as the base web is requested. Hence, GateCheckerThread() is run the background right away.
It will then run 
'''
run_lengthy_web_scrape = False 

if run_lengthy_web_scrape:
    'Running Lengthy web scrape'
    gc_thread = Gate_scrape_thread()
    gc_thread.start()

current_time = Gate_checker().date_time()

def home(request):
    # Homepage first skips a "POST", goes to else and returns home.html since the query is not submitted yet.
    if request.method == "POST":
        main_query = request.POST.get('query','')
        
        search_query = SearchQuery(query=main_query)      # Adds search queries to the database
        search_query.save()                               # you've got to save it otherwise it wont save
        
        return parse_query(request, main_query)

    else:
        return render(request, 'home.html')


def contact(request):
    return render(request, 'contact.html')

    
def about(request):
    return render(request, 'about.html')

def source(request):
    return render(request, 'source.html')

def source(request):
    return render(request, 'gate_check.html')

def source(request):
    return render(request, 'flight_lookup.html')

def source(request):
    return render(request, 'weather.html')


def parse_query(request, main_query):
    main_query = main_query
    query_in_list_form = []     # Global variable since it is used outside of the if statement in case it was not triggered. purpose: Handeling Error
                                    # if .split() method is used outside here it can return since empty strings cannot be split.
                                    
    if main_query == '':        # query is empty then return all gates
        return gate_info(request, main_query='')
    if main_query != '':        # if query is not empty it splits it into list form
        query_in_list_form = main_query.split()
        if len(query_in_list_form) == 1:            # If query is only one word or item  

            # When the length of query_in_list_form is only 1 it returns gates table for that particular query.
            gate_query = query_in_list_form[0]
            return gate_info(request, main_query=gate_query)
    if len(query_in_list_form) > 1:
        first_letter = query_in_list_form[0].upper()        # Making it uppercase for compatibility issues and error handling
        if first_letter == 'W':
            weather_query_airport  = query_in_list_form[1]
            weather_query_airport = weather_query_airport.upper()       # Making query uppercase for it to be compatible
            return metar_display(request, weather_query_airport)
        
        if first_letter == 'I':        
            return flight_deets(request, query_in_list_form)
        
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


def gate_info(request,main_query):
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


def flight_deets(request, query_in_list_form ):
    # pull weather for a partifular flight number. 
    flt_info = Pull_flight_info()
    dep_des = flt_info.pull_dep_des(query_in_list_form)
    
    if dep_des: 
        departure = f'K{list(dep_des.values())[0][0]}'      # Turning a 3 letter airport identifier into 4 letter ICAO identifier
        destination = f'K{list(dep_des.values())[0][1]}' 
    else:
        departure = ''
        destination = ''
        
        
    def weather_req(airport):
        weather = Weather_display()
        weather = weather.scrape(airport)
        return weather
    
    if departure and destination:
        dep_weather = weather_req(departure)
        dest_weather = weather_req(destination)
        flight_query = " ".join(query_in_list_form[1] + query_in_list_form[2])
        bulk_flight_deets = {'flight_query': flight_query, 
                            'dep_des': dep_des,
                            'current_time': current_time,
                            'dep_weather': dep_weather,
                            'dest_weather': dest_weather       
                                }
        return render(request, 'flight_deet.html', bulk_flight_deets )
    else:
        return render(request, 'flight_deet.html', {'flight_query': flight_query} )
    
    # find departure and destination of this particular flight from the web.
    

def metar_display(request,weather_query):
    
    weather_query = weather_query.strip()       # remove leading and trailing spaces. Seems precautionary.
    airport = weather_query[-4:]
    
    weather = Weather_display()
    weather = weather.scrape(weather_query)
    
    return render(request, 'metar_info.html', {'airport': airport, 'weather': weather})


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


def source(request):
    return render(request, 'source.html')


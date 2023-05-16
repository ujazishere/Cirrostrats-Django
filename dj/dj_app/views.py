from django.shortcuts import render
from .root_gate_checker import Gate_checker, Gate_scrape_thread
from .root.MET_TAF_parse import Weather_display
from .root.dep_des import Pull_dep_des
from .root.flt_deet import airports


'''
views.py runs as soon as the base web is requested. Hence, GateCheckerThread() is run the background right away.
It will then run 
'''
run_lengthy_web_scrape = False
if run_lengthy_web_scrape:
    gc_thread = Gate_scrape_thread()
    gc_thread.start()

current_time = Gate_checker().date_time

def home(request):
    
    # Homepage first skips a "POST", goes to else and returns home.html since the query is not submitted yet.
    if request.method == "POST":
        main_query = request.POST.get('query','')
        return parse_query(request, main_query)
    else:
        return render(request, 'home.html')


def parse_query(request, main_query):
    
    if main_query == '':        # query is empty then return all gates
        return gate_info(request, main_query='')
    query_in_list_form = []     # Global variable since it is used outside of the if statement in case it was not triggered. purpose: Handeling Error
    if main_query != '':        # if query is not empty it splits it into list form
        query_in_list_form = main_query.split()
        if len(query_in_list_form) == 1:

            # When the length of query_in_list_form is only 1 it returns gates table.
            gate_query = query_in_list_form[0]
            return gate_info(request, gate_query)
    
    if len(query_in_list_form) > 1:
        if query_in_list_form[0] == 'w':
            weather_query_airport  = query_in_list_form[1]
            weather_query_airport = weather_query_airport.upper()       # making query uppercase for it to be compatible
            return metar_display(request, weather_query_airport)
        if query_in_list_form[0] == 'i':
            flight_query = query_in_list_form[1]
            return flight_deets(request, flight_query)

            '''
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
    # In the database the all gates are uppercase so making the query uppercase    
    gate = gate.upper()
    print('Search results for ', gate)

    # Dictionary format a list with one or many dictionaries each dictionary containing 4 items:gate,flight,scheduled,actual

    current_time = Gate_checker().date_time()
    print(1, current_time)
    gate_data_table = Gate_checker().ewr_UA_gate(gate)
    
    # showing info if the info is found else it falls back to `No flights found for {{gate}}`on flight_info.html
    if gate_data_table: 
        # print(gate_data_table)
        return render(request, 'flight_info.html',{'gate_data_table': gate_data_table, 'gate': gate, 'current_time': current_time})
    else:       # Returns all gates since query is empty. Maybe this is not necessary. Try deleting else statement.
        return render(request, 'flight_info.html', {'gate': gate})


def flight_deets(request, flight_query ):
    # pull weather for a partifular flight number. 
    dep_des = Pull_dep_des()
    dep_des = dep_des.pull(flight_query)
    
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
    weather = Weather_display()
    
    # TODO: Figure out how to account for errors and queries that are not found.
    weather = weather.scrape(weather_query)
    print('test1')
    airport = weather_query[-4:]
    print(airport)
    print(weather)
    return render(request, 'metar_info.html', {'airport': airport, 'weather': weather})

    
def about(request):
    return render(request, 'home.html')
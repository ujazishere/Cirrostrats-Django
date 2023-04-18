from django.shortcuts import render
from django.http import HttpResponse
from .root_gate_checker import Gate_checker
import threading

# TODO: Deploy the ability to chat and store queries.

'''
views.py runs as soon as the base web is requested. Hence, GateCheckerThread() is run the background right away.
It will then run 
'''
run_lengthy_web_scrape = False

# Defining a global variable to hold the gate checker instance
gc = None

# Define a thread class to run the gate checker in the background
class GateCheckerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.gc = Gate_checker()

    
    # run method is the inherited. It gets called as
    def run(self):
        self.gc.activator()
    

# Create an instance of the GateCheckerThread class and start the thread
gc_thread = GateCheckerThread()
if run_lengthy_web_scrape:
    gc_thread.start()


def flights(gate):
    return Gate_checker().ewr_UA_gate(gate)


def home(request):
    
    
    if request.method == "POST":
        # query = request.POST.get('query','')
        # if query.upper() in:
        return parse_query(request)

    else:
        # TODO: When User first accesses the web the date and time of the latest master should be displayed 
        return render(request, 'home.html', {'loading': True})


def parse_query(request):
    print(request)
    query = request.POST.get('query','').upper()
    if len(query) <= 3:
        flight_stack = flights(query)
        return flight_info(request, flight_stack)
    else:
        return metar_display(request)

def flight_info(request, flights):

    # Homepage first skips a "POST", goes to else and returns home.html

    gate = request.POST.get('query','').upper()
    if gate:

        print('Getting flight infor for gate:', gate)

        # Dictionary format a list with one or many dictionaries each dictionary containing 4 items:gate,flight,scheduled,actual

        flights = Gate_checker().ewr_UA_gate(gate)
        
        # showing info if the info is found else it falls back to `No flights found for {{gate}}`on flight_info.html
        if flights: 
            return render(request, 'flight_info.html',{'flights': flights, 'gate': gate})
        else:
            return render(request, 'flight_info.html', {'gate': gate})
    else:
        return render(request, 'flight_info.html')


# def flight_info(request):

#     # Homepage first skips a "POST", goes to else and returns home.html

#     if request.method == "POST":
#         gate = request.POST.get('query','').upper()
#         if gate:

#             print('Getting flight infor for gate:', gate)

#             # Dictionary format a list with one or many dictionaries each dictionary containing 4 items:gate,flight,scheduled,actual

#             flights = Gate_checker().ewr_UA_gate(gate)
            
#             # showing info if the info is found else it falls back to `No flights found for {{gate}}`on flight_info.html
#             if flights: 
#                 return render(request, 'flight_info.html',{'flights': flights, 'gate': gate})
#             else:
#                 return render(request, 'flight_info.html', {'gate': gate})
#         else:
#             return render(request, 'flight_info.html')
#     else:
#         # TODO: When User first accesses the web the date and time of the latest master should be displayed 
#         return render(request, 'home.html', {'loading': True})


def metar_display(request):
    
    return render(request, 'metar_info.html')


def about(request):
    return render(request, 'about.html')
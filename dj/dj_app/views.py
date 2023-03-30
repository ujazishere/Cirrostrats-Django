from django.shortcuts import render
from django.http import HttpResponse
from .root_gate_checker import Gate_checker
import threading


# def gate_out(request):
    # return render(request,'home.html')

# Define a global variable to hold the gate checker instance
gc = None

# Define a thread class to run the gate checker in the background
class GateCheckerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.gc = Gate_checker()
    
    # run method is the inherited. It gets called as
    def run(self):
        self.gc.multiple_thread()
    

# Create an instance of the GateCheckerThread class and start the thread
gc_thread = GateCheckerThread()
gc_thread.start()

# Deploy the ability to chat and store queries.
def flight_info(request):
    # Homepage first skips the POST 
    if request.method == "POST":
        gate = request.POST.get('gate','')
        if gate:
            # gc = Gate_checker(gate)
            # gc.multiple_thread()
            gate = gate.upper()
            print('Getting gate:', gate)

            # Dictionary format a list with one or many dictionaries each dictionary containing 4 items:gate,flight,scheduled, actual
            flights = Gate_checker(gate).ewr_UA_gate()
            gate = flights[0]['gate']
            
            return render(request, 'flight_info.html',{'flights': flights})
        else:
            return render(request, 'flight_info.html')
    else:
        return render(request, 'home.html', {'loading': True})


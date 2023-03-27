from django.shortcuts import render
from django.http import HttpResponse
from .root_gate_checker import Gate_checker


# def gate_out(request):
    # return render(request,'home.html')


def flight_info(request):
    if request.method == "POST":
        gate = request.POST.get('gate','')
        if gate:
            gc = Gate_checker(gate)
            gc.multiple_thread()
            print('Getting gate:', gate)

            # Dictionary format a list with one or many dictionaries each dictionary containing 4 items:gate,flight,scheduled, actual
            flights = Gate_checker(gate).ewr_UA_gate()
            
            gate = flights[0]['gate']
            
            return render(request, 'flight_info.html',{'flights': flights})
    return render(request, 'flight_info.html')


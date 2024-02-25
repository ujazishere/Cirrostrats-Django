import requests
from time import time,sleep
import pickle

# the script scrapes massive amounts of flight_aware united flight
    # individual flights pulled every 5 seconds which allows
    # complies with the '10 pulls in a minute' pull timer.


query = "1217"
apiKey = "V2M5XJKNC5L1oJb0Dxukt0HJ7c8cxXDQ"
apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
auth_header = {'x-apikey':apiKey}

flight_number_start = 2000
flight_number_stop = 3500

new_responses = {}          # Sucecssful status code 200 ones.
other_responses = {}        # Unsuccessful ones
count = 1
start_time = int(time())
for query in range(flight_number_start,flight_number_stop):
    response = requests.get(apiUrl + f"flights/ual{query}", headers=auth_header)
    count += 1
    if response.status_code == 200:         # Add successful ones to new_responses
        new_responses.update({query:response})              
        success_stop = int(time())
        sleep(6)
        print(f'done: {count,query}',f'et:{success_stop-start_time}')
    else:
        other_responses.update({query:response})    # Unsuccessful ones to other responses
        print('not done')
        stop = int(time())
        print(f'unsuccessful_time: {stop-start_time}')
        sleep(5)



# _____________________________________

# The extra bits that analyses the fa data
with open(r"C:\Users\ujasv\OneDrive\Desktop\fa_data_2023_11_21.pkl", "rb") as f:
    responses = pickle.load(f)

# *********************************
#************** VVI ***************
# ********* PLEASE READ ***********
# *********************************

# In responses.items() the key is flight number, val is the status code.
# val .json() is a dict type item whose keys are flights, links and num_pages
# value of flights is a USUALLY a list type item. it can also be an empty list
# This list usually contains 12-15 items each of them is a dict of 53 items
# keys of this 53 item dict is a string and value can be a string or dict or null


# Check all type of items and how many of then are there in tots
tots = {}
for a,resp in responses.items():
    tots[type(resp.json())] = tots.get(type(resp.json()),0) +1
    pass
print(tots)
# >>> dict : 998

# Check all unique 53 items within ['flight']
x = {}
for a,b in responses.items():
    flights = b.json()['flights']
    if flights:
        for a_flight in flights:
            for inner_key,inner_val in a_flight.items():
                x[inner_key] = x.get(inner_key,0) + 1
x
# flatten out and chek if theres a discrepency in the 53 item dictonary.
set(list(x.values()))

# iterate over the 53 item dict.
x = {}
for a,b in responses.items():
    flights = b.json()['flights']
    if flights:
        for fifty_three_item_dict in flights:
            for a,b in fifty_three_item_dict.items():
                pass

# Getting rid of the null items from the 53 item dict
updated_responses = {}          # hybrid vals that dont have json() object.  Just flights
for outer_flight_number,outer_response in responses.items():
    flights = outer_response.json()['flights']           # 15 or so items
    updated_flights = []
    if flights: 
        for fifty_three_item_dict in flights:
            updated_dict = {}
            for inner_keys,inner_vals in fifty_three_item_dict.items():
                if type(inner_vals) != dict:
                    if inner_vals:
                        updated_dict.update({inner_keys:inner_vals})
                if type(inner_vals) == dict:
                    if inner_vals['code']:      # in this case inner_vals is 'origin' or 'destination'
                        updated_dict.update({inner_keys:inner_vals})
            updated_flights.append(updated_dict)
    updated_flights_in_dict = {'flights':updated_flights}
    updated_responses.update({outer_flight_number:updated_flights_in_dict})
# iterating through those flights since they'hybrid values that dont have json() object
for flt_num, flights in updated_responses.items():
    flights = flights['flights']
    if flights:
        for each_flight in flights:
            for key, vals in each_flight.items():       # iter through 53 item dict whose nulls have been trimmed off
                pass

# get rid of all key values pairs whose values are null. This is the extra one
example_flights = responses[0].json()['flights']
fifty_three_item_dict = example_flights[0]
x = {}
for a,b in fifty_three_item_dict.items():
    if type(b) != dict:
        if b:
            x.update({a:b})

# The amount of flights(dict form) and their occourances. typically 15 dictionaries in a list.
tots = {}
for key, val in responses.items():
    all_flights = responses[key].json()['flights']
    fifty_three_typicals = len(all_flights)
    tots[fifty_three_typicals] = tots.get(fifty_three_typicals, 0) +1


# flatten out all dictionaries within the `flights``
all_dictionaries = []
for key, val in responses.items():
    # Each flight with have upto 15 dictionaries in list form.
    all_flights = responses[key].json()['flights']  
    # Hence, all_flights is a list type that contains upto 15 dictionaries
    
    tot_in_flights_list = len(all_flights)
    if tot_in_flights_list != 0:    # Some of these lists are empty
        for five_three_dicts in all_flights:    # iter through all dictionaries
            all_dictionaries.append(five_three_dicts)        





# Look up the 0th item in the associated list. In this case `flights`
list(list(responses.values())[0].json().keys())[0]
# >>> 'flights'

tots = {}
for resp in responses.values():
    three_item_dict = resp.json()
    for i in three_item_dict.keys():
        tots[i] = tots.get(i,0) +1
# >>> {'flights': 998, 'links': 998, 'num_pages': 998}

# tots here contains totals of flight list. iterating through all flights and checking their len
tots = {}
for resp in responses.values():
    three_item_dict = resp.json()
    flights = three_item_dict['flights']
    tots[len(flights)] = tots.get(len(flights), 0) + 1

# iterating through those flight vals:
tots = {}
for resp in responses.values():
    three_item_dict = resp.json()
    flights = three_item_dict['flights']
    if len(flights) != 0:       # Accounting for the empty lists
        for i in flights:
            for a in i.keys():
                tots[a] = tots.get(a,0) + 1

# Check unique routes and their amounts.
def unique_checker_fa(item,tot_items=None):
    tots = {}
    for resp in responses.values():
        three_item_dict = resp.json()
        flights = three_item_dict['flights']
        if flights:             # Since flights can be empty
            for i in flights:
                if i[item]:
                    tots[i[item]] = tots.get(i[item], 0) + 1
    if tot_items:
        return len(list(tots.keys()))
    else:
        return tots 
routes = unique_checker_fa('route')

# Unique Scheduled times and their occourances:
tots= {}
for flight_numer, response in responses.items():
    flights = response.json()['flights']
    if flights:
        scheduled_out = flights[0]['scheduled_out']
        if scheduled_out:
            scheduled_out = scheduled_out[:10]
            tots[scheduled_out] = tots.get(scheduled_out,0) + 1
tots

# Unique origin and their occourances:
tots= {}
for flight_numer, response in responses.items():
    flights = response.json()['flights']
    if flights:
        origin = flights[0]['origin']['code']
        if origin:
            tots[origin] = tots.get(origin,0) + 1
        else:
            print(origin)
tots

# get all those routes and see the most used route total totals like literally
unique_routes = {}
for route, totals in routes.items():
    unique_routes[totals] = unique_routes.get(totals,0) + 1

# scheduled_out only since it accounts for upto 10 index
def unique_checker_fa(item,tot_items=None):
    tots = {}
    for resp in responses.values():
        three_item_dict = resp.json()
        flights = three_item_dict['flights']
        if len(flights) != 0:
            for i in flights:
                if i[item] != None:
                    tots[i[item][:10]] = tots.get(i[item][:10], 0) + 1
    if tot_items:
        return len(list(tots.keys()))
    else:
        return tots 

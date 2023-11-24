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

new_responses = {}
other_responses = {}
count = 1
count_res_200 = 1
start_time = int(time())
for query in range(999,2000):
    response = requests.get(apiUrl + f"flights/ual{query}", headers=auth_header)
    count += 1
    if response.status_code == 200:
        new_responses.update({query:response})
        success_stop = int(time())
        sleep(6)
        print(f'done: {count,query}',f'et:{success_stop-start_time}')
    else:
        new_responses.update({query:response})
        print('not done')
        stop = int(time())
        print(f'unsuccessful_time: {stop-start_time}')
        sleep(5)

all_responses = {}
for response in other_responses.items():
    all_responses.update(set(response.status_code),)


# _____________________________________

# The extra bits that analyses the fa data
with open(r"C:\Users\ujasv\OneDrive\Desktop\fa_data_2023_11_21.pkl", "rb") as f:
    responses = pickle.load(f)

# In responses.items() the key is flight number, val is the status code.
# val .json() is a dict type item whose keys are flights, links and num_pages
# value of flights is a USUALLY a list type item. it can be an empty list as well
    # This list usually contains 12-15 items each of them is a dict of 53 items

# Check all type of items and how many of then are there in tots
tots = {}
for a,resp in responses.items():
    tots[type(resp.json())] = tots.get(type(resp.json()),0) +1
    pass
print(tots)
# >>> dict : 998

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
        if len(flights) != 0:
            for i in flights:
                if i[item] != None:
                    tots[i[item]] = tots.get(i[item], 0) + 1
    if tot_items:
        return len(list(tots.keys()))
    else:
        return tots 
routes = unique_checker_fa('route')

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

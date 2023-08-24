import pickle
import os
from collections import Counter

# CONCLUSION: Majors:

# use METAR DECODER on https://e6bx.com/metar-decoder/
# TODO: Attempt to derive the Typical_met pattern on the metar and the taf to determine prominent info:
         # VFR/IFR/LIFR; Freezing conditions, icing, stronger winds with gusts, reduce font size of less important information.
         # give ability to decode individual complex items.  
# POA: determine each item for typicality in the metar list form and put them all together in a seperate container.
    # Once that is done, sort the non-typical ones for typicality.
        # Repeat the process until exhaustion. sort these by most typical to the least typical.
        # The goal is to make use of the most typical metar items then color code by them

# Be careful these paths. Shortened path is only local to the vs code terminal but doesnt work on the main cmd terminal
metar_stack_pkl_path = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\dj_app\root\pkl\METAR_stack.pkl"
with open(metar_stack_pkl_path, 'rb') as f:         
    met = pickle.load(f)

all_metar_list = [i.split() for i in met]       # List of lists: Bulk metar in the list form. Each metar is also a list of metar items.


typical_metar_item = []
for i in all_metar_list:
    item_index = 3
    typical_metar_item.append(i[item_index])

# The first prominent item is the 4 letter ICAO airport ID. It semes TAF got in there somehow.
# Removing the metar items that dont have first letter as 'K' or is not 4 letters long.
len(all_metar_list)             # printing len to compare before and after the loop to see what was popped
for individual_full_metar in all_metar_list:
    airport_id = individual_full_metar[0]
    first_leter_of_airport_id = airport_id[0]
    if len(airport_id) != 4 and first_leter_of_airport_id != 'K':
        outlaw_metar = individual_full_metar
        all_metar_list.pop(all_metar_list.index(outlaw_metar))

len(all_metar_list)             # comparing how many items were removed.

# second prominent item of the metar is date and time DDTTTTZ. seems like all of the second prominent item is always going to be zulu time.
for individual_full_metar in all_metar_list:
    datetime = individual_full_metar[1]
    z_in_datetime = individual_full_metar[1][-1]
    if len(datetime) != 7 and z_in_datetime != 'Z':    # conditions for it to be reliable:
        outlaw_metar = individual_full_metar
        outlaw_metar_index = all_metar_list.index(outlaw_metar)
        all_metar_list.pop(outlaw_metar_index)

"""
# Third prominent item is the AUTO or not item. if its not AUTO its usually winds with gust.
# Another significant BLUEPRINT!!!!
class Auto_or_not:
    auto_items = []
    not_auto = []
    others = []
    for individual_full_metar in all_metar_list:
        auto_as_third_item = individual_full_metar[2]
        if auto_as_third_item == 'AUTO':
            auto_items.append(auto_as_third_item)
        elif auto_as_third_item != 'AUTO':
            not_auto.append(auto_as_third_item)
        else:
            others.append(auto_as_third_item)
x = Auto_or_not()
len(x.auto_items)
len(x.not_auto)
len(x.others)
"""

class Auto:
    new_all_metar_list = []
    not_auto = []
    for individual_full_metar in all_metar_list:
        auto_as_third_item = individual_full_metar[2]
        if auto_as_third_item == 'AUTO':    # If 'AUTO' then remove it
            individual_full_metar.pop(2)
            new_all_metar_list.append(individual_full_metar)
        elif auto_as_third_item != 'AUTO':
            not_auto.append(auto_as_third_item)
            new_all_metar_list.append(individual_full_metar)

auto = Auto()

all_metar_list = auto.new_all_metar_list

new_aml = []
wind_index = 2
for each_metar in all_metar_list:
    wind_item = each_metar[wind_index]
    if 'KT' in wind_item:
        if len(wind_item) == 7 or 'G' in wind_item:
            each_metar.pop(wind_index)
            new_aml.append(each_metar)
        else:
            new_aml.append(each_metar)
    else:
        new_aml.append(each_metar)

all_metar_list = new_aml

# 5th prominent item is visibility.
new_aml = []
vis_index = 2
for each_metar in all_metar_list:
    visibility = each_metar[vis_index]
    if 'SM' in visibility:
        each_metar.pop(vis_index)
        new_aml.append(each_metar)
    else:
        new_aml.append(each_metar)
all_metar_list.append()

altimeter_setting = r"\w{1}\d{4})"

# Seperate Metar after Temp and altimeter

# The following will allow for extracting unique items and their count.

counter = Counter(x.not_auto)
unique = counter.keys()


# Seems unnecessary. 
class Typical_met:                          # analyzing the first metar in the bulk metar list
    typical_complete_metar = all_metar_list[0]         # First metar from the all metar bulk list
    id = all_metar_list[0][0]
    zulu_time = all_metar_list[0][1]
    z_in_time = zulu_time[-1]
    auto_or_not = all_metar_list[0][2]
    winds = all_metar_list[0][3]





















import pickle
import os
from collections import Counter
# CONCLUSION: Majors:

# TODO: Attempt to derrive the Typical_met pattern on the metar and the taf to determine prominent info:
         # VFR/IFR/LIFR; Freezing conditions, icing, stronger winds with gusts, reduce font size of less important information
# POA: determine each item for typicality in the metar list form and put them all together in a seperate container.
    # Once that is done, sort the non-typical ones for typicality.
        # Repeat the process until exhaustion. sort these by most typical to the least typical.
        # The goal is to make use of the most typical metar items then color code by them

# Be careful these paths. Shortened path is only local to the vs clode terminal but doesnt work on the main cmd terminal
metar_stack_pkl_path = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\dj_app\root\pkl\METAR_stack.pkl"
with open(metar_stack_pkl_path, 'rb') as f:         
    met = pickle.load(f)

'''
item_2 = []
for i in all_metar_list:
    item_2.append(i[1])
'''

all_metar_list = [i.split() for i in met]       # List of lists: Bulk metar in the list form. Each metar is also a list of metar items.

# The first prominent item is the airport ID. It semes TAF got in there somehow.
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
        all_metar_list.pop(all_metar_list.index(outlaw_metar))


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
        elif auto_as_third_item !='' 'AUTO':
            not_auto.append(auto_as_third_item)
        else:
            others.append(auto_as_third_item)
x = Auto_or_not()
len(x.auto_items)
len(x.not_auto)
len(x.others)

counter = Counter(item_one)
unique = counter.keys()

# TODO: insert NOT_AUTO into the mix that way you can work with data easily.




typical_bulk_metars = Auto_or_not.auto_items

class Wind_items:
    wind_items = []
    no_winds = []
    for i in typical_bulk_metars:
        if 'KT' in i[3]:
            wind_items.append(i)
        else:
            no_winds.append(i)
    print(len(all_metar_list), len(wind_items))

typical_bulk_metars = Wind_items.wind_items

no_k = []               # No k in airport ID
for airport_id in typical_bulk_metars:
    if airport_id[0][1] == 'K':
        no_k.append(airport_id)
# print(Typical_met.complete_metar)
# print(Typical_met.zulu_time)
altimeter_setting = r"\w{1}\d{4})"

# Seperate Metar after Temp and altimeter


# Seems unnecessary. 
class Typical_met:                          # analyzing the first metar in the bulk metar list
    typical_complete_metar = all_metar_list[0]         # First metar from the all metar bulk list
    id = all_metar_list[0][0]
    zulu_time = all_metar_list[0][1]
    z_in_time = zulu_time[-1]
    auto_or_not = all_metar_list[0][2]
    winds = all_metar_list[0][3]





















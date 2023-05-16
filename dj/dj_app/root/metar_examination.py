import pickle
import os

print(os.getcwd())

with open('dj/dj_app/root/pkl/METAR_stack.pkl', 'rb') as f:
    met = pickle.load(f)

all_metar_list = [i.split() for i in met]
class Typical_met:  
    complete_metar = all_metar_list[0]
    id = all_metar_list[0][0]
    zulu_time = all_metar_list[0][1]
    z_in_time = all_metar_list[0]
    auto_or_not = all_metar_list[0][2]
    winds = all_metar_list[0][3]
        

auto_items = []
for i in all_metar_list:
    if i[2] == 'AUTO':
        auto_items.append(i)
# print(len(met), len(auto_items))

all_metar_list = auto_items

wind_items = []
no_winds = []
for i in all_metar_list:
    if 'KT' in i[3]:
        wind_items.append(i)
    else:
        no_winds.append(i)
print(len(all_metar_list), len(wind_items))


no_k = []
for i in all_metar_list:
    if i[0][1] == 'K':
        no_k.append(i)
# print(Typical_met.complete_metar)
# print(Typical_met.zulu_time)


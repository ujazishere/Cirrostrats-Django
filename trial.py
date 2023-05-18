'''import pickle

with open('METAR_stack.pkl', 'rb') as f:
    met = pickle.load(f)

all_metar_list = [i.split() for i in met]
id = all_metar_list[0][0]
time = all_metar_list[0][1]
auto_or_not = all_metar_list[0][2]
wague_items = []
for i in all_metar_list:
    if i[2] == 'AUTO':
        wague_items.append(i)

print(len(wague_items))
# print((all_metar_list[:2]))
print(all_metar_list[0][1][-1])
print(all_metar_list[0][3])

'''
import pickle
import os
print(os.getcwd())



with open('dj/queries.pkl', 'rb') as f:
    x = pickle.load(f)

print(x)
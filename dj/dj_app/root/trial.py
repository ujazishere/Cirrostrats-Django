import pickle
# Create your tests here.
# import os

# print(os.getcwd())

# Dict wwith keys as states. Each key or 'state' has a list as list as its value.
# This list contains 2 items.
    # first one is the link and other is the list of all airports of that state
with open('dj/dj_app/root/pkl/all_US_airports_dict.pkl', 'rb') as f:
    x = pickle.load(f)
    
print(len((x['Florida'][1])))
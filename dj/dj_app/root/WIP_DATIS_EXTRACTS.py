from .root_class import Root_class
import re
import pickle
from collections import Counter
import json
import requests


# The most comman pattern
airport_id = r'[A-Z]{1,3} '
atis_info = r'(ATIS|ARR/DEP|DEP|ARR) INFO [A-Z] '
time_in_zulu = r'(\d{1,4}Z(\.| ))'        #4 digits followed by `Z`
special_or_not = r'(SPECIAL\.)? '    #SPECIAL then `.` or just `.`
winds = r'((\d{5}(G|KT)(\d{2}KT)?)|VRB\d\dKT) '    # winds that account for regular, variable and gusts
SM = r'M?\d{1,2}SM '            # DOESNT ACCOUNT FOR FRACTIONALS
# Right after SM there are light or heavy RA SN DR BR and vertical visibilities that need to be accounted for
sky_condition = r'((FEW|CLR|BKN|OVC|SCT)(\d{3})? ){1,10}'       
temperature = r'(M?\d\d/M?\d\d )'
altimeter = r'A\d{4} \(([A-Z]{3,5}( |\))){1,4}(\. | )'      # Accounts for dictated bracs and trailing `. ` or just ` `


lengthy_regex = airport_id + atis_info + time_in_zulu + special_or_not
lengthy_regex = lengthy_regex + winds + SM + sky_condition
lengthy_regex = lengthy_regex +temperature + altimeter

def datis_info(airport_id):
    datis_api =  f"https://datis.clowd.io/api/{airport_id}"
    datis = requests.get(datis_api)
    datis = json.loads(datis.content.decode('utf-8'))
    datis_raw = 'N/A'
    if type(datis) == list and 'datis' in datis[0].keys():
        datis_raw = datis[0]['datis']

all_datis_airports_path = r'C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\all_datis_airports.pkl'
with open(all_datis_airports_path, 'rb') as f:
    all_datis_airports = pickle.load(f)

datis_info_stack = []
for each_id in all_datis_airports:
    datis_info_stack.append(datis_info(each_id))

YYYYMMDD = Root_class().date_time(raw_utc=True)
with open(f'datis_info_stack_{YYYYMMDD}.pkl', 'wb') as f:
    pickle.dump(datis_info_stack,f)


datis_extracts = r'C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\datis_info_stack_20231206.pkl'
with open(datis_extracts, 'rb') as f:
    datis_extracts = pickle.load(f)
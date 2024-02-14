import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from bs4 import BeautifulSoup as bs4
import requests

# TODO: TAF is still remianing
# Extracts METARs and TAFs. Heavy pull with 2000+ airport ID and each airport pulls big chunk of data
# DONT USE THIS SCRIPT IF YOU DONT NEED TO. METAR_stack.pkl has the output for it
# Shorten the airport_ID list if you are to use it. Get rid of No_mets and no_tafs. Those consists of airports that return null vals.
# Dont exceed 500 workers. Better 350. It doesn't get much better after 500.

# 20,296 airport ID in list form. eg ['DAB', 'EWR', 'X50', 'AL44']
with open('dj/dj_app/root/pkl/airport_identifiers_US.pkl', 'rb') as f:
    id = pickle.load(f)


# list all files
base_path = r"C:\Users\ujasv\OneDrive\Desktop\pickles"
all_pickle_files = os.listdir(base_path)            # get all file names in pickles folder

# Loading a perticular file
Bulk_met_path = r"C:\Users\ujasv\OneDrive\Desktop\pickles\BULK_METAR_JAN_END_2024.pkl" 
with open(Bulk_met_path, 'rb') as f:
    w = pickle.load(f)
print(f'total metar files: {len(w)}')


# isalpha returns bool for string if the letters are all alphabets eg. EWR, MCO, MLB, etc.
    # and discards airports like 'X50' since its alphanumeric
airport_ID = [i for i in id if len(i) ==3 and i.isalpha()]      # Investigate this sorcery

# Use this to shorten the list for trial
# airport_ID = airport_ID[:10]

print('alphabetic airport ID',len(airport_ID))
print('all airport ID as imported',len(id))

def code_tag(airport_id,taf=None):
    """
    # Archieve
    awc_web = f"https://aviationweather.gov/metar/data?ids=K{airport_id}&format=raw&hours=0&taf={TAF}&layout=on"
    """
    
    # Metar gives data upto 15 days ago and TAF gives upto 17 days ago
    if taf:
        awc_taf_api = f"https://aviationweather.gov/api/data/taf?ids={airport_id}&hours=408"
        metar_raw = requests.get(awc_taf_api)
    else:
        awc_metar_api = f"https://aviationweather.gov/api/data/metar?ids={airport_id}&hours=360"
        metar_raw = requests.get(awc_metar_api)
    
    metar_raw = metar_raw.content
    metar_raw = metar_raw.decode("utf-8")

    return metar_raw

# Prepending K to 3 leter codes 
def export_airports_without_digits():
    new_id = []
    for i in id:    # Using all airport ID's
        if len(i) == 3:
            prepend = 'K' + i
            new_id.append(prepend)
        else:
            new_id.append(i)

    # seperating id's that contain digit since those mostly dont have associated metars/TAFs
    x = set()
    for i in new_id:
        for char in i:
            if char.isdigit():
                x.add(i)
    ids_with_digit = list(x)
    ids_without_digit = new_id      # declaring the variable
    for i in ids_with_digit:
        ids_without_digit.remove(i)
    return ids_with_digit, ids_without_digit

ids_with_digit, ids_without_digit = export_airports_without_digits()


with open(r'C:\Users\ujasv\OneDrive\Desktop\pickles\no_mets.pkl', 'rb') as f:
    no_mets = pickle.load(f)

ids_without_digit_with_no_mets_ecluded = [i for i in ids_without_digit if i not in no_mets]

# This is without the concurrent futures threadpool executor. Inefficient but stable
taf_bool = True
count = 0
bulky_weather = []
no_weather_id = []
yes_weather_id = []
# half_index = int(len(ids_without_digit)/2)     # use this to split pulls into two sections.
for airport_id in ids_without_digit_with_no_mets_ecluded:
    count += 1
    metars = code_tag(airport_id=airport_id,taf=taf_bool)
    if not metars:
        no_weather_id.append(airport_id)
        print('no_weather_id', airport_id, count)
    else:
        metars_in_list_form = metars.split('\n')    # Delete this for TAF.
        for a_metar in metars_in_list_form:
            if a_metar:         # since, there are empty metar lines.
                bulky_weather.append(a_metar)
        yes_weather_id.append(airport_id)
    print(count)
    # use this to test how long it takes to pull and if the pull is even working.
    # Comment it out if you plan to use the whole thing.
    if count >5:
        print('Test done! no_weather_id/yes_weather_id: ', len(no_weather_id),'/', len(yes_weather_id))
        break

# dump metar to desktop pickles
# *********CAUTION HARD WRITE*********
def dump_bulky_weather(bulky_weather):
    with open(r'C:\Users\ujasv\OneDrive\Desktop\pickles\BULK_METAR_JAN_2024_.pkl', 'wb') as f:
        pickle.dump(bulky_weather, f)
dump_bulky_weather(bulky_weather)

# Important code. Seemed to take forever to build this
def fix_taf():
    fixed = []
    bt = bulky_weather
    for i in range(len(bt)):
        initial_two = bt[i][:2]
        trailing = bt[i][-1]
        if initial_two != '  ':      # main bod
            if trailing == ' ':      # last index empty: taf with forecast
                new_line_break = bt[i][:-1] + '\n'
            elif trailing != ' ':    # main bod wo taf
                fixed.append(bt[i])
        elif initial_two == '  ' and trailing == ' ':    # associated forecast that continues
            new_line_break += bt[i][:-1] + '\n'
        elif initial_two == '  ' and trailing != ' ':   # forecast ends
            new_line_break += bt[i]
            fixed.append(new_line_break)
    for i in fixed:
        print(i)
    return fixed

# This is the Unstable efficient version that pulls upto 8 indexes for whatever reason
airport_ID = ids_without_digit
met_taf = []        # This is essentially code_tag. Using a seperate variable to avoid clashes
with ThreadPoolExecutor(max_workers=500) as executor:
    # First argument in submit method is the function without parenthesis. VVI second is each airport ID
    futures = {executor.submit(code_tag, airport): airport for airport in airport_ID}
    # futures .key() is the memory location of the task and the .value() is the airport ID associated with it
    for future in as_completed(futures):
        # Again. future here as well is the memory location.
        airport_id_2 = futures[future]
        result = future.result()    # result is the output of the task of the memory location
        if result:
            cleaned = result.split('\n')
            if cleaned:
                for each_metar in cleaned:
                    met_taf.append(each_metar)


# for each in met_taf(which is essentially a code_tag), if the code_tag is exactly 2 items(one metar and other TAF)
    # then TAF is good if it is only 1 or less item then that item is most probably METAR)
    # This is done to avoid IndedxErrors Since not all airports report TAF.
TAF_stack = [str(list(i)[1].text) for i in met_taf if len(i) == 2]


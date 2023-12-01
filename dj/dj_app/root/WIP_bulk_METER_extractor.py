from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from bs4 import BeautifulSoup as bs4
import requests

# TODO: TAF is still remianing
# Extracts METARs. need TAFs. Heavy script with 2000+ airport ID
# DONT USE THIS SCRIPT IF YOU DONT NEED TO. METAR_stack.pkl has the output for it
# Shorten the airport_ID list if you are to use it.
# Dont exceed 500 workers. Better 350. It doesn't get much better after 500.
# TAF is remaining.
# This is a heavy script with 2600+ airport ID.
    # Used executor to multi thread the operation



# 20,296 airport ID in list form. eg ['DAB', 'EWR', 'X50', 'AL44']
# with open('pkl/airport_identifiers_US.pkl', 'rb') as f:
    # id = pickle.load(f)
with open('dj/dj_app/root/pkl/airport_identifiers_US.pkl', 'rb') as f:
    id = pickle.load(f)


# isalpha returns bool for string if the letters are all alphabets eg. EWR, MCO, MLB, etc.
    # and discards airports like 'X50' since its alphanumeric
airport_ID = [i for i in id if len(i) ==3 and i.isalpha()]      # Investigate this sorcery

# Use this to shorten the list for trial
# airport_ID = airport_ID[:10]

print(len(airport_ID))

def code_tag(airport_id):
    """
    # Archieve
    awc_web = f"https://aviationweather.gov/metar/data?ids=K{airport_id}&format=raw&hours=0&taf={TAF}&layout=on"
    """
    
    # Metar gives data upto 15 days ago and TAF gives upto 17 days ago
    # awc_taf_api = f"https://aviationweather.gov/api/data/taf?ids={airport_id}&hours=408"
    awc_metar_api = f"https://aviationweather.gov/api/data/metar?ids={airport_id}&hours=360"
    
    metar_raw = requests.get(awc_metar_api)
    metar_raw = metar_raw.content
    metar_raw = metar_raw.decode("utf-8")

    return metar_raw

# Prepending K to 3 leter codes 
new_id = []
for i in id:
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
ids_without_digit = new_id
for i in ids_with_digit:
    ids_without_digit.remove(i)


# without concurrent futures threadpool executor. Inefficient but stable
# For somme reason ends up with only 21460 items in the bulky)metar
count = 0
bulky_metar = []
no_mets = []
yes_mets = []
for airport_id in ids_without_digit:
    count += 1
    metars = code_tag(airport_id)
    if not metars:
        no_mets.append(airport_id)
    else:
        metars_in_list_form = metars.split('\n')
        for a_metar in metars_in_list_form:
            bulky_metar.append(a_metar)
        yes_mets.append(airport_id)
    if count >30:
        break


# The Unstable efficient version that pulls upto 8 indexes for whatever reason
# Same as the stable inefficient version: ends up with only 21460 items in the list
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

# with open('METAR_stack.pkl', 'wb') as f:
    # pickle.dump(metar_stack, f)

with open('TAF_stack.pkl', 'wb') as f:
    pickle.dump(TAF_stack, f)
print(len(TAF_stack))

# Some of the TAF stack contains 

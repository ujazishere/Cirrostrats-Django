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
    TAF = 'on'
    awc_web = f"https://aviationweather.gov/metar/data?ids=K{airport_id}&format=raw&hours=0&taf={TAF}&layout=on"

    response = requests.get(awc_web)
    soup = bs4(response.content, 'html.parser')
    code_tag = soup.find_all('code')
    
    return code_tag


met_taf = []        # This is essentially code_tag. Using a seperate variable to avoid clashes
troubled = []
with ThreadPoolExecutor(max_workers=500) as executor:
    # First argument in submit method is the function without parenthesis. VVI second is each airport ID
    futures = {executor.submit(code_tag, airport): airport for airport in airport_ID}
    # futures .key() is the memory location of the task and the .value() is the airport ID associated with it
    for future in as_completed(futures):
        # Again. future here as well is the memory location.
        airport_id_2 = futures[future]
        try:
            result = future.result()    # result is the output of the task of the memory location
            met_taf.append(result)
        except Exception as e:
            troubled.append(airport_id_2)

code_tag = met_taf
# stripping off empty list to avoid error
met_taf = [x for x in met_taf if x]
# print(met_taf)

# metar_stack = [str(list(i)[0].text) for i in met_taf]

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

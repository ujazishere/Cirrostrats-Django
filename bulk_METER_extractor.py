from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from bs4 import BeautifulSoup as bs4
import requests

# TODO: TAF is still remianing
# Extracts METARs. need TAFs. Heavy script with 2000+ airport ID
# DONT USE THIS SCRIPT IF YOU DONT NEED TO. METAR_stack.pkl has the output for it
# Shorten the airport_ID list if you are to use it.
# Done exceed 500 workers. It doesn't get much better after that.
# TAF is remaining.
# This is a heavy script with 2600+ airport ID.
    # Used executor to multi thread the operation

with open('pkl/airport_identifiers_US.pkl', 'rb') as f:
    id = pickle.load(f)


airport_ID = [i for i in id if len(i) ==3 and i.isalpha()]

# Use this to shorten the list for trial
# airport_ID = airport_ID[:10]

print(len(airport_ID))

metar_stacked = []
taf_stacked = []
def code_tag(airport_id):
    TAF = 'on'
    awc_web = f"https://aviationweather.gov/metar/data?ids=K{airport_id}&format=raw&hours=0&taf={TAF}&layout=on"

    response = requests.get(awc_web)
    soup = bs4(response.content, 'html.parser')
    code_tag = soup.find_all('code')
    
    return code_tag


met_taf = []
troubled = []
with ThreadPoolExecutor(max_workers=500) as executor:
    futures = {executor.submit(code_tag, airport): airport for airport in airport_ID}
    
    for future in as_completed(futures):
        airport = futures[future]
        try:
            result = future.result()
            met_taf.append(result)
        except Exception as e:
            troubled.append(airport)

# stripping off empty list to avoid error
met_taf = [x for x in met_taf if x]


metar_raw = [str(list(i)[0].text) for i in met_taf]
print(len(metar_raw))

with open('METAR_stack.pkl', 'wb') as f:
    pickle.dump(metar_raw, f)
# taf_raw = [str(list(i)[1].text) for i in met_taf]


# taf_stacked.append(taf_raw)
from bs4 import BeautifulSoup as bs4
import requests

"""
Key info on bs4:
.find() method will only get you the first item it finds with 
    multiple items within it, if it has items(it is a list with one item).
.find_all() will give you all the items and put those in list form and its like a 
    dictionary but a bs4 form but in a list form. 
in order to find content you have to break the list in to individual parts such
    that it doesn't show you len() more than 1
You can then plug in .text or ['href']
refer to an example like: [print(i['href']) for i in *kwarg.find('a')] or i.text
    instead of i['href']

"""

US_airports = "/airports/United%20States"
response_SV = requests.get(f"https://skyvector.com{US_airports}")
soup_sv = bs4(response_SV.content, 'html.parser')

# finds all 'a' element with attribute 'href'
# cont = soup_sv.find('a', href=US_airports)

# only brings in first item -No Value-.
# cont2 = soup_sv.find('span', {'class': 'views-summary views-summary-unformatted'})

content = soup_sv.find('div', {'class': 'view-content'})
all_states_html = content.find_all('a')

# slicing maneuver that strips off the first unwanted item(0th index) from the list
all_states_html = all_states_html[1:]

# prints out all cities in text form.
# [print(i.text) for i in all_states_html]
states = []
states_link = []
[states.append(each_state.text) for each_state in all_states_html]
[states_link.append(each_state_link['href']) for each_state_link in all_states_html]

state_and_links_dict = dict(zip(states, states_link))

# # prints out all href links.
# [print(i['href']) for i in all_states_html]

base_url = "https://skyvector.com"
all_US_airports_dict = {}
for state, state_link in state_and_links_dict.items():
    # concatenated list of links

    url = base_url + state_link
    response = requests.get(url)
    soup = bs4(response.text, 'html.parser')

    all_airports = soup.find_all('tr')
    all_airports = all_airports[1:]  # stripping off the first index(0th index) that's unwanted

    ind_state_airport = []
    [ind_state_airport.append(each_airport.text.strip()) for each_airport in all_airports]  # .strip stripping line feed

    all_US_airports_dict.update(dict({state: [url, ind_state_airport]}))

# hierarchy is like this: {state: [state sky-vector link, [all airports in that link]]}
                            # e.g {'Florida', ['sv.com/fl', ['DAB - Daytona Beach Airport', 'MCO - Orlando Airport', 'etc']]}
airport_lists = []  # this is a list of 59 lists. Each list contains JUST the airports of an associated state
for state, airport in all_US_airports_dict.items():
    state = state
    airport_link = airport[0]
    airports = airport[1]
    airport_lists.append(airports)

# here I blow up the list of lists into one list making it 20,000+ items each
    # The format is 'ID - airport name'. ID is 3 letter code e.g `DAB`
final_airports = [] 
[final_airports.append(each_list) for each_list in airport_lists]
print(final_airports[0])

# Extracting just the airport identifiers
# Spliting the whole string by ' ' then appending ID(0th index) to the list.
all_US_airports_ID = []   
[all_US_airports_ID.append(i.split()[0]) for i in final_airports]

# making list og all 3 letter alphabet codes attempting to return controlled 
    # airports only and discarding airports like `X50` whih
airport_ID = [i for i in all_US_airports_ID if len(i) ==3 and i.isalpha()]      # Investigate this sorcery


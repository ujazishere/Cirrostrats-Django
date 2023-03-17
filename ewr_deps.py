import requests
from bs4 import BeautifulSoup as bs4
from time import sleep
import threading

response = requests.get('https://www.airport-ewr.com/newark-departures')
soup = bs4(response.content, 'html.parser')

# the index [1:] strips away the first itme in list that is unwanted.
raw_bs4_flight_nums = soup.find_all('div', class_="flight-col flight-col__flight")[1:]
# list of bs4 packets essentially making it list of lists with many empty feed lines.

# This packet contains Delay information for all flights organized per destinations
raw_bs4_html_ele = soup.find_all('div', class_="flight-row")[1:]

flight_nums = []
# multidimensional for loop to extract flight number text and then to remove empty feed line.
for index in range(len(raw_bs4_flight_nums)):
    for i in raw_bs4_flight_nums[index]:
        if i != '\n':
            flight_nums.append(i.text)
UA_flight_nums = []
[UA_flight_nums.append(i) for i in flight_nums if 'UA' in i]

print(UA_flight_nums)

# flight_stats = "https://www.flightstats.com/v2/flight-tracker/UA/1377?year=2023&month=3&date=16&flightId=1139346788"

master = {}
troubled = []
# for loop with timeout and ability to extract individual flight information.
for flt_num in UA_flight_nums:
    flight_view = f"https://www.flightview.com/flight-tracker/UA/{flt_num[2:]}?date=20230316&depapt=EWR"
    response2 = requests.get(flight_view, timeout=5)
    soup2 = bs4(response2.content, 'html.parser')
    if 'Gateway Time-out' in soup2.text:
        print(f'timed out for {troubled}')
        troubled.append(flt_num)
        sleep(5)
    else:
        raw_bs4_scd2 = soup2.find_all('td')

        # Schedule and terminal information with a lot of other garbage too:
        scd = []
        [scd.append(i.text.strip()) for i in raw_bs4_scd2 if i != '']

        scheduled = scd[2].replace('\xa0', '')
        actual = scd[3].replace('\xa0', '')
        terminal = scd[4]
        master.update(dict({flt_num: [terminal, scheduled, actual]}))

print(f'troubled: {len(troubled)}, master : {len(master)}')
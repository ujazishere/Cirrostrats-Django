from bs4 import BeautifulSoup as bs4
import requests
# from data_access import load_kewr
# kewr = load_kewr()

# TODO: extract all airpoirts METAR and TAF  in the airport database
            # compare all unique values and group identical ones
            # analyze data for format patterns to make a template for output
while True:

    # Asking User prompt what they want.
    airport_id = input('Airport ID/break? ')
    if airport_id == 'break':
        print('Thank you! Over!')
        break
    TAF_bools = input('Need TAF yes/no?')
    TAF = 'on' if TAF_bools == 'yes' else 'off'

    awc_web = f"https://aviationweather.gov/metar/data?ids={airport_id}&format=raw&hours=0&taf={TAF}&layout=on"

    response = requests.get(awc_web)
    soup = bs4(response.content, 'html.parser')
    code_tag = soup.find_all('code')


    # code_tag is bs4 element with meter and taf in it. converted it to list then [0]th item is metar in bs4 that is
    # converted whole of it to str which is then split and converted to list
    metar_raw = str(list(code_tag)[0].text)
    taf_raw = str(list(code_tag)[1].text)
    
    metar = metar_raw.split()
    taf = taf_raw.split()
    # taf = str(list(code_tag)[1].text).split()

    # stripping the <code> stuff at the beginning. initially I could see it but seems like now that's not the case.
    # metar[0] = metar[0][6:]
    # taf[0] = taf[0][6:]

    print(metar_raw)
    print(taf_raw)

    #  TODO: parse data to detect key indicators like ceilings below 2k vis below 3sm, windshear,

template = ['Station identifier', 'Date and time of the observation', 'Wind direction and speed', 'Visibility', 'Weather phenomena', 'Sky conditions', 'Temperature and dew point', 'Altimeter setting']

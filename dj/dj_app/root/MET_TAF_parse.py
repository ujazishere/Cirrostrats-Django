from bs4 import BeautifulSoup as bs4
import requests
# from data_access import load_kewr
# kewr = load_kewr()

# TODO: extract all airpoirts METAR and TAF  in the airport database
            # compare all unique values and group identical ones
            # analyze data for format patterns to make a template for output

class Weather_display:
    def __init__(self) -> None:
        pass
    
    def scrape(self, query=None):
        
        # Find ways to convert raw query input into identifiable airport ID
        airport_id = query
        TAF =  'on'
        
        awc_web = f"https://aviationweather.gov/metar/data?ids={airport_id}&format=raw&hours=0&taf={TAF}&layout=on"
        response = requests.get(awc_web)
        soup = bs4(response.content, 'html.parser')
        code_tag = soup.find_all('code')
        
        # code_tag is bs4 element with meter and taf in it. 

        metar_index = 0
        taf_index = 1
        
        metar_and_taf_in_bs4_list = list(code_tag)      # This list has 2 string items. A metar and a TAF.
        
        if len(metar_and_taf_in_bs4_list) == 2:         # If both metar and TAF are available
            metar_raw = str(list(code_tag)[metar_index].text)
            taf_raw = str(list(code_tag)[taf_index].text)
            
            # print(taf_raw.replace("   ", "/n"))             # TODO: Fix the nwe line problem in TAF since it doesnt work in Django
            taf_raw = taf_raw.replace("FM", "\nFrom")
            
            # taf_raw = taf_raw.replace("   ", "/n")        #.replace() does not work in Django. Works outside.
        elif len(metar_and_taf_in_bs4_list) == 1:       # if only METAR is available which is the first and only item
            metar_raw = str(list(code_tag)[metar_index].text)
            taf_raw = 'NA'
        else:                                           # if neither are available
            metar_raw = 'NA'
            taf_raw = 'NA'
        '''
        if metar_and_taf_in_bs4_list[0] and metar_and_taf_in_bs4_list[1]:
            metar_raw = str(list(code_tag)[metar_index].text)
            taf_raw = str(list(code_tag)[taf_index].text)
            
            
        elif metar_and_taf_in_bs4_list[0] and not metar_and_taf_in_bs4_list[1]:
            metar_raw = str(list(code_tag)[0].text)
            taf_raw = ''
            
        else:          # Checking if the bs4 element even contains anything
            metar_raw = ''
            taf_raw = ''
'''        
        
        # split returns into list form for further processing.
        # metar = metar_raw.split()
        # taf = taf_raw.split()
        # print((taf_raw))
        return dict({'metar': metar_raw, 'taf': taf_raw})

    

# weather_display = Weather_display()
# met_taf = weather_display.scrape('kewr')

# print(met_taf)

'''
while True:

    # Asking User prompt what they want.
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
'''
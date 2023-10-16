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
        awc_metar_api = f"https://beta.aviationweather.gov/cgi-bin/data/metar.php?ids={airport_id}"
        metar_raw = requests.get(awc_metar_api)
        metar_raw = metar_raw.content
        metar_raw = metar_raw.decode("utf-8")
        
        awc_taf_api = f"https://beta.aviationweather.gov/cgi-bin/data/taf.php?ids={airport_id}"
        taf_raw = requests.get(awc_taf_api)
        taf_raw = taf_raw.content
        taf_raw = taf_raw.decode("utf-8")
        taf_raw = taf_raw.replace("FM", "<br>\xa0\xa0\xa0\xa0FM")   # line break for FM section in TAF
        
        """
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
            
            taf_raw = taf_raw.replace("FM", "<br>\xa0\xa0\xa0\xa0FM")   # line break for FM section in TAF
            
        elif len(metar_and_taf_in_bs4_list) == 1:       # if only METAR is available which is the first and only item
            metar_raw = str(list(code_tag)[metar_index].text)
            taf_raw = 'NA'
        else:                                           # if neither are available
            metar_raw = 'NA'
            taf_raw = 'NA'
        
        """
        # metar = metar_raw.split()     # split returns into list form for further processing.
        # taf = taf_raw.split()
        # print((taf_raw))
        
        return dict({'METAR': metar_raw, 'TAF': taf_raw})


    
# To check code locally use this:
# icao_id = 'kewr'
# weather_display = Weather_display()
# met_taf = weather_display.scrape('icao_id')

# print(met_taf)

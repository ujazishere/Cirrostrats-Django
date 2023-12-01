import re
import pickle
from bs4 import BeautifulSoup as bs4
import requests
import json
# from data_access import load_kewr
# kewr = load_kewr()

# TODO: extract all airpoirts METAR and TAF  in the airport database
            # compare all unique values and group identical ones
            # analyze data for format patterns to make a template for output

class Weather_display:
    def __init__(self) -> None:
        self.pink_text_color = r'<span class="pink_text_color">\1\2</span>'
        self.red_text_color = r'<span class="red_text_color">\1\2</span>'
        self.red_highlight = r'<span class="highlight-red">\1\2</span>'
        
        # first digit between 1-2 then space all of it optional. Then digit and fwrd slash optional then digit then SM
        self.SM_PATTERN = r"([1-2] )?(\d/)?(\d)?(\d)(SM)"
        self.SM_PATTERN = r"([1-2] )?(\d/)?(\d)(SM)"    
        self.BKN_OVC_PATTERN_LIFR = r"(BKN|OVC)(00[0-4])"   # BKN or OVC,first two digit `0`, 3rd digit btwn 0-4
        self.BKN_OVC_PATTERN_IFR = r"(BKN|OVC)(00[5-9])"    # BKN/OVC below 10 but above 5
        self.BKN_OVC_PATTERN_alternate = r"(BKN|OVC)(0[1][0-9])"         # Anything and everything below 20

    
    def scrape(self, query=None,dummy=None):
        
        if dummy:
            
            datis_raw = dummy['D-ATIS']
            metar_raw = dummy['METAR']
            taf_raw = dummy['TAF']
            # print('RAW DUMMY WEATHER', dummy)

        else:
        # Find ways to convert raw query input into identifiable airport ID
            airport_id = query
            awc_metar_api = f"https://aviationweather.gov/api/data/metar?ids={airport_id}"
            metar_raw = requests.get(awc_metar_api)
            metar_raw = metar_raw.content
            metar_raw = metar_raw.decode("utf-8")
            metar_list_form = metar_raw.split()
            for each_item in metar_list_form:
                if 'SM' in each_item and each_item[0] != 'K' and each_item != '10SM':
                    pass
                # The logic is if forward slash exists e.g `1/2SM` then look for previous item.
                    # if previous item is contains single `1` or `2` then its a visibility
                    # ([1-2] )(\d/)?(\d)(SM) This regex is for 
                    
            
            awc_taf_api = f"https://aviationweather.gov/api/data/taf?ids={airport_id}"
            taf_raw = requests.get(awc_taf_api)
            taf_raw = taf_raw.content
            taf_raw = taf_raw.decode("utf-8")

            datis_api =  f"https://datis.clowd.io/api/{airport_id}"
            datis = requests.get(datis_api)
            datis = json.loads(datis.content.decode('utf-8'))
            datis_raw = 'N/A'
            if type(datis) == list and 'datis' in datis[0].keys():
                datis_raw = datis[0]['datis']
        

        # Exporting raw weather data for color code processing
        # raw_weather_dummy_data = { 'D-ATIS': datis_raw, 'METAR': metar_raw, 'TAF': taf_raw} 
        # with open(f'raw_weather_dummy_data{airport_id}.pkl', 'wb') as f:
            # print(f"DUMPING RAW WEATHER DATA")
            # pickle.dump(raw_weather_dummy_data, f)

        # LIFR PAttern >>> Anything below 5 to pink
        low_ifr_metar = re.sub(self.BKN_OVC_PATTERN_LIFR, self.pink_text_color, metar_raw)
        # LIFR pattern >>> anything below 5 to pink
        low_ifr_taf = re.sub(self.BKN_OVC_PATTERN_LIFR, self.pink_text_color, taf_raw)


        # IFR Pattern
        ifr_metar = re.sub(self.BKN_OVC_PATTERN_IFR, self.red_text_color, low_ifr_metar)
        # IFR pattern
        
        ifr_taf = re.sub(self.BKN_OVC_PATTERN_IFR, self.red_text_color, low_ifr_taf)

        # original metar alternate text color >> NEED HIGHLIGHT FOR ANYTHING BELOW 20
        highlighted_metar = re.sub(self.BKN_OVC_PATTERN_alternate, self.red_highlight, ifr_metar)
        
        # original taf alternate text color
        highlighted_taf = re.sub(self.BKN_OVC_PATTERN_alternate, self.red_highlight, ifr_taf)
        highlighted_taf = highlighted_taf.replace("FM", "<br>\xa0\xa0\xa0\xa0FM")   # line break for FM section in TAF for HTML
        print(highlighted_metar,'\n\n', highlighted_taf)



        return dict({ 'D-ATIS': datis_raw, 'METAR': highlighted_metar, 'TAF': highlighted_taf})

import re
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
        self.red_highlight_html = r'<span class="highlight-red">\1\2</span>'
        self.red_font_html = r'<span class="font-red">\1\2</span>'
        self.pinkk_font_html = r'<span class="font-pink">\1\2</span>'
        
        # first digit between 1-2 then space all of it optional. Then digit and fwrd slash optional then digit then SM
        self.SM_PATTERN = r"([1-2] )?(\d/)?(\d)(SM)"    
        self.BKN_OVC_PATTERN_LIFR = r"(BKN|OVC)(00[0-4])"   # BKN or OVC,first two digit `0`, 3rd digit btwn 0-4
        self.BKN_OVC_PATTERN_IFR = r"(BKN|OVC)(00[5-9])"
        self.BKN_OVC_PATTERN_alternate = r"(BKN|OVC)(0[0-1]\d)"

    
    def scrape(self, query=None):
        
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


        highlighted_metar = re.sub(self.BKN_OVC_PATTERN_alternate, self.red_highlight_html, metar_raw)

        highlighted_taf = re.sub(self.BKN_OVC_PATTERN_alternate, self.red_highlight_html, taf_raw)
        highlighted_taf = highlighted_taf.replace("FM", "<br>\xa0\xa0\xa0\xa0FM")   # line break for FM section in TAF for HTML

        return dict({ 'D-ATIS': datis_raw, 'METAR': highlighted_metar, 'TAF': highlighted_taf})

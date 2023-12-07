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
        self.yellow_highlight = r'<span class="yellow_highlight">\1\2</span>'
        self.box_around_text = r'<span class="box_around_text">\1\2</span>'         # Change name to `box_around_text`

        # first digit between 1-2 then space all of it optional. Then digit and fwrd slash optional then digit then SM
        self.lifr_fractional_patt = r'((?<! \d ))((M)?\d/(\d)?\dSM)'        # Just the fractional pattern
        self.ifr_fractional_patt = r'((?<!\d))(([0-2] )(\d/\d{1,2})SM)'
        self.lifr_single_or_douple = r'((?<= )0?)(0SM)'
        self.ifr_single_or_douple = r'((?<= )0?)([1,2]SM)'

        self.SM_PATTERN = r"( [1-2] )?(\d/)?(\d)?(\d)(SM)"       # Matches all Visibilities with trailing SM
        self.SM_PATTERN_fractions = r"([0-2] )?(\d/\d{1,2})SM"          # maps fractional visibilities between 1 and 3
        self.SM_PATTERN_two_digit = r"^[0-9]?[0-9]SM"          # valid 1 and 2 digit visibility
        self.SM_PATTERN_one_digit_ifr = r"^[0-2]SM"          # 0,1 and 2 SM only
        
        self.BKN_OVC_PATTERN_LIFR = r"(BKN|OVC)(00[0-4])"   # BKN or OVC,first two digit `0`, 3rd digit btwn 0-4
        self.BKN_OVC_PATTERN_IFR = r"(BKN|OVC)(00[5-9])"    # BKN/OVC below 10 but above 5
        self.BKN_OVC_PATTERN_alternate = r"(BKN|OVC)(0[1][0-9])"         # Anything and everything below 20

        self.ALTIMETER_PATTERN = r"((?<= )A)(\d{4})"
        self.FREEZING_TEMPS = r'(00|M\d\d)(/M?\d\d)'
        self.ATIS_INFO = r"(DEP|ARR|ARR/DEP|ATIS)( INFO [A-Z])"

        self.RW_IN_US = r'(ARRIVALS EXPECT|SIMUL|RUNWAYS|VISUAL|RNAV|ILS(,|RY|))(.*?)\.'

    def visibility_color_code(self,incoming_weather_data):

        lifr_frac = re.sub(self.lifr_fractional_patt, self.pink_text_color,incoming_weather_data)
        ifr_frac = re.sub(self.ifr_fractional_patt, self.red_text_color,lifr_frac)
        lifr_digits = re.sub(self.lifr_single_or_douple,self.pink_text_color,ifr_frac)
        ifr_digits = re.sub(self.ifr_single_or_douple,self.red_text_color,lifr_digits)
        processed_incoming_data = ifr_digits



        if processed_incoming_data:
            return processed_incoming_data
        else:
            print('Nothing to process in visibility_work_func')
            return incoming_weather_data
        


    def scrape(self, query=None,dummy=None):
        
        if dummy:
            
            datis_raw = dummy['D-ATIS']
            metar_raw = dummy['METAR']
            taf_raw = dummy['TAF']
            # print('RAW DUMMY WEATHER', dummy)
            vis1 = 'FM030500 09004KT 00SM -RA BR OVC004'
            vis_frac = 'FM031300 19005KT 1 1/2SM BR OVC004'
            
            datis_raw = datis_raw + vis1 + vis_frac 
            # taf_raw = metar_raw + sfc_vis + vis_half
            taf_raw = 'KRIC 022355Z 0300/0324 00000KT 2SM BR VCSH FEW015 OVC060 TEMPO 0300/0303 1 1/2SM FG BKN015 FM030300 00000KT 1SM -SHRA FG OVC002 FM031300 19005KT 3/4SM BR OVC004 FM031500 23008KT 1/26SM OVC005 FM031800 25010KT 1/4SM OVC015 FM032100 25010KT M1/4SM BKN040'

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

        # LIFR PAttern for ceilings >>> Anything below 5 to pink METAR
        low_ifr_metar_ceilings = re.sub(self.BKN_OVC_PATTERN_LIFR, self.pink_text_color, metar_raw)
        # LIFR pattern for ceilings >>> anything below 5 to pink TAF 
        low_ifr_taf_ceilings = re.sub(self.BKN_OVC_PATTERN_LIFR, self.pink_text_color, taf_raw)
        # LIFR pattern for ceilings >>> anything below 5 to pink DATIS 
        low_ifr_datis_ceilings = re.sub(self.BKN_OVC_PATTERN_LIFR, self.pink_text_color, datis_raw)


        # IFR Pattern for ceilings METAR
        ifr_metar_ceilings = re.sub(self.BKN_OVC_PATTERN_IFR, self.red_text_color, low_ifr_metar_ceilings)
        # IFR pattern for ceilings TAF
        ifr_taf_ceilings = re.sub(self.BKN_OVC_PATTERN_IFR, self.red_text_color, low_ifr_taf_ceilings)
        # IFR pattern for ceilings DATIS
        ifr_datis_ceilings = re.sub(self.BKN_OVC_PATTERN_IFR, self.red_text_color, low_ifr_datis_ceilings)
        
        # ACCOUNT FOR VISIBILITY `1 /2 SM`  mind the space in betwee. SCA had this in TAF and its not accounted for.

        # LIFR PAttern for visibility >>> Anything below 5 to pink METAR
        lifr_ifr_metar_visibility = self.visibility_color_code(ifr_metar_ceilings)
        # LIFR pattern for visibility >>> anything below 5 to pink TAF 
        lifr_ifr_taf_visibility = self.visibility_color_code(ifr_taf_ceilings)
        # LIFR pattern for visibility >>> anything below 5 to pink DATIS 
        lifr_ifr_datis_visibility = self.visibility_color_code(ifr_datis_ceilings)

        # original metar alternate for ceilings text color >> NEED HIGHLIGHT FOR ANYTHING BELOW 20
        highlighted_metar = re.sub(self.BKN_OVC_PATTERN_alternate, self.yellow_highlight, lifr_ifr_metar_visibility)

        # original taf alternate for ceilings text color
        highlighted_taf = re.sub(self.BKN_OVC_PATTERN_alternate, self.yellow_highlight, lifr_ifr_taf_visibility)
        highlighted_taf = highlighted_taf.replace("FM", "<br>\xa0\xa0\xa0\xa0FM")   # line break for FM section in TAF for HTML
        highlighted_datis = re.sub(self.BKN_OVC_PATTERN_alternate, self.yellow_highlight, lifr_ifr_datis_visibility)

        highlighted_datis = re.sub(self.ATIS_INFO, self.box_around_text, highlighted_datis)
        highlighted_datis = re.sub(self.ALTIMETER_PATTERN, self.box_around_text, highlighted_datis)
        highlighted_metar = re.sub(self.ALTIMETER_PATTERN, self.box_around_text, highlighted_metar)

        print(highlighted_metar)
        return dict({ 'D-ATIS': highlighted_datis, 'METAR': highlighted_metar, 'TAF': highlighted_taf})
        

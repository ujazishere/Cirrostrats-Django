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
        self.SM_PATTERN = r"( [1-2] )?(\d/)?(\d)?(\d)(SM)"       # Matches all Visibilities with trailing SM
        self.SM_PATTERN_fractions = r"([0-2] )?(\d/\d{1,2})SM"          # maps fractional visibilities between 1 and 3
        self.SM_PATTERN_two_digit = r"^[0-9]?[0-9]SM"          # valid 1 and 2 digit visibility
        self.SM_PATTERN_one_digit_ifr = r"^[0-2]SM"          # 0,1 and 2 SM only
        self.BKN_OVC_PATTERN_LIFR = r"(BKN|OVC)(00[0-4])"   # BKN or OVC,first two digit `0`, 3rd digit btwn 0-4
        self.BKN_OVC_PATTERN_IFR = r"(BKN|OVC)(00[5-9])"    # BKN/OVC below 10 but above 5
        self.BKN_OVC_PATTERN_alternate = r"(BKN|OVC)(0[1][0-9])"         # Anything and everything below 20

    def visibility_work(self,incoming_weather_data):
        """
        import re
        incoming_weather_data = 'KRIC 022355Z 10SM 0300/0324 00000KT 2SM BR VCSH FEW015 OVC060 TEMPO 0300/0303 1 1/2SM FG BKN015 FM030300 00000KT 1SM -SHRA FG OVC002 FM031300 19005KT 3/4SM BR OVC004 FM031500 23008KT 1/26SM OVC005 FM031800 25010KT 1/4SM OVC015 FM032100 25010KT M1/4SM BKN040'
        SM_PATTERN = r"( [1-2] )?(\d/)?(\d)?(\d)(SM)"       # Matches all Visibilities with trailing SM
        visibility_pattern = re.findall(SM_PATTERN, incoming_weather_data)
        [''.join(i) for i in visibility_pattern]

        """        

        def replacement(weather_raw_in, color_code, pattern_in):

            # weather_raw_in is the preprocessed metar taf or datis.
            # Replace color_code pattern with visibility pattern in it.
            # Find regex pattern in the data_in. replace data that data_in visibility with processed color coded one
            
            local_color_code = str(color_code)
            weather_raw_in = str(weather_raw_in)
            
            color_coded_pattern = local_color_code.replace(r'\1\2',pattern_in)

            package_to_send = weather_raw_in.replace(pattern_in, color_coded_pattern)

            return package_to_send


        # CAUTION!!! SM_PATTERN takes into account all SM visibilities including ***leading empty space*** for fractionals
        visibility_pattern = re.search(self.SM_PATTERN, incoming_weather_data)
        # Do not use it for replacement in the fractional processing since thats where it might contains leading empty space.

        processed_incoming_data = None      # Declaring variable for error handling
        if visibility_pattern:

            visibility_pattern = visibility_pattern.group()
            print(visibility_pattern)
            fractional_item = re.search(self.SM_PATTERN_fractions, visibility_pattern)

            # First 4 {1,2} digit LIFR vis. Last 2 are IFR
            lifr_and_ifr_vis = ['00SM','01SM','0SM','1SM', '02SM', '2SM']       
            
            
            if fractional_item:     # CAUTION!!! Contains leading empty space.
                if len(fractional_item.group().split()) == 1:       # This is certainly LIFR
                    processed_incoming_data = replacement(incoming_weather_data, self.pink_text_color, fractional_item.group())
                    print('LIFR!!! found LIFR base fractional', fractional_item.group())

                elif len(fractional_item.group().split()) > 1:      # This is IFR. Contains btween 1 and >3 SM in fractions
                    # This is the fraction with leading empty space.
                    processed_incoming_data = replacement(incoming_weather_data, self.red_text_color, fractional_item.group())
                    print('IFR!!! Found leading empty space fractional', fractional_item.group())

            elif visibility_pattern in lifr_and_ifr_vis:        # If not a fractional it is one or two digit SM and does not contain leading empty space
                if visibility_pattern in lifr_and_ifr_vis[:4]:
                    # This is L-IFR {1,2} digits SM only
                    processed_incoming_data = replacement(incoming_weather_data, self.pink_text_color, visibility_pattern)
                    print('LIFR! {1,2} digit SM', visibility_pattern)
                else:
                    # This is IFR {1,2} diggits SM Only
                    processed_incoming_data = replacement(incoming_weather_data, self.pink_text_color, visibility_pattern)
                    print('IFR! {1,2} digit SM', visibility_pattern)
        print('processed data', processed_incoming_data)
        if processed_incoming_data:
            return processed_incoming_data
        else:
            return incoming_weather_data
        

    
    def scrape(self, query=None,dummy=None):
        
        if dummy:
            
            datis_raw = dummy['D-ATIS']
            metar_raw = dummy['METAR']
            taf_raw = dummy['TAF']
            # print('RAW DUMMY WEATHER', dummy)
            vis1 = 'FM030500 09004KT 1SM -RA BR OVC004'
            vis_frac = 'FM031300 19005KT 1 1/2SM BR OVC004'
            sfc_vis = 'IAD 030102Z 17003KT 0SM R01R/2800V4000FT FG VV002 11/10 A2999 RMK AO2 SFC VIS 1/4 T01110100 $'
            vis_half = 'FM031000 07004KT 1/2SM -RA FG OVC003'
            vis_half = 'FM031000 07004KT 1 1/2SM -RA FG OVC003'
            
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
        lifr_ifr_metar_visibility = self.visibility_work(ifr_metar_ceilings)
        # LIFR pattern for visibility >>> anything below 5 to pink TAF 
        lifr_ifr_taf_visibility = self.visibility_work(ifr_taf_ceilings)
        # LIFR pattern for visibility >>> anything below 5 to pink DATIS 
        lifr_ifr_datis_visibility = self.visibility_work(ifr_datis_ceilings)

        # original metar alternate for ceilings text color >> NEED HIGHLIGHT FOR ANYTHING BELOW 20
        highlighted_metar = re.sub(self.BKN_OVC_PATTERN_alternate, self.red_highlight, lifr_ifr_metar_visibility)

        # original taf alternate for ceilings text color
        highlighted_taf = re.sub(self.BKN_OVC_PATTERN_alternate, self.red_highlight, lifr_ifr_taf_visibility)
        highlighted_taf = highlighted_taf.replace("FM", "<br>\xa0\xa0\xa0\xa0FM")   # line break for FM section in TAF for HTML
        highlighted_datis = re.sub(self.BKN_OVC_PATTERN_alternate, self.red_highlight, lifr_ifr_datis_visibility)

        


        return dict({ 'D-ATIS': highlighted_datis, 'METAR': highlighted_metar, 'TAF': highlighted_taf})
        

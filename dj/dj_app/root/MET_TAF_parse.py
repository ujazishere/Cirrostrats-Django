import re
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
        awc_metar_api = f"https://aviationweather.gov/api/data/metar?ids={airport_id}"
        metar_raw = requests.get(awc_metar_api)
        metar_raw = metar_raw.content
        metar_raw = metar_raw.decode("utf-8")
        
        awc_taf_api = f"https://aviationweather.gov/api/data/taf?ids={airport_id}"
        taf_raw = requests.get(awc_taf_api)
        taf_raw = taf_raw.content
        taf_raw = taf_raw.decode("utf-8")
        print(taf_raw)

        ismail_work = r'<span class="highlight-red">\1\2</span>'

        highlighted_taf = re.sub(r'(BKN|OVC)(0[0-1]\d)', ismail_work, taf_raw)
        highlighted_taf = highlighted_taf.replace("FM", "<br>\xa0\xa0\xa0\xa0FM")   # line break for FM section in TAF for HTML
        print(highlighted_taf)
        return dict({'METAR': metar_raw, 'TAF': highlighted_taf})

from .root_class import Root_class

class Newark_departures_scrape(Root_class):
    
    def __init__(self) -> None:
            pass


    def newark_deps(self):
        print('working on united departures out of Newark')
        # morning = '?tp=6'         # When its late in night and you want to run lengthy scrape it wont work since
                                        # there are no flights. Use this morning to pull early morning flights instead
        morning = ''
        EWR_deps_url = f'https://www.airport-ewr.com/newark-departures{morning}'

        # TODO: web splits time in 3 parts.
                # Makes it harder to pick appropriate information about flights
                # from different times of the date

        
        soup = self.request(EWR_deps_url)
        raw_bs4_all_EWR_deps = soup.find_all('div', class_="flight-col flight-col__flight")[1:]
        # TODO: raw_bs4_html_ele contains delay info. Get delayed flight numbers
        # raw_bs4_html_ele = soup.find_all('div', class_="flight-row")[1:]

        #  This code pulls out all the flight numbers departing out of EWR
        all_EWR_deps = []
        for index in range(len(raw_bs4_all_EWR_deps)):
            for i in raw_bs4_all_EWR_deps[index]:
                if i != '\n':
                    all_EWR_deps.append(i.text)
        
        return all_EWR_deps


    def united_departures(self):
        # returns list of all united flights as UA**** each
        # Here we extract raw united flight number departures from airport-ewr.com
        
        all_EWR_deps = self.newark_deps()
        # extracting all united flights and putting them all in list to return it in the function.
        united_departures_newark =[each for each in all_EWR_deps if 'UA' in each]
        print('Successfully pulled United departures out of Newark at', self.date_time())
        print(f'Total United departures: {len(united_departures_newark)}')
        
        return united_departures_newark

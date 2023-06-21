# from flt_deet import airports
from root_class import Root_class

# print(len(airports))

class Cirrum(Root_class):
    def __init__(self) -> None:
        super().__init__()

    def pull_cis(self):
        info = "https://united-airlines.flight-status.info/ua-1232"
        soup = self.request(info)

        # table = soup.find('div', {'class': 'a2'})
        distane_and_duration = soup.find('ul', {'class': 'a3_n'})
        distance_duration = [i.text for i in distane_and_duration if 'Flight D' in i.text]
        duration = distance_duration[0]
        distance = distance_duration[1]
        # airport_name = soup.find('div', {'class': 'a2_a'})
        airport_id = soup.find_all('div', {'class': 'a2_ak'})
        airport_id = [i.text for i in airport_id if 'ICAO' in i.text]
        departure_ID = airport_id[0].split()[2]
        destination_ID = airport_id[1].split()[2]
        
        times = soup.find_all('div', {'class': 'a2_b'})          # scheduled and actual times in local time zone
        times = [i.text for i in times if 'Scheduled' in i.text]
        departure_times = ' '.join(times[0].replace('\n','').split())
        destination_times = ' '.join(times[1].replace('\n','').split())
        
        gate = soup.find_all('div', {'class': 'a2_c'})
        gate = [i.text.replace('\n', '') for i in gate]
        departure_gate = gate[0]
        destination_gate = gate[1]
        # time = soup.find('div', {'class': 'a2_b'})


        return [departure_ID, destination_ID, 
                 duration, distance, 
                 departure_times, destination_times,
                 departure_gate, destination_gate]
    

cir = Cirrum()
print(cir.pull_cis())

    
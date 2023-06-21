# from flt_deet import airports
from root_class import Root_class

# print(len(airports))

class Cirrum(Root_class):
    def __init__(self) -> None:
        super().__init__()

    def pull_cis(self):
        info = "https://united-airlines.flight-status.info/ua-492"
        soup = self.request(info)

        # table = soup.find('div', {'class': 'a2'})
        distane_and_duration = soup.find('ul', {'class': 'a3_n'})

        # airport_name = soup.find('div', {'class': 'a2_a'})
        airport_id = soup.find('div', {'class': 'a2_ak'})
        time = soup.find('div', {'class': 'a2_b'})          # scheduled and actual times in local time zone
        gate = soup.find('div', {'class': 'a2_c'})
        # time = soup.find('div', {'class': 'a2_b'})


        juice = [gate, time,]

        return distane_and_duration 
    

cir = Cirrum()
print(cir.pull_cis())

    
import pickle
import os
from .weather_parse import Weather_parse

def getting_the_path_right():
    
    currentWorking = os.getcwd()
    print("currentWorking through dummy_files_call.py",currentWorking)
    luis_trailing_path = "Cirrostrats"      # TODO: On UJ's system apparently Luis' path is being returned. Fix it
    uj_trailing_path = r"Cirrostrats\dj"
    ismail_trailing_path = "Cirrostrats/dj/"

    if currentWorking[-11:] == luis_trailing_path:
        path_to_be_used = currentWorking + "/dj/"
        print('Maybe Luis path:', path_to_be_used)
    elif currentWorking[-14:] == uj_trailing_path:
        path_to_be_used = currentWorking + "\\"       # Caution! Escape char issue with `\` Windows path
        print('Maybe UJ path:', path_to_be_used)
    elif currentWorking[-14:] == ismail_trailing_path or currentWorking:  # This could be just `else` but elaborate for situational awareness.
        path_to_be_used = currentWorking + "/"        # linux path
        print('Maybe Ismail path or others:', path_to_be_used)

    # ismail = r"/Users/ismailsakhani/Desktop/Cirrostrats/dj/"
    # ujas = r"C:\Users\ujasv\OneDrive\Desktop\codes\Cirrostrats\dj\\"

    return path_to_be_used


def test_data_imports():
    path_to_be_used = getting_the_path_right()   
    
    # nas_data, summary box, weather_data, and dummy function takes this dummy bulk_flight_deets to the front end.
    
    def pickle_imports_and_processing():
        # TODO: Need to account for titles for dep and dest that has time gate and airport id.

        bulk_flight_deets_path = path_to_be_used + r"test_flight_deets_data.pkl"
        bulk_flight_deets = pickle.load(open(bulk_flight_deets_path, 'rb'))

        # IFR and LIFR weather for departure and destination.
        ind = path_to_be_used + r"raw_weather_dummy_dataKIND.pkl"
        ord = path_to_be_used + r"raw_weather_dummy_dataKORD.pkl"
        with open(ind, 'rb') as f:
            dep_weather = pickle.load(f)
        with open(ord, 'rb') as f:
            dest_weather = pickle.load(f)

        # Injesting the html/css for highlighting here.
        weather = Weather_parse()
        bulk_flight_deets['dep_weather'] = weather.processed_weather(
            dummy=dep_weather)
        weather = Weather_parse()
        bulk_flight_deets['dest_weather'] = weather.processed_weather(
            dummy=dest_weather)


        # These seperate out all the weather for ease of work for design. for loops are harder to work with in html so..
        # sending the data as individuals rather than nested dictionaries.
        def weather_separation_process():
            dep_atis = bulk_flight_deets['dep_weather']['D-ATIS']
            dep_metar = bulk_flight_deets['dep_weather']['METAR']
            dep_taf = bulk_flight_deets['dep_weather']['TAF']
            bulk_flight_deets['dep_datis'] = dep_atis
            bulk_flight_deets['dep_metar'] = dep_metar
            bulk_flight_deets['dep_taf'] = dep_taf
            
            dest_datis = bulk_flight_deets['dest_weather']['D-ATIS']
            dest_metar = bulk_flight_deets['dest_weather']['METAR']
            dest_taf = bulk_flight_deets['dest_weather']['TAF']
            bulk_flight_deets['dest_datis'] = dest_datis
            bulk_flight_deets['dest_metar'] = dest_metar
            bulk_flight_deets['dest_taf'] = dest_taf
            return bulk_flight_deets
        return weather_separation_process(),dep_weather,dest_weather

    data_return = pickle_imports_and_processing()
    return data_return


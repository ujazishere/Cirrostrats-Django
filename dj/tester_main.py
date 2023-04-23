import pickle

futures_dict = {}


pick_data = {
            'UA1212': ['C71', '8am', '10pm'],
            'UA1212': ['C72', '8am', '10pm'],
            'DL1234': ['C72', '8am', '10pm'], 
                }


with open('united_flts', 'rb') as f:
    flights = pickle.load(f)

more_flights = ['UA1212', 'DL1234', 'UA2222']


with open('united_flts.pkl', 'wb') as f:
    for i in flights:
        pickle.dump(i, f)
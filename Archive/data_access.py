import pickle


def load_kewr():
    with open(r'C:\Users\ujasv\OneDrive\Desktop\codes\Weather_work\pkl\kewr.pkl', 'rb') as f:
        kewr = pickle.load(f)
    return kewr


# print(kewr)

# with open('pkl/cities.pkl', 'rb') as f:
#     cities = pickle.load(f)

# print(cities)

# with open('pkl/cit_url.pkl', 'rb') as x:
#     cit_url = pickle.load(x)


# print(cit_url)

airport_id = ['EWR', 'ORD']
flight_code = {4421, 4409, 4449, 4403, 4465, 4444}  # You can only put in 4-digit code for united only
two_digit_airline = ['UA', 'AD', 'NZ', ]

flight_gates = f"https://www.flightview.com/flight-tracker/{two_digit_airline}/{flight_code}?date={'20230315'}&depapt={airport_id}"

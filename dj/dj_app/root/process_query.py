
def airlineCodeQueryParse(one_word_query):
    if one_word_query[0] == 'G':     # if GJS instead of UA: else its UA
        # Its GJS
        airline_code, flt_digits = one_word_query[:3], one_word_query[3:]
    else:           # Its UA
        flt_digits = one_word_query[2:]
        airline_code = None
        if one_word_query[:3] ==  'UAL':
            airline_code = 'UAL'
            flt_digits = one_word_query[3:]
        elif one_word_query[:2] == 'UA':
            airline_code = 'UA'

        gjs_flight_nums = range(4000, 5000)
        if int(flt_digits) in gjs_flight_nums:
            print('GJS flight query, since digit_query is between 4000 and 5000, flt_digits:', flt_digits)
            airline_code = 'GJS'
        else:
            print('NOT A GJS flight query. flt_digits:', flt_digits)
    return airline_code,flt_digits

# async def process_query(request, query):
#     query = query.upper()

#     if query.startswith(('UA', 'GJS', 'UAL')):
#         return await process_airline_query(request, query)

#     if len(query) <= 4:
#         return process_short_query(request, query)

#     return process_multi_word_query(request, query)

# async def process_airline_query(request, query):
#     if query.startswith('GJS'):
#         airline_code, flight_number = query[:3], query[3:]
#     elif query.startswith('UAL'):
#         airline_code, flight_number = 'UAL', query[3:]
#     else:  # UA
#         airline_code, flight_number = 'UA', query[2:]

#     print('\nSearching for:', airline_code, flight_number)
#     return await flight_deets(request, airline_code=airline_code, flight_number_query=flight_number)

# def process_short_query(request, query):
#     if query.isdigit():
#         num = int(query)
#         if 1 <= num <= 35 or 40 <= num <= 136:
#             return gate_info(request, main_query=str(num))
#         else:
#             print("INITIATING flight_deets FUNCTION.")
#             return flight_deets(request, airline_code=None, flight_number_query=num)
#     elif len(query) == 4 and query.startswith('K'):
#         return weather_info(request, query)
#     else:
#         print('gate query')
#         return gate_info(request, main_query=query)

# def process_multi_word_query(request, query):
#     words = query.split()
#     if words[0] == 'W':
#         return weather_info(request, words[1])
#     else:
#         return gate_info(request, main_query=query)
from .root_class import Root_class


# this class subclassess Root_class that creates instance variables of the subclass and inherits its methods
class Gate_checker(Root_class):
    
    def __init__(self,):

        # super method inherits all of the instance variables of the Gate_root class.
        super().__init__()


    def ewr_UA_gate(self, query=None):
        # Stacking query items together
        master = self.load_master()
        flights = []
        for flt_num, values in master.items():
            gate = values[0]
            scheduled = values[1]
            actual = values[2]
            
            if f'{query}' in gate:
                flights.append({
                    'gate': gate,
                    'flight_number': flt_num,
                    'scheduled': scheduled,
                    'actual': actual,
                })

        # Sorts the date by 'scheduled' in descending order to get the latest date and time to the top
        flights = sorted(flights, key=lambda x:x['scheduled'], reverse=True)

        # Converting it back to string for it to show in a viewable format otherwise
            # browser craps out when it sees class object for date since earlier 'scheduled' item is a class object and not a string
        for dictionries in flights:
            dictionries['scheduled'] = dictionries['scheduled'].strftime("%#H:%M, %b%d")
            dictionries['actual'] = dictionries['actual'].strftime("%#H:%M, %b%d")
        
        return flights
    
    
'''
    
    def structured_flights(self):
        master = self.load_master()
        structured_flights = []
        outlaws_reliable = []
        outlaws_unreliable = []
        # issue: too many values to unpack. Solution: unpack keys and values, use regex to make sure flight number matches.
        for flight_num, values in master.items():
            
            # TODO: Move reliable flightnumbers regex to Gate_scrape class to make data reliable at source.
            # Regex that matches 2 uppercase alphabets followed by digits between 2 and 4.
            reliable_flt_num = re.match(r'[A-Z]{2}\d{2,4}', flight_num)
            # if len(reliable_flt_num) != len(flight_num):
            # if flight number is reliable and the associated values is exactly 3(i.e gate, schd, act) then;
                # else outlaws_unreliable
            if reliable_flt_num and len(values) == 3:
                
                # its important that these values are nested in here since if the flight number is reliable these 3 values will exist.
                gate = values[0]
                scheduled = values[1]
                actual = values[2]
                # TODO: this 'not available' might not be the most reliable way to check for reliable data.
                    # Earlier I used `if self.dt_conversion(scheduled) and actual`` but
                        # it spat out nasty errors so wont be using it.
                if "Terminal" in gate and scheduled!= 'Not Available' and actual!= 'Not Available':
                    scheduled = self.dt_conversion(scheduled)
                    actual = self.dt_conversion(actual)
                    structured_flights.append({
                        'gate': gate,
                        'flight_number': flight_num,
                        'scheduled': scheduled,
                        'actual': actual,
                    })
                else:
                    # TODO: Have to deal with these outlaws and feed it back into the system.
                        # Sometimes gate goes into scheduled or actual. Beware of that kind of data.
                    outlaws_reliable.append({
                        'flight_number': flight_num,
                        'gate': gate,
                        'scheduled': scheduled,
                        'actual': actual,
                    })
            
            else:
                outlaws_unreliable.append(dict({"flight_number": flight_num, "values": values}))
        
        # print('outlaws_reliable', 'gt', gate,  scheduled, actual)
        print('outlaws_reliable and outlaws_unreliable:', len(outlaws_reliable), len(outlaws_unreliable))
        
        outlaws = dict({
            self.date_time() : [dict({'reliable_outlaws':outlaws_reliable,'unreliable_outlaws':outlaws_unreliable})]
        })
        
        with open('outlaws.pkl', 'rb') as f:
            outlaws_read = pickle.load(f)
        
        outlaws_read.update(outlaws)    #calling outlaws and updating it, then dumping it again to previous old data.
        
        # Better if the file is read, extracted and appended to extracted as a new file.
        with open('outlaws.pkl', 'wb') as f:
            pickle.dump(outlaws_read, f)

        return structured_flights'''


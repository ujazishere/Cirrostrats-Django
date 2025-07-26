from datetime import datetime
import datetime as dt

import pytz
from .root_class import Root_class
from .database import db_UJ


# this class subclassess Root_class that creates instance variables of the subclass and inherits its methods
class Gate_checker(Root_class):
    
    def __init__(self,):

        # super method inherits all of the instance variables of the Gate_root class.
        super().__init__()

        self.old_data_detected = False


    def old_data_detection(self, master):
        ''' Detects old data in gate returns and sends an email to UJ if any is found. '''
        # Account for EST time zone since date data is in EST - UTC Failsafe.
        eastern = pytz.timezone('US/Eastern')
        yesterday = datetime.now(eastern).date()+dt.timedelta(days=-1)

        # Reason for this mmdd format is that date in data doesn't have a year in it.
        yesterday_mmdd = yesterday.strftime("%m%d")
        # print('astime',eastern)
        print('currently ',datetime.now(eastern), '\nyesterday', yesterday, '\nyesterday_mmdd', yesterday_mmdd)

        old_data_collection = []
        for i in master.keys():
            data_mmdd = master[i][1].strftime("%m%d")
            # print('yesterday_mmdd', yesterday_mmdd,data_mmdd )
            if data_mmdd <= yesterday_mmdd:         # if data is older than or equal to yesterday's date
                old_data = (i, master[i][0])        # get flight number and gate and append it to collection
                old_data_collection.append(old_data)
        if old_data_collection:
            # Root_class().send_email(body_to_send=f'!!! Detected old data in gate returns when user made gate query--. {old_data_collection}')
            self.old_data_detected = True
        else:
            self.old_data_detected = False
        


    def ewr_UA_gate(self, query=None):
        """ *** Function Depricated *** """

        # This function loads the gate_query_database.pkl pickle file that is a dictionary with keys as 
            # flight numbers out of newark and values as their gate and times.
            # It filters per users query, sorts by date then returns as list. A list of dicts.
            # Check gate scrape for actual data fetch and filter mechanish

        # TODO: Update actual more frequently and scheduled less frequently to get delayed flights info. maybe couple times a day for scheduled.
            # Scheduled ones are usually very much planned. Drawback-repo and non-scheduled ones wont show up as promptly.
            # Highlight late ones in red
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
        
        
        # This is failsafe to detect old data since implementing this feature within
            # concurrent threads would address the actual isse of thread itself not working
        self.old_data_detection(master)
        if self.old_data_detected:
            return {'old_data': self.old_data_detected, 'flights': flights}

        return flights
    
    
     
    def ewr_gate_query(self, gate):
        gate_rows_collection = db_UJ['ewrGates']   # create/get a collection
        
        return_crit = {'_id':0}
        find_crit = {'Gate':{'$regex':gate}}
        res = gate_rows_collection.find(find_crit, return_crit).sort('Scheduled', -1)
        # res = gate_rows_collection.find(find_crit, return_crit)

        flight_rows = list(res)

        if flight_rows:
            return flight_rows

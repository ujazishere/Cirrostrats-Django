from concurrent.futures import ThreadPoolExecutor, as_completed
from .EC2 import EC2_location
import requests
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import pytz
import pickle
import smtplib
import os

class Root_class():
    
    def __init__(self) -> None:
            pass


    def send_email(self, body_to_send):
        full_email = f"Subject: {EC2_location}\n\n{body_to_send}"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587  # Use 587 for TLS port
        smtp_user = "publicuj@gmail.com"
        smtp_password = "dsxi rywz jmxn qwiz"
        to_email = ['ujasvaghani@gmail.com', 'ismailsakhani879@gmail.com']
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Start TLS for security
            server.starttls()
        
            # Login to the email account
            server.login(smtp_user, smtp_password)
        
            # Send the email
            server.sendmail(smtp_user, to_email, full_email.encode('utf-8'))
        print('SENT EMAIL!!!!!!!!!!!!!:', body_to_send)

        
    def date_time(self, raw=None, viewable=None, raw_utc=None):
        eastern = pytz.timezone('US/eastern')
        now = datetime.now(eastern)
        latest_time = now.strftime("%#I:%M%p, %b %d.")
        if raw_utc:
            if raw_utc == 'HM':
                return datetime.utcnow().strftime('%Y%m%d%H%M')
            else:
                raw_UTC_instant = str(datetime.utcnow())[:10].replace('-','')  # Format is YYYYMMDD
                return raw_UTC_instant
        elif raw:         # format yyyymmdd
            return now.strftime('%Y%m%d')       # date format yyyymmdd
        elif viewable:
            return now.strftime('%b %d, %Y')
        else:
            return latest_time
    

    def request(self, url, timeout=None):
        if timeout:
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.get(url)
        return bs4(response.content, 'html.parser')


    def load_master(self):
        try:
            with open('master_UA.pkl', 'rb') as f:
                return pickle.load(f)
        except:
            with open('dj/master_UA.pkl', 'rb') as f:
                return pickle.load(f)




    def dt_conversion(self, data):
        # converts date and time string into a class object 
        return datetime.strptime(data, "%I:%M%p, %b%d")


    def exec(self, input1, multithreader):
    
    # TODO: VVI: Have a solid understanding and extract this blueprint for future use.

    # executor blueprint: In this case input1 argument of this exec funtion are a bunch of flight numbers in list form while,
        # `multithreaders` is the task itself. This task will be multiplied by the amount of times of flight numbers.
            # In this case multithreaders is a function that takes in a flight number and returns its gates and stuff.
            # if there are 10 flight numbers the multithreader function will be duplicated 10 times.
        # executor.submit will submit all flight numbers at once to the multithreader function that is the second argument in exec
            # seems like this creates a task list of all functions and all those functions get sent to work at once altogether.
        # this will take in all the flight numbers at once and perform web scrape(`pick_flight_data()`) on all of them simultaneously
        # Multithreading
    
        completed = {}
        troubled = set()
            # VVI!!! The dictionary `futures` .value is the flight number and  key is the the memory location of return from pick_flight_data
            # Used in list comprehension for loop with multiple keys and values in the dictionary. for example:
            # {<Future at 0x7f08f203ec10 state=running>: 'UA123',
                # <Future at 0x7f08f203ed10 state=running>: 'DL789'
                        # }
        with ThreadPoolExecutor(max_workers=150) as executor:
            # First argument in submit method is the lengthy function that needs multi threading
                # second argument is each flt number that goes into that function. Together forming the futures.key()
                #note no parentheses in the first argument
            futures = {executor.submit(multithreader, flt_num): flt_num for flt_num in
                        input1}         # This submit method tasks to do to the executor for concurrent execution.
            # futures .key() is the memory location of the task and the .value() is the flt_num associated with it
            for future in as_completed(futures):    # as_completed is imported with the ThreadPoolExecutor
                # again, future is the memory location of the task
                flt_num = futures[future]
                try:
                    result = future.result()        # result is the output of the task at that memory location 
                    completed.update(result)
                except Exception as e:
                    # print(f"Error scraping {flt_num}: {e}")
                    troubled.add(flt_num)
                
        # reading outlaws and dumping them
        with open('outlaws.pkl', 'rb') as f:
            outlaws = pickle.load(f)
        outlaws.update(self.outlaws_reliable)
        with open('outlaws.pkl', 'wb') as f:
            pickle.dump(outlaws, f)
            
        return dict({'completed':  completed, 'troubled': troubled})
        
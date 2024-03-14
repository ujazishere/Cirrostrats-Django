# from dj.dj_app.root.root_class import Root_class, Pull_class
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import pytz
import pickle
import smtplib
import asyncio
import aiohttp

class Root_class():
    
    def __init__(self) -> None:
            pass


    def send_email(self, body_to_send):

        try: 
            from .Switch_n_auth import EC2_location
            full_email = f"Subject: {EC2_location}\n\n{body_to_send}"
        except:
            print('EC2_location within dj\dj_app\root\Switch_n_auth.py was not found. Need the file and the variable as string.')
            full_email = f"Subject: UNKNOWN Local\n\n{body_to_send}"
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
        

class Pull_class(Root_class):           # Change this name to Fetch_class
    def __init__(self,flt_num=None,dep_airport_id=None,dest_airport_id=None) -> None:
        super().__init__()
        date = self.date_time(raw=True)
        # United departure and destination airport only
        # soup
        self.ua_dep_dest = f"https://united-airlines.flight-status.info/ua-{flt_num}"               # This web probably contains incorrect information.

        # local time zones. just needs flight number as input
        # soup
        self.flight_stats_url = f"https://www.flightstats.com/v2/flight-tracker/UA/{flt_num}?year={date[:4]}&month={date[4:6]}&date={date[-2:]}"
        
        #soup- gate information accounted for both
        try:        # the airport coming in initially wouldnt take airport as arg since it lacks the initial info, hence sec rep info will have this airport ID
            self.flight_view_gate_info = f"https://www.flightview.com/flight-tracker/UA/{flt_num}?date={date}&depapt={dep_airport_id[1:]}"
        except:
            pass
        self.nas = "https://nasstatus.faa.gov/api/airport-status-information"

        # Flight Aware
        fa_apiKey = "G43B7Izssvrs8RYeLozyJj2uQyyH4lbU"         # New Key from Ismail
        self.fa_auth_header = {'x-apikey':fa_apiKey}

        # Aviation Stack api call. 3000 requests per month
        self.aviation_stack_params = {
          'access_key': '65dfac89c99477374011de39d27e290a',
          'flight_icao': "UAL414"
        }


    def requests_processing(self, 
                        requests_raw_extract: requests.models.Response,
                        json=None,
                        awc=None,
                        bs=None,
                        ):
        if awc:
            
            awc_raw = requests_raw_extract        # Trying this asraw see if it works
            # awc_raw = requests_raw_extract.text
            # awc_raw = awc_raw.decode("utf-8")
            return awc_raw
        elif json:
            return requests_raw_extract.json()
        elif bs:
            # Might need to change this to requests_raw_extract.content depending on the use case.
            return bs4(requests_raw_extract,'html.parser')


    def weather_links(self, dep_airport_id, dest_airport_id, ):
        
        return {
        "dep_awc_metar_api": f"https://aviationweather.gov/api/data/metar?ids={dep_airport_id}",
        "dep_awc_taf_api": f"https://aviationweather.gov/api/data/taf?ids={dep_airport_id}",
        "dep_datis_api":  f"https://datis.clowd.io/api/{dep_airport_id}",
        "dest_awc_metar_api": f"https://aviationweather.gov/api/data/metar?ids={dest_airport_id}",
        "dest_awc_taf_api": f"https://aviationweather.gov/api/data/taf?ids={dest_airport_id}",
        "dest_datis_api":  f"https://datis.clowd.io/api/{dest_airport_id}",
        }


    def api_pull_w_limits(self, flt_num, airline_code=None):

        if not airline_code:
            airline_code = 'UAL'
        fa_base_apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
        self.fa_url = fa_base_apiUrl + f"flights/{airline_code}{flt_num}"
        # response = requests.get(url, headers=fa_auth_header) 

        # aviationstack just like flight_aware
        self.aviation_stack_url = 'http://api.aviationstack.com/v1/flights'
        # api_result = requests.get(aviation_stack_url, self.aviation_stack_params)


        """
        # copy paste these lines within comment to jupyter and it will work
        import requests,asyncio, aiohttp
        from dj.dj_app.root.root_class import Root_class, Pull_class
        pc = Pull_class('4416)
        r = Root_class()
        pc.pull('4416')
        all_links = [
        pc.ua_dep_dest,
        pc.flight_stats_url,
        pc.dep_awc_metar_api,
        pc.dep_awc_taf_api,
        pc.dep_datis_api,
        pc.dest_awc_metar_api,
        pc.dest_datis_api,
        pc.dest_awc_taf_api,
        pc.nas,]

        task = asyncio.ensure_future(pc.async_pull(all_links))
        asyncio.gather(task)
        resp = await task       # This is the responsein jupyter that works 

        print(resp)

        # all_items = []
        # for url in all_links:
            # all_items.append(r.request(url))

        """


    async def async_pull(self, link_list:list):
        # A function is a coroutine if you prepend it with `async`. This is a coroutine function
        async def get_tasks(session):
            # an inexpensive operation: putting all urls to be fetched into tasks list.
            tasks = []
            for url in link_list:
                tasks.append(asyncio.create_task(session.get(url)))
            return tasks
        
        async def main():
            async with aiohttp.ClientSession() as session:
                tasks = await get_tasks(session)
                # Upto here the tasks are created which is very light.
        
                # Actual pull work is done using as_completed 
                resp_return_list = {}
                for resp in asyncio.as_completed(tasks):        # use .gather() instead of .as_completed for background completion
                    resp = await resp
                    content_type = resp.headers.get('Content-Type')
                    if content_type == "application/json":
                        resp_text = await resp.json()
                    else:
                        resp_text = await resp.text()
                    resp_return_list[resp.url] = resp_text
                return resp_return_list

        #1 Temporary. Works when function calling within jupyter.
        return await main()         

        #2 works for jupyter when copy pasting this whole code within jupyter.
        # link_fetch = await asyncio.ensure_future(main())  
        
        #3 works for external cli use.
        # if __name__ == "__main__":        # if statement seems unnecessary: works when calling from cli, not when importing elsewhere
            # link_fetch = await asyncio.run(main())
            # return await link_fetch
        
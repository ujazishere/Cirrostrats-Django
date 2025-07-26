


from pymongo import MongoClient
from decouple import config
import certifi

"""
***CAUTION***
When getting key=value pair error, the issue is that athe connection string arrives truncated in VS code terminal.
Updating VS code to the latest build should fix the issue. If it doesn't,
Try using command promt window or terminal window outside of VS code instead of using the vs code terminal.
To troubeshoot make sure to print the connection string to see whats actuallly being used by the system.
"""
client_UJ = MongoClient(config('connection_string_uj'), tlsCAFile=certifi.where())

db_UJ = client_UJ.cirrostrats
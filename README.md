Clone the repo:
`git clone https://github.com/ujazishere/Cirrostrats.git`

Creating and activating virtual environment on mac/win:


win:

Navigate into the Cirrostrats directory and make virtual environment:
`python3 -m venv c_venv`

Activate it:
`c_venv\Scripts\activate`


mac:

Navigate into Cirrostrats directory then run:
`sudo pip3 install virtualenv`

Make virtual environment using:
`virtualenv c_venv`

Activate it:
`source c_venv/bin/activate`


__________________________________________________________________________

Install packages/dependencies:
`pip install -r req.txt`

Checkout the dev branch for latest code AND AVOID THE MAIN BRANCH:
`git chekcout dev`

MAKE SURE YOURE IN THE `dev` BRANCH:
`git branch`

Run the local django server:
`python dj/manage.py runserver 0.0.0.0:8000`

Go on browser pull up http://127.0.0.1:8000/

Go crazy!




Access the AWS EC2 test web server from phone/laptop at:
http://3.132.144.5/

Production ready AWS EC2 at:
https://cirrostrats.us/


Available Queries:

Gate in EWR examples:
C71, C, A, B, 106, 71X, 71V, etc.

weather queries(have to prepend `w ` for international ICAO identifiers):
eg- kbos, kewr, kiad, kord, w cyow, etc.

all examples:

"" - Empty query returns all gates

"c71x" - Returns all flights scheduled times from this gate. Gives their scheduled time of departure and actual.

"w kewr" - Returns metar and taf of the airport in question

"4425" - Returns the departure airport, arrival airport, and, weather(D-Atis, METAR, TAF), ground stops, ground delays,route,skyvector route redirect, registration, etc.


 


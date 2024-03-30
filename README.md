### Backend

1. **Open Terminal:** You'll need to open the terminal via your computer or visual code

2. **Running the Backend:**

   a. **Ensure Python Installation:** Make sure Python is installed on your machine.

   b. **Create an env file inside of backend folder :**
   right click, backend folder, select create new file and name it '.env'
   inside of the file create a variable named connection_string=''
   inside of the quotes add your connection string with username and password.

   c. **Initialize Virtual Environment (venv) in the project's root directory i.e /cirrostrats/:**

   ```bash
   python -m venv venv
   ```

   d. **Activate the Virtual Environment in the root directory i.e /cirrostrats/:**

   ```bash
   source venv/bin/activate
   ```

   e. **Install Required Packages from the root branch(not the backend directory):**

   ```bash
   pip install -r req.txt
   ```

   f. **Navigate/cd into backend directory i.e cirrostrats/backend and Run the Server:**

   ```bash
   uvicorn main:app --reload
   ```

   g. **Access the Project:** The project will be running on [http://127.0.0.1:8000](http://127.0.0.1:8000).
















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

Checkout the uj branch for latest code AND AVOID THE MAIN BRANCH:
`git chekcout uj`

MAKE SURE YOURE IN THE `uj` BRANCH:
`git branch`

Navigate into backend folder:
`cd backend`

Run the local fastAPI:
`uvicorn main:app --reload`

Go on browser pull up http://127.0.0.1:8000/

 


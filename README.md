### How to setup the project

* Make sure that you have python 3 installed.
* Create a virtual environment using `python3 -m venv venv`
    * To run the virtual environment on bash, use `source venv/bin/activate`
    * On Windows, use `venv\Scripts\activate`
    * If you did this correctly, you should see `(venv)` before each command line
* Install flask with `pip install flask`
* To verify that this install worked, open a python interpreter for the venv and type `import flask`
    * If you don't get errors, it works!    
* Set an environment variable using `export FLASK_APP=app.py`
    * Replace `export` with `set` on Windows    
* Type `flask db migrate`, then `flask db upgrade` to create the mock database for the project
* Type `flask run` to start the server
  

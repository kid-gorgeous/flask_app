


## SETTING UP FLASK



### Dependence
These disibutions will be installed automatically when installing Flask

1. [Werkzeug](https://palletsprojects.com/p/werkzeug/) implements WSGI, the standard Python interface between applications and serverse

2. [Jinja](https://palletsprojects.com/p/jinja/) is a template languege that renders the pages your application serves. ..involves .html and jinja templating syntax

3. [MarkupSafe](https://palletsprojects.com/p/markupsafe/) implements a text object that excapes characters so it is safe to use in HTML and XML.

4. [ItsDangerous](https://palletsprojects.com/p/itsdangerous/) Data is cryptographically signed to ensure that a token has not been tampered with.

5. [Click](https://palletsprojects.com/p/click/) It's the "Command Line Interface Creation Kit".


---
### Optional dependencies: 
        Blinker, python-dotenv, Watchdog

### Necessary:
        PyPy >= 7.3.7, and greenlet>=1.0
    
* These are not minimum supported versions, they only indicate the first versions that added necessary features. You should use the latest versions of each.



---
### Installing Flask
Within the activated environment, use the following command to install Flask:

        $ pip install Flask
    
Flask is now installed. 



---
## Setting up Flask Environment

The command line arguements that are necessary for starting the flask application must be written as such in the command line:

#### UNIX OS
        $ export FLASK_APP=app
        $ export FLASK_ENV=development
        $ flask run -h localhost -p 5000
#### fish
        $ set -x FLASK_APP flasker
        $ set -x FLASK_ENV development
        $ flask run -h localhost -p 5000

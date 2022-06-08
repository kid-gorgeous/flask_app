import sqlite3 

import click
from flask import current_app, g
from flask.cli import with_appcontext

# helper function that will allow flask to easily access, or create 
# a new database if none is specified
def get_db():

    # this will create a sqlite database if one is not already found
    # g is a special object that is unique for each request, it is used to store
    # data that might be accessed by multiple functions during the request
    # the connection is stored and reused instead of creating a new connection if 
    # the helper function get_db() is called a second time in the same request
    if 'db' not in g:

        # establishes a connection to the file pointed at by the DATABASE configuration key. 
        # This file doesn’t have to exist yet, and won’t until you initialize the database later.
        g.db = sqlite3.connect(

            # current_app is another special object that points to the Flask application handling
            # request; since you used an application factory there is no application object when writing
            # the rest of the code. the helper function get_db() will be cralled when the application 
            # has been created and is handling a request, hence why current_app() is used
            current_app.config['DATABASE'],
            detect_types = sqlite3.PARSE_DECLTYPES
        )

        # sqlite3.Row tells the connection to return rows that behave like dictionarys. The allows accessing
        # the columns by name
        g.db.row_factory = sqlite3.Row

    return g.db


# helper function that closes the database upon request, it will check if a connection was created by 
# checking if g.db was set; if it exist from the stack then it is removed and closed.
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# helper function that will retreive a saved database, and decode
# its contents using utf8
def init_db():
    db = get_db()

    # open_resource() opens a file relative to the flaskr package, which is useful since you wont nessarily know where 
    # that location is when deplaying the application later. get_db() returns a database connection, which is used to 
    # execute the commands read from the file
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    

# @click.command() defines a command called init-db that calls the init_db function and shows a success
# message to the user. @with_appcontext will wrap a callback so that it's guarenteed to be executed with the
# script's application context. if the callbacks are registered directly to the app.cli object then they are
# wrapped with this function by default unless it is disabled.
@click.command('init-db')
@with_appcontext
def init_db_command():
    # this clears the existing data and creates new tables
    init_db()
    click.echo('Initialized the database.')


# the close_db() and init_db_command() functions need to be registered with tthe application 
# however, since this is using a factory function, that instance inst available when writing the function
# instead this will take the app as a parameter and register the application.
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
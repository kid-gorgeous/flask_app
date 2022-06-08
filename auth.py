import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# associates the URL /register with the register view function. When 
# flask recieves a request to /auth/register it will call the register view
# and use the return value as the repsonse, 
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # the request form is a special type of dictionary mapping submitted form keys and values
        # the user will input their username and password
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # validates that a username and password was submitted
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # if there is no error and the validation succeeds, insert the new user data into the
        # databases: db.execute takes a SQL query with ? palceholders for any user input, and
        # a tuple of values to preplace the placeholders with, generate_password_hash() is used
        # to securely hash the password, and that hash is stored (since the query modifies data, 
        # db.commit() must be used afterwards for changes to be made), sqlite3.InterruptedError
        # will occure is no username or password is specified
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."

        # after storing the user, they are redirected to the login page: url_for() generates the URL
        # for the login view based on its name; this is preferable to writing the URL directly as it
        # allows you to change the URL later without changing all code that links to it; redirect() 
        # generates a redirect response to the generated URL
            else:
                return redirect(url_for("auth.login"))

        # if there is a validation fails, the error is shown to the user. 
        # flash() stores messages that can be retrieved when rendering the template
        flash(error)

    # render_template() will render a template containing the HTML 
    return render_template('auth/register.html')


# associates the URL /login with the login view function. When 
# flask recieves a request to /auth/login it will call the login view
# and use the return value as the repsonse, 
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # retrevies the user from the database based on the submitted form data
        # fetchone() returns one row from the query; if the query returned no results, 
        # it returns None; later
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # check_password_hash hashes the submitted password in the same way as
        # the stored hash and securely compares them; if they match, the password is valid
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrest password.'

        # session is a dictionary that stores data across request; when validation succeeds, the
        # the user's id is stored in a new session. the data is stored in a cookie that is sent to
        # the browser, and the browser then sends it back with the subsequent request; flask securely
        # signs the data so that it can't be tempered with 
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        # if there is a validation fails, the error is shown to the user. 
        # flash() stores messages that can be retrieved when rendering the template
        flash(error)
    # render_template() will render a template containing the HTML
    return render_template('auth/login.html')


# checks if a user id is stored in the sesion and gets that user's data from 
# the database, storing it on g.user, which lasts for the length of the request. 
# before_app_request registers a function that runs before the view function, no 
# matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    # gets the user_id from the session
    user_id = session.get('user_id')

    # if there is no user if, of if the id doesnt exist, g.user will be None
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id)
        ).fetchone()


# to log out, the user_id must be removed from the session, then load_logged_in_user 
# wont load a user on subsequent request
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    # functools is a standard Python module for higher-order functions, wraps() is a decorator
    # that is applied to the wrapper function of a decorator
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
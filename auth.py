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
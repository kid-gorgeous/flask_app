from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

# updates the index from the __init__.py file, selects the id, title, body, created, author_id, username
# from the sqlite3 database, but utilizes the SQL function fetchall(), similar to the .fetchone() from auth.py
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# !!! MODULE FUNCTION
# a constructor like functions that uses the login_required wrapper function
# the wrapper (decorator) requires the user to be logged into the application
# the decorator is imported from auth.py
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        else: 
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


# ! HELPER FUNCTION
# this is a helper function; check author argument is defined so that the funstion can be user to get a post 
# without checking the author. This would be useful if you wrote a view to show an individual post on a page, where
# the user doesnt matter because they're 
def get_post(id, check_author=True):
    # post is created as a SQL dictionary
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # takes an optional message to show with the error, otherwise a default message is used. 404 means
    # Not found, and the error message, but if not these condition the default message is user. 
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# !!! MODULE FUNCTION
# unlike the VIEWS seen this 
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    
    # the form date request made from the form submission 
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        # update the HTML page title
        if not title:
            error = 'Title is required.'

        # Hey here, first flash if error, if not then proceed with retreving the database
        # 
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
from datetime import date
import functools
from asyncio.windows_events import NULL
from distutils.log import error

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash

from ResortManagementSystem.db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        adminname = request.form['admin']
        passwd = request.form['passwd']

        db = get_db()
        error = None

        admin = db.execute(
            'SELECT * FROM admin WHERE admin = ?', (adminname,)
        ).fetchone()

        if adminname is '':
            error = 'Enter admin name'
        elif admin is None:
            error = 'Admin ID not found'
        elif not check_password_hash(admin['passwd'], passwd):
            error = 'Incorrect Password'

        if error is None:
            session.clear()
            session['adminid'] = admin['admin_id']
            session['admin'] = admin['admin']
            return redirect(url_for('auth.index'))

        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    adminid = session.get('adminid')
    if adminid is None:
        g.admin = None
    else:
        g.admin = get_db().execute(
            'SELECT * FROM admin WHERE admin_id = ?', (adminid,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for('auth.login'))
            
        return view(**kwargs)

    return wrapped_view


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    indexdata = db.execute(
        'SELECT * FROM indexdata',
    ).fetchall()
    checkoutlist = db.execute(
        'SELECT * FROM checkoutlist',
    ).fetchall()

    return render_template('index.html', indexdata = indexdata, checkoutlist = checkoutlist)

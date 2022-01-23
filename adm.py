from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from ResortManagementSystem.auth import login_required
from ResortManagementSystem.db import get_db

bp = Blueprint('adm', __name__)

@bp.route('/admin/chngpasswd', methods=('GET', 'POST'))
@login_required
def chngpasswd():
    if request.method == 'POST':
        curpass = request.form['curpass']
        newpass = request.form['newpass']
        cnfrmpass = request.form['cnfrmpass']

        adminid = session.get('adminid')
        db = get_db()
        error = None

        admin = db.execute(
            'SELECT * FROM admin WHERE admin_id = ?', (adminid,)
        ).fetchone()

        if not check_password_hash(admin['passwd'], curpass):
            error = 'Incorrect password'
        elif not newpass:
            error = 'Enter new Password'
        elif not newpass == cnfrmpass:
            error = 'Passwords doesn\'t match'

        if error is not None:
            flash(error)
        else:
            db.execute(
                "UPDATE admin SET passwd = ? WHERE admin_id = ?",
                (generate_password_hash(newpass), adminid)
            )
            db.commit()
            session.clear()
            return redirect(url_for('auth.login'))

    return render_template('admin/chngpasswd.html')

@bp.route('/admin/adminlist', methods=('GET', 'POST'))
@login_required
def getadminlist():
    db = get_db()
    adminlist = db.execute(
        'SELECT admin_id, admin FROM admin'
    ).fetchall()

    return render_template('admin/adminlist.html', adminlist = adminlist)

@bp.route('/admin/addadmin', methods=('GET', 'POST'))
@login_required
def addadmin():
    if request.method == 'POST':
        newadm = request.form['newadm']
        newpass = request.form['newpass']
        cnfrmpass = request.form['cnfrmpass']

        db = get_db()
        error = None
        admin = None
        admin = db.execute(
            'SELECT * FROM admin WHERE admin = ?', (newadm,)
        ).fetchone()

        if admin is not None:
            error = 'Admin already exists'
        elif not newpass == cnfrmpass:
            error = 'Passwords doesn\'t match'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO admin (admin, passwd) VALUES(?, ?)',
                (newadm, generate_password_hash(newpass)),
            )
            db.commit()
            flash(f"Successfully added admin {newadm}")

    return render_template('admin/addadmin.html')

@bp.route('/admin/rmvadmin', methods=('GET', 'POST'))
@login_required
def rmvadmin():
    if request.method == 'POST':
        rmadm = request.form['rmadm']
        rmadmpass = request.form['rmadmpass']
        admpass = request.form['admpass']
        adminid = session.get('adminid')

        db = get_db()
        error = None
        admin = None
        rmv_admin = None
        admin = db.execute(
            'SELECT * FROM admin WHERE admin_id = ?', (adminid,)
        ).fetchone()

        if not check_password_hash(admin['passwd'], admpass):
            error = 'Your password is incorrect'    
        else:
            rmv_admin = db.execute(
                'SELECT * FROM admin WHERE admin = ?', (rmadm,),
            ).fetchone()
            if rmv_admin is None:
                error = "Admin not found"
            elif int(rmv_admin['admin_id']) == int(adminid):
                error = "You cannot remove yourself"
            elif not check_password_hash(rmv_admin['passwd'], rmadmpass):
                error = "Password for given Admin ID is incorrect"
            
        if error is None:
            db.execute(
                'DELETE FROM admin WHERE admin_id = ?',
                (rmv_admin['admin_id'],),
            )
            db.commit()
            flash(f"Successfully removed admin with name {rmv_admin['admin']}")
        else:
            flash(error)
        
    return render_template('admin/rmvadmin.html')

from sqlite3 import DatabaseError

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from ResortManagementSystem.auth import login_required
from ResortManagementSystem.db import get_db

bp = Blueprint('resort', __name__)

@bp.route('/resort/addresort', methods=('GET', 'POST'))
@login_required
def addresort():
    db = get_db()
    roomtypes = db.execute(
        'SELECT * FROM room_types',
    ).fetchall()
    
    if request.method == 'POST':
        resortname = request.form['newresort']
        resortloc = request.form['resortloc']
        rooms = {}
        for room in roomtypes:
            rooms[room['room_type_id']] = request.form[room['room_type_id']]

        db = get_db()
        resortcheck = None
        resortcheck = db.execute(
            'SELECT * FROM resort WHERE resort_name = ?',(resortname,),
        ).fetchone()

        if resortcheck is not None:
            flash('Resort already exists')
        else:
            db.execute(
                'INSERT INTO resort(resort_name, location) VALUES( ?, ?)',
                (resortname, resortloc,),
            )
            resortid = db.execute(
                'SELECT resort_id FROM resort WHERE resort_name = ?',(resortname,),
            ).fetchone()
            for room in roomtypes:
                roomtypeid =  room['room_type_id']
                for i in range(0, int(rooms[roomtypeid])):
                    db.execute(
                        'INSERT INTO rooms(resort_id, room_type_id) VALUES( ?, ?)',
                        (int(resortid['resort_id']), roomtypeid),
                    )
            db.commit()
            flash('New Resort details added')

    return render_template('resort/addresort.html', roomtypes = roomtypes)

@bp.route('/resort/resortlist', methods=('GET','POST'))
@login_required
def resortlist():
    db=get_db()
    resortlist = db.execute(
        'SELECT * FROM resort'
    ).fetchall()
    return render_template('resort/resortlist.html', resortlist=resortlist)

@bp.route('/resort/update', methods=('GET','POST'))
@bp.route('/resort/<resortid>/update', methods=('GET','POST'))
@login_required
def updateresort(resortid=-1):
    if request.method == 'POST':
        if resortid == -1:
            resortid = request.form['resortid']

        newname = request.form['newname']
        newloc = request.form['newloc']
        db =get_db()

        if newname == '' and newloc == '':
            flash('Nothing to update')
        elif not newname == '' and not newloc == '':
            db.execute(
                'UPDATE resort SET resort_name = ?, location = ?  WHERE resort_id = ?',
                (newname, newloc, resortid),
            )
            db.commit()
            flash('Resort details updated')
        else:
            if not newname == '':
                db.execute(
                    'UPDATE resort SET resort_name = ? WHERE resort_id = ?',
                    (newname, resortid,),
                )
                db.commit()
            else:
                db.execute(
                    'UPDATE resort SET location = ? WHERE resort_id = ?',
                    (newloc, resortid,),
                )
                db.commit()
            flash('Resort details updated')
    
    resort= {}
    if resortid is not None:
        db = get_db()
        resort = db.execute(
            'SELECT * FROM resort WHERE resort_id = ?',
            (resortid,),
        ).fetchone()
        
    return render_template('resort/updateresort.html', resort = resort)

@bp.route('/resort/delete', methods=('GET','POST'))
@bp.route('/resort/delete/<resortid>', methods=('GET','POST'))
@login_required
def deleteresort(resortid=-1):
    if request.method == 'POST':
        if resortid == -1:
            resortid = request.form['resortid']
        
        db = get_db()
        search = db.execute(
            'SELECT * FROM resort WHERE resort_id = ?',
            (resortid,),
        ).fetchone()
    
        if search is not None:
            try:
                db.execute(
                    'DELETE FROM resort WHERE resort_id = ?',
                    (resortid,),
                )
                db.commit()
                flash('Resort data has been deleted')
            except DatabaseError:
                pass
        else:
            flash(f'Rsort with ID {resortid} not found')
    
    if resortid == -1:
        resortid=''
    return render_template('resort/deleteresort.html', resortid = resortid)

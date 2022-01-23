import datetime
from distutils.log import error
from re import search
from sqlite3 import IntegrityError
from webbrowser import get

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from itsdangerous import exc

from ResortManagementSystem.auth import login_required
from ResortManagementSystem.db import get_db

bp = Blueprint('guest', __name__)

@bp.route('/guest/addguest', methods=('GET', 'POST'))
@login_required
def addguest():
    db = get_db()
    if request.method == 'POST':
        guestname = request.form['guestname']
        idtype = request.form.get('idtype')
        idnumber = request.form['idnumber']
        address = request.form['address']
        phoneno = request.form['phoneno']

        db.execute(
            'INSERT INTO guests(guest_name, id_type, id_number, address, phone) VALUES(?, ?, ?, ?, ?)',
            (guestname, idtype, idnumber, address, phoneno,),
        )
        db.commit()
        flash('Guest details has been saved')

    id_types = db.execute(
        'SELECT * FROM id_types'
    ).fetchall()
    return render_template('/guest/addguest.html', idtypes = id_types)

@bp.route('/guest/guestlist', methods=('GET', 'POST'))
@login_required
def guestlist():

    db = get_db()
    guestlist = db.execute(
        'SELECT guest_id, guest_name, phone, address, id_name, id_number FROM guests g, id_types i WHERE g.id_type = i.id_type',
    ).fetchall()

    return render_template('guest/guestlist.html', guestlist = guestlist)

@bp.route('/guest/<guestid>/deleteguest', methods=('GET', 'POST'))
@login_required
def deleteguest(guestid):
    db = get_db()
    try:
        db.execute(
            'DELETE FROM guests WHERE guest_id = ?',
            (guestid,),
        )
        db.commit()
        flash('Guest record has been deleted')
    except IntegrityError:
        flash('Unable to delete checked in guest, check-out first')
    return redirect(url_for('guest.guestlist'))


@bp.route('/guest/<guestid>/updateguest', methods=('GET', 'POST'))
@login_required
def updateguest(guestid):
    db = get_db()
    if request.method == 'POST':
        guestname = request.form['guestname']
        idtype = request.form.get('idtype')
        idnumber = request.form['idnumber']
        address = request.form['address']
        phoneno = request.form['phoneno']

        db.execute(
            'UPDATE guests SET guest_name = ?, id_type = ?, id_number = ?, address = ?, phone =? WHERE guest_id = ?',
            (guestname, idtype, idnumber, address, phoneno, guestid),
        )
        db.commit()
        flash('Guest details have been updated')
        return redirect(url_for('guest.guestlist'))

    guestlist = db.execute(
        'SELECT * FROM guests WHERE guest_id = ?',
        (guestid,),
    ).fetchone()
    id_types = db.execute(
        'SELECT * FROM id_types'
    ).fetchall()
    return render_template('guest/updateguest.html', guestlist = guestlist, idtypes = id_types)

@bp.route('/guest/<guestid>/checkin', methods=('GET', 'POST'))
@login_required
def checkin(guestid):
    db=get_db()
    guestlist = db.execute(
        'SELECT * FROM guests',
    )
    resortlist = db.execute(
        'SELECT * FROM resort',
    )

    if request.method == 'POST':
        if request.form['selectroom'] == '0':
            guestid = request.form.get('guest')
            resort = request.form.get('resort')
            selectroom = 1
            rooms = db.execute(
                'SELECT r.room_type_id, room_type, room_number, status FROM rooms r, room_types rt WHERE r.room_type_id = rt.room_type_id and resort_id = ?',
                (resort,),
            ).fetchall()
            mindate = datetime.date.today() + datetime.timedelta(1)
            maxdate = datetime.date.today() + datetime.timedelta(10)
            return render_template('guest/checkin.html', guestid = guestid, resortid = resort, guestlist = guestlist, resortlist = resortlist, selectroom = selectroom, rooms = rooms, mindate = mindate, maxdate = maxdate)
        else:
            guestid = request.form.get('guest')
            resort = request.form.get('resort')
            room = request.form.get('room')
            checkout = datetime.datetime.strptime(request.form['checkout'], '%Y-%m-%d')

            try:
                db.execute(
                'INSERT INTO occupants(guest_id, resort_id, room_number, number_of_occupants, check_out_date) VALUES (?, ?, ?, ?, ?)',
                (guestid, resort, room, 4, checkout,),
                )
                db.execute(
                    'UPDATE rooms SET status = ? WHERE room_number = ?',
                    (1, room),
                )
                db.commit()
                flash('Check-In Complete')
            except IntegrityError:
                flash('Guest has already checked in')

            return redirect(url_for('guest.guestlist'))

    selectroom=0
    return render_template('guest/checkin.html', guestid = guestid, guestlist = guestlist, resortlist = resortlist, selectroom = selectroom)

@bp.route('/guest/checkinlist', methods=('GET', 'POST'))
@login_required
def checkinlist():
    db = get_db()
    guestlist = db.execute(
        'SELECT o.guest_id, guest_name, resort_name, room_number FROM resort r, occupants o, guests g WHERE o.guest_id = g.guest_id and o.resort_id = r.resort_id',
    ).fetchall()
    return render_template('guest/checkinlist.html', guestlist = guestlist)

@bp.route('/guest/<guestid>/addservices', methods=('GET', 'POST'))
@login_required
def addservices(guestid):
    db = get_db()
    if request.method == 'POST':
        guest_id = request.form['guest']
        service = request.form.get('service')
        db.execute(
            'INSERT INTO availed_additional_services VALUES( ?, ?)',
            (guest_id, service,),
        )
        db.commit()
        flash('Additional Service has been added')

    services = db.execute(
        'SELECT * FROM additional_services',
    ).fetchall()
    guests = db.execute(
        'SELECT guest_name FROM occupants o, guests g WHERE o.guest_id = g.guest_id and o.guest_id = ?',
        (guestid,),
    ).fetchall()
    availed_services = db.execute(
        'SELECT service_name, price FROM availed_additional_services aas, additional_services a WHERE aas.service_id = a.service_id and guest_id = ?',
        (guestid,),
    ).fetchall()
    return render_template('guest/addservices.html', services = services, guests = guests, guestid = guestid, availedservices = availed_services)

@bp.route('/guest/<guestid>/checkout', methods=('GET', 'POST'))
@login_required
def checkout(guestid):
    db = get_db()
    if request.method == 'POST':
        room = db.execute(
            'SELECT room_number FROM occupants WHERE guest_id = ?',
            (guestid,),
        ).fetchone()
        db.execute(
            'UPDATE rooms SET status = 0 WHERE room_number = ?',
            (room['room_number'],),
        )
        db.execute(
            'DELETE FROM occupants WHERE guest_id = ?',
            (guestid,),        
        )
        db.commit()
        flash('Guest has been checked out')
        return redirect(url_for('guest.checkinlist'))
    
    room = db.execute(
        'SELECT room_type, room_price FROM occupants o, rooms r, room_types rt where o.room_number = r.room_number and r.room_type_id = rt.room_type_id and o.guest_id = ?',
        (guestid,),
    ).fetchone()
    availed_services = db.execute(
        'SELECT service_name, price FROM availed_additional_services aas, additional_services a WHERE aas.service_id = a.service_id and guest_id = ?',
        (guestid,),
    ).fetchall()
    guest = db.execute(
        'SELECT guest_name, guest_id, address, phone FROM guests WHERE guest_id = ?',
        (guestid,),
    ).fetchone()
    return render_template('guest/checkout.html', availedservices = availed_services, room = room, guest = guest)
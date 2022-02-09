from audioop import add
from distutils.log import error
from re import search
from sqlite3 import IntegrityError
from tkinter.messagebox import NO

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from ResortManagementSystem.auth import login_required

from ResortManagementSystem.db import get_db

bp = Blueprint('emp', __name__)
@bp.route('/employee/register', methods=('GET', 'POST'))
@login_required
def registeremployee():
    if request.method == 'POST':
        empname = request.form['newemp']
        phoneno = request.form['phoneno']
        address = request.form['address']
        salary = request.form['salary']

        db = get_db()
        try:
            db.execute(
                'INSERT INTO employee(emp_name, phoneno, address, salary) VALUES( ?, ?, ?, ?)',
                (empname, phoneno, address, salary,),
            )
            db.commit()
            flash('Employee details have been saved')
        except IntegrityError:
            flash('Phone Number already used')

    return render_template('employee/registeremployee.html')

@bp.route('/employee/listemployee', methods=('GET', 'POST'))
@login_required
def employeelist():
    db=get_db()
    employeelist = db.execute(
        'SELECT * FROM employee'
    ).fetchall()

    return render_template('employee/employeelist.html', employeelist = employeelist)

@bp.route('/employee/listemployee', methods=('GET', 'POST'))
@bp.route('/employee/<employeeid>/listemployee', methods=('GET', 'POST'))
@login_required
def updateemployee(employeeid):
    db = get_db()
    
    if request.method == 'POST':
        empname = request.form['newemp']
        phoneno = request.form['phoneno']
        address = request.form['address']
        salary = request.form['salary']

        db.execute(
            'UPDATE employee SET emp_name = ?, phoneno = ?, address = ?, salary = ? WHERE employee_id = ?',
            (empname, phoneno, address, salary, employeeid),
        )
        db.commit()
        flash('Employee details have been updated')
 
    employee = db.execute(
        'SELECT * FROM employee WHERE employee_id = ?',
        (employeeid,),
    ).fetchone()
    return render_template('employee/updateemployee.html', emp = employee)

@bp.route('/employee/<employeeid>/deleteemployee', methods=('GET', 'POST'))
@login_required
def deleteemployee(employeeid):
    db = get_db()
    db.execute(
        'DELETE FROM employee WHERE employee_id = ?',
        (employeeid,),
    )
    db.commit()
    flash('Employee record has been deleted')
    return redirect(url_for('emp.employeelist'))


@bp.route('/employee/postemployee', methods=('GET', 'POST'))
@bp.route('/employee/<employeeid>/postemployee', methods=('GET', 'POST'))
@login_required
def postemployee(employeeid):
    db = get_db()
    if request.method == 'POST':
        employid = request.form.get('employee')
        resortid = request.form.get('resort')
        desg = request.form['desg']

        search = db.execute(
            'SELECT employee_id FROM employee_posting WHERE employee_id = ?',
            (int(employid),),
        ).fetchone()

        if search is not None:
            flash('Employee has been already posted')
        db.execute(
            'INSERT INTO employee_posting(employee_id, resort_id, designation) VALUES(?, ?, ?)',
            (int(employid), int(resortid), desg,),
        )
        db.commit()

    employee = db.execute(
        'SELECT employee_id, emp_name FROM employee',
    ).fetchall()
    resortlist = db.execute(
        'SELECT resort_id, resort_name FROM resort',
    ).fetchall()
    return render_template('employee/postemployee.html', emp = employee, empid = employeeid, resortlist = resortlist)

@bp.route('/employee/postinglist', methods=('GET', 'POST'))
@login_required
def postinglist():
    db = get_db()
    employee = db.execute(
        'SELECT ep.employee_id, emp_name, resort_name, designation, strftime("%d-%m-%Y",date_of_posting)  FROM employee_posting ep, employee e, resort r WHERE ep.employee_id = e.employee_id and ep.resort_id = r.resort_id',
    ).fetchall()

    return render_template('employee/postinglist.html', posting = employee)

@bp.route('/employee/<employeeid>/deleteposting', methods=('GET', 'POST'))
@login_required
def deleteposting(employeeid):
    db = get_db()
    db.execute(
        'DELETE FROM employee_posting WHERE employee_id = ?',
        (employeeid,),
    )
    db.commit()
    flash('Posting record has been deleted')
    return redirect(url_for('emp.postinglist'))
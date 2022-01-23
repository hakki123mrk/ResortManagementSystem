DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS resort;
DROP TABLE IF EXISTS room_types;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS employee_posting;
DROP TABLE IF EXISTS id_types;
DROP TABLE IF EXISTS guests;
DROP TABLE IF EXISTS additional_services;
DROP TABLE IF EXISTS occupants;
DROP TABLE IF EXISTS availed_additional_services;

CREATE TABLE admin (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin VARCHAR2(20) UNIQUE,
    passwd TEXT NOT NULL
);

CREATE TABLE resort(
    resort_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resort_name VARCHAR2(15),
    location VARCHAR2(15)
);

CREATE TABLE room_types(
    room_type_id VARCHAR2(6) PRIMARY KEY,
    room_type VARCHAR2(20),
    room_price FLOAT
);

CREATE TABLE rooms(
    resort_id NUMBER(5) REFERENCES resort(resort_id) ON DELETE CASCADE,
    room_number INTEGER PRIMARY KEY AUTOINCREMENT,
    room_type_id NUMBER(3) REFERENCES room_types(room_type_id) ON DELETE CASCADE,
    status INTEGER DEFAULT 0,
    CHECK (status IN(0, 1))
);

CREATE TABLE employee(
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_name VARCHAR2(20),
    phoneno NUMBER(11) UNIQUE,
    address VARCHAR2(20),
    salary FLOAT
);

CREATE TABLE employee_posting(
    employee_id NUMBER(5) REFERENCES employee(employee_id) ON DELETE CASCADE,
    resort_id NUMBER(5) REFERENCES resort(resort_id) ON DELETE CASCADE,
    designation VARCHAR2(20),
    date_of_posting DATE DEFAULT (datetime('now'))
);

CREATE TABLE id_types(
    id_type VARCHAR2(5) PRIMARY KEY,
    id_name VARCHAR2(30)
);

CREATE TABLE guests(
    guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name VARCHAR2(20), 
    id_type VARCHAR2(8) REFERENCES id_types(id_type),
    id_number NUMBER(12) UNIQUE,
    address VARCHAR2(20),
    phone NUMBER(11) UNIQUE
);

CREATE TABLE occupants (
    guest_id NUMBER(5) REFERENCES guests(guest_id) UNIQUE,
    resort_id NUMBER(5) REFERENCES resort(resort_id),
    room_number NUMBER(5) REFERENCES rooms(room_number),
    number_of_occupants NUMBER(1),
    check_in_date DATE DEFAULT (datetime('now')),
    check_out_date DATE,
    CHECK (number_of_occupants > 0)
);

CREATE TABLE additional_services (
    service_id VARCHAR2(5) PRIMARY KEY,
    service_name VARCHAR2(25),
    price FLOAT
);

CREATE TABLE availed_additional_services (
    guest_id NUMBER(5) REFERENCES occupants(guest_id) ON DELETE CASCADE,
    service_id NUMBER(5) REFERENCES additional_services(service_id)
);

INSERT INTO sqlite_sequence VALUES('admin', 100);
INSERT INTO sqlite_sequence VALUES('resort', 500);
INSERT INTO sqlite_sequence VALUES( 'rooms', 1000);
INSERT INTO sqlite_sequence VALUES( 'employee', 100000);
INSERT INTO sqlite_sequence VALUES( 'guests', 500000);

INSERT INTO room_types VALUES ('SNGL', 'Single Bedroom', 800.0);
INSERT INTO room_types VALUES ('SMDL', 'Semi Deluxe', 1500.0);
INSERT INTO room_types VALUES ('FDLX', 'Deluxe', 2000.0);

INSERT INTO id_types VALUES('ADHAR', 'Aadhar Card');
INSERT INTO id_types VALUES('DL', 'Driving License');
INSERT INTO id_types VALUES('PAN', 'PAN Card');
INSERT INTO id_types VALUES('VOTID', 'Voter ID');
INSERT INTO id_types VALUES('PASSP', 'Passport');

INSERT INTO additional_services VALUES('WTRSK', 'Water Skiing', 300.00);
INSERT INTO additional_services VALUES('GLF', 'Golf', 800.00);
INSERT INTO additional_services VALUES('RKCLM', 'Rock Climbing', 300.00);
INSERT INTO additional_services VALUES('SCDIV', 'Scuba Diving', 500.00);
INSERT INTO additional_services VALUES('OFFRD', 'Off Road Driving', 1000.00);
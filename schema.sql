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
DROP TRIGGER IF EXISTS status_occupied;
DROP TRIGGER IF EXISTS status_UNoccupied;

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
    date_of_posting DATE DEFAULT (date('now'))
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
    check_in_date DATE DEFAULT (date()),
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

CREATE TRIGGER status_occupied
AFTER INSERT ON occupants
BEGIN
    UPDATE rooms SET status = 1 WHERE room_number = new.room_number;
END;

CREATE TRIGGER status_unoccupied
AFTER DELETE ON occupants
BEGIN
    UPDATE rooms SET status = 0 WHERE room_number = old.room_number;
END;

CREATE VIEW checked_in_guests (
    resort_id,
    guest_count
)
AS
SELECT
    r.resort_id,
    COUNT(guest_id)
    FROM resort r
    LEFT JOIN occupants o ON r.resort_id = o.resort_id
    GROUP BY r.resort_id;

CREATE VIEW available_rooms(
    resort_id,
    available_rooms
)
AS
SELECT 
    r.resort_id,
    count(room_number)
    FROM resort r
    LEFT JOIN rooms rm ON r.resort_id = rm.resort_id
    WHERE room_number NOT IN (SELECT room_number FROM occupants)
    GROUP BY r.resort_id;

CREATE VIEW posted_employees (
    resort_id,
    employee_count
)
AS
SELECT
    r.resort_id,
    COUNT(employee_id)
    FROM resort r
    LEFT JOIN employee_posting ep ON r.resort_id = ep.resort_id
    GROUP BY r.resort_id;

CREATE VIEW indexdata (
    resort_id,
    checked_guests,
    available_rooms,
    posted_employees
)
AS 
SELECT resort_name,
    guest_count,
    available_rooms,
    employee_count
FROM resort r
LEFT JOIN checked_in_guests o ON r.resort_id = o.resort_id
LEFT JOIN available_rooms rm ON r.resort_id = rm.resort_id
LEFT JOIN posted_employees pe ON r.resort_id = pe.resort_id
GROUP BY r.resort_id;

CREATE VIEW checkoutlist
AS
SELECT 
        o.guest_id,
        guest_name,
        resort_name,
        room_number
    FROM
        occupants o,
        guests g,
        resort r
    WHERE o.guest_id = g .guest_id and o.resort_id = r.resort_id 
    group by g.guest_id 
    having date(check_out_date) = date();

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
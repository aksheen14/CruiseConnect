-- CruiseConnect schema (Checkpoint 2)
PRAGMA foreign_keys = ON;

CREATE TABLE Staff (
    s_staff_id INTEGER PRIMARY KEY,
    s_name VARCHAR(100) NOT NULL,
    s_role VARCHAR(100),
    s_department VARCHAR(100)
);

CREATE TABLE Cabin (
    c_cabin_id INTEGER PRIMARY KEY,
    c_cabin_number VARCHAR(10) NOT NULL,
    c_deck INTEGER,
    c_capacity INTEGER NOT NULL CHECK (c_capacity > 0),
    c_current_size INTEGER DEFAULT 0 CHECK (c_current_size BETWEEN 0 AND c_capacity),
    c_staff_id INTEGER REFERENCES Staff(s_staff_id)
);

CREATE TABLE Passenger (
    p_passenger_id INTEGER PRIMARY KEY,
    p_name VARCHAR(150) NOT NULL,
    p_email VARCHAR(100) NOT NULL UNIQUE,
    p_phone VARCHAR(20),
    p_age INTEGER,
    p_cabin_id INTEGER NOT NULL REFERENCES Cabin(c_cabin_id)
);

CREATE TABLE Excursion (
    ex_excursion_id INTEGER PRIMARY KEY,
    ex_port_name VARCHAR(100) NOT NULL,
    ex_description TEXT,
    ex_cost DECIMAL(10,2) NOT NULL CHECK (ex_cost >= 0),
    ex_excursion_date DATE NOT NULL,
    ex_capacity INTEGER NOT NULL CHECK (ex_capacity > 0),
    ex_current_size INTEGER DEFAULT 0 CHECK (ex_current_size BETWEEN 0 AND ex_capacity),
    ex_staff_id INTEGER REFERENCES Staff(s_staff_id)
);

-- dv_capacity is the number of people the venue can seat at one time.
CREATE TABLE Dining_Venues (
    dv_venue_id INTEGER PRIMARY KEY,
    dv_name VARCHAR(100) NOT NULL,
    dv_cuisine_type VARCHAR(50),
    dv_capacity INTEGER NOT NULL CHECK (dv_capacity > 0),
    dv_staff_id INTEGER REFERENCES Staff(s_staff_id)
);

CREATE TABLE Event (
    ev_event_id INTEGER PRIMARY KEY,
    ev_name VARCHAR(150) NOT NULL,
    ev_location VARCHAR(100),
    ev_event_time DATETIME NOT NULL,
    ev_capacity INTEGER NOT NULL CHECK (ev_capacity > 0),
    ev_current_size INTEGER DEFAULT 0 CHECK (ev_current_size BETWEEN 0 AND ev_capacity),
    ev_staff_id INTEGER REFERENCES Staff(s_staff_id)
);

CREATE TABLE Books_Excursion (
    p_passenger_id INTEGER REFERENCES Passenger(p_passenger_id) ON DELETE CASCADE,
    ex_excursion_id INTEGER REFERENCES Excursion(ex_excursion_id) ON DELETE CASCADE,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (p_passenger_id, ex_excursion_id)
);

-- Every reservation occupies its venue for 90 minutes from reservation_time.
CREATE TABLE Reserves_Dining (
    p_passenger_id INTEGER REFERENCES Passenger(p_passenger_id) ON DELETE CASCADE,
    dv_venue_id INTEGER REFERENCES Dining_Venues(dv_venue_id) ON DELETE CASCADE,
    reservation_time DATETIME NOT NULL,
    party_size INTEGER NOT NULL CHECK (party_size > 0),
    PRIMARY KEY (p_passenger_id, dv_venue_id, reservation_time)
);

CREATE TABLE RSVPs_Event (
    p_passenger_id INTEGER REFERENCES Passenger(p_passenger_id) ON DELETE CASCADE,
    ev_event_id INTEGER REFERENCES Event(ev_event_id) ON DELETE CASCADE,
    rsvp_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (p_passenger_id, ev_event_id)
);

CREATE INDEX idx_books_excursion_excursion ON Books_Excursion(ex_excursion_id);
CREATE INDEX idx_reserves_dining_venue_time ON Reserves_Dining(dv_venue_id, reservation_time);
CREATE INDEX idx_rsvps_event_event ON RSVPs_Event(ev_event_id);

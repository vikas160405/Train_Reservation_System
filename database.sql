-- TRAIN RESERVATION SYSTEM
-- Clean schema based on the supplied database1.sql export.
-- Credentials, CREATE USER, GRANT, demo records, and test queries are excluded.

CREATE DATABASE IF NOT EXISTS train_reservation_system;
USE train_reservation_system;

CREATE TABLE IF NOT EXISTS trains (
    train_id INT AUTO_INCREMENT PRIMARY KEY,
    train_number VARCHAR(10) UNIQUE NOT NULL,
    train_name VARCHAR(100) NOT NULL,
    train_type VARCHAR(50),
    source_station VARCHAR(100) NOT NULL,
    destination_station VARCHAR(100) NOT NULL,
    total_seats INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_code VARCHAR(10) UNIQUE NOT NULL,
    station_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    departure_datetime DATETIME NOT NULL,
    arrival_datetime DATETIME NOT NULL,
    schedule_status ENUM('SCHEDULED', 'DELAYED', 'CANCELLED')
        DEFAULT 'SCHEDULED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (train_id) REFERENCES trains(train_id)
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    seat_class ENUM('SL', '3A', '2A', '1A', 'CC') NOT NULL,
    seat_status ENUM('AVAILABLE', 'BOOKED', 'BLOCKED') DEFAULT 'AVAILABLE',
    UNIQUE (schedule_id, seat_number),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_role ENUM('CUSTOMER', 'ADMIN') DEFAULT 'CUSTOMER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS passengers (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL,
    passenger_type ENUM('ADULT', 'CHILD', 'SENIOR_CITIZEN') DEFAULT 'ADULT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    CHECK (age >= 0 AND age <= 120)
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    pnr_number VARCHAR(20) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    booking_status ENUM('CONFIRMED', 'RAC', 'WAITLIST', 'CANCELLED')
        DEFAULT 'CONFIRMED',
    total_fare DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id),
    CHECK (total_fare >= 0)
);

CREATE TABLE IF NOT EXISTS booking_passengers (
    booking_passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    passenger_id INT NOT NULL,
    seat_id INT NULL,
    passenger_fare DECIMAL(10,2) NOT NULL,
    UNIQUE (booking_id, passenger_id),
    UNIQUE (booking_id, seat_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id),
    CHECK (passenger_fare >= 0)
);

CREATE TABLE IF NOT EXISTS cancellations (
    cancellation_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    cancellation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancellation_reason VARCHAR(255),
    refund_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    cancellation_status ENUM('PROCESSED', 'PENDING', 'REJECTED')
        DEFAULT 'PENDING',
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    CHECK (refund_amount >= 0)
);

CREATE TABLE IF NOT EXISTS waitlist (
    waitlist_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    passenger_id INT NOT NULL,
    schedule_id INT NOT NULL,
    waitlist_position INT NOT NULL,
    waitlist_status ENUM('WAITING', 'PROMOTED', 'CANCELLED') DEFAULT 'WAITING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (schedule_id, waitlist_position),
    UNIQUE (booking_id, passenger_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id),
    CHECK (waitlist_position > 0)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    payment_method ENUM('UPI', 'CARD', 'NET_BANKING', 'WALLET', 'CASH') NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('SUCCESS', 'FAILED', 'PENDING', 'REFUNDED') DEFAULT 'PENDING',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    CHECK (payment_amount >= 0)
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    booking_passenger_id INT NOT NULL,
    ticket_number VARCHAR(30) UNIQUE NOT NULL,
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ticket_status ENUM('ACTIVE', 'CANCELLED') DEFAULT 'ACTIVE',
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (booking_passenger_id)
        REFERENCES booking_passengers(booking_passenger_id)
);

SHOW TABLES;

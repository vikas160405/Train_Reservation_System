import mysql.connector
import hashlib
import secrets

from database import create_connection

logged_in_user = None

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# User Registration
def register_user():

    print("\n===== USER REGISTRATION =====")

    full_name = input("Enter your name: ")
    email = input("Enter your email: ")
    phone = input("Enter your phone: ")
    password = input("Create password: ")

    password_hash = hash_password(password)

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        INSERT INTO users
        (full_name, email, phone, password_hash)
        VALUES (%s, %s, %s, %s)
        """

        try:
            cursor.execute(
                query,
                (full_name, email, phone, password_hash)
            )

            connection.commit()

            print("Registration Successful!")

        except mysql.connector.Error as error:
            connection.rollback()
            print("Error:", error)

        finally:
            cursor.close()
            connection.close()


# User Login
def login_user():

    global logged_in_user

    print("\n===== USER LOGIN =====")

    email = input("Enter email: ")
    password = input("Enter password: ")

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT user_id, full_name, user_role
        FROM users
        WHERE email = %s AND password_hash = %s
        """

        cursor.execute(
            query,
            (email, hash_password(password))
        )

        user = cursor.fetchone()

        if user:
            logged_in_user = {
                "user_id": user[0],
                "full_name": user[1],
                "user_role": user[2]
            }

            print("\nLogin Successful!")
            print("Welcome", user[1])
            print("User ID:", user[0])
            print("Role:", user[2])

        else:
            print("Invalid Credentials!")

        cursor.close()
        connection.close()

def search_trains():

    print("\n===== SEARCH TRAINS =====")

    source = input("Enter source station: ")
    destination = input("Enter destination station: ")
    journey_date = input("Enter journey date (YYYY-MM-DD): ")

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT
            t.train_number,
            t.train_name,
            t.source_station,
            t.destination_station,
            s.departure_datetime,
            s.arrival_datetime
        FROM trains t
        INNER JOIN schedules s
            ON t.train_id = s.train_id
        WHERE t.source_station = %s
          AND t.destination_station = %s
          AND DATE(s.departure_datetime) = %s
          AND s.schedule_status != 'CANCELLED'
        ORDER BY s.departure_datetime
        """

        cursor.execute(query, (source, destination, journey_date))

        trains = cursor.fetchall()

        if trains:
            for train in trains:
                print("\n-------------------------")
                print("Train Number:", train[0])
                print("Train Name:", train[1])
                print("Source:", train[2])
                print("Destination:", train[3])
                print("Departure:", train[4])
                print("Arrival:", train[5])
        else:
            print("No trains found!")

        cursor.close()
        connection.close()
        
def check_seat_availability():

    print("\n===== SEAT AVAILABILITY =====")

    train_number = input("Enter train number: ").strip()
    journey_date = input("Enter journey date (YYYY-MM-DD): ").strip()

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT
            t.train_name,
            se.seat_class,
            COUNT(se.seat_id) AS total_seats,
            SUM(
                CASE
                    WHEN se.seat_status = 'AVAILABLE'
                    THEN 1 ELSE 0
                END
            ) AS available_seats
        FROM trains t
        JOIN schedules s
            ON t.train_id = s.train_id
        JOIN seats se
            ON s.schedule_id = se.schedule_id
        WHERE t.train_number = %s
          AND DATE(s.departure_datetime) = %s
          AND s.schedule_status != 'CANCELLED'
        GROUP BY t.train_name, se.seat_class
        ORDER BY se.seat_class
        """

        try:
            cursor.execute(query, (train_number, journey_date))
            results = cursor.fetchall()

            if results:
                print("\nTrain:", results[0][0])
                print("\nClass\tTotal Seats\tAvailable Seats")

                for row in results:
                    print(
                        row[1], "\t",
                        row[2], "\t\t",
                        row[3]
                    )
            else:
                print("No seat records found!")

        except mysql.connector.Error as error:
            print("Error:", error)

        finally:
            cursor.close()
            connection.close()

def register_passenger():

    print("\n===== PASSENGER REGISTRATION =====")

    if logged_in_user is None:
        print("Please login first!")
        return

    user_id = logged_in_user["user_id"]
    full_name = input("Enter passenger name: ").strip()
    age = int(input("Enter passenger age: "))
    gender = input("Enter gender (MALE/FEMALE/OTHER): ").strip().upper()

    if age < 0 or age > 120:
        print("Invalid age!")
        return

    if gender not in ["MALE", "FEMALE", "OTHER"]:
        print("Invalid gender!")
        return

    if age < 18:
        passenger_type = "CHILD"
    elif age >= 60:
        passenger_type = "SENIOR_CITIZEN"
    else:
        passenger_type = "ADULT"

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        INSERT INTO passengers
        (user_id, full_name, age, gender, passenger_type)
        VALUES (%s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(
                query,
                (user_id, full_name, age, gender, passenger_type)
            )

            connection.commit()

            print("\nPassenger registered successfully!")
            print("Passenger ID:", cursor.lastrowid)
            print("Passenger Type:", passenger_type)

        except mysql.connector.Error as error:
            connection.rollback()
            print("Registration failed:", error)

        finally:
            cursor.close()
            connection.close()

def view_passengers():

    print("\n===== REGISTERED PASSENGERS =====")

    if logged_in_user is None:
        print("Please login first!")
        return

    user_id = logged_in_user["user_id"]

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT passenger_id, full_name, age, gender, passenger_type
        FROM passengers
        WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))

        passengers = cursor.fetchall()

        if passengers:
            for passenger in passengers:
                print("----------------------------")
                print("Passenger ID:", passenger[0])
                print("Name:", passenger[1])
                print("Age:", passenger[2])
                print("Gender:", passenger[3])
                print("Type:", passenger[4])
        else:
            print("No passengers registered!")

        cursor.close()
        connection.close()
        

def select_passenger_for_booking():

    print("\n===== SELECT PASSENGER FOR BOOKING =====")

    # Check login
    if logged_in_user is None:
        print("Please login first!")
        return None

    user_id = logged_in_user["user_id"]

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT passenger_id, full_name, age, gender
        FROM passengers
        WHERE user_id = %s
        ORDER BY passenger_id
        """

        try:
            cursor.execute(query, (user_id,))
            passengers = cursor.fetchall()

            if not passengers:
                print("No passengers found!")
                print("Please register a passenger first.")
                return None

            print("\nAvailable Passengers:")

            for passenger in passengers:
                print("-----------------------------")
                print("Passenger ID:", passenger[0])
                print("Name:", passenger[1])
                print("Age:", passenger[2])
                print("Gender:", passenger[3])

            passenger_id = int(
                input("\nEnter Passenger ID to select: ")
            )

            selected_passenger = next(
                (p for p in passengers if p[0] == passenger_id),
                None
            )

            if selected_passenger:
                print("\nPassenger selected successfully!")
                print("Selected:", selected_passenger[1])

                return selected_passenger[0]

            else:
                print("Invalid Passenger ID!")
                return None

        except (mysql.connector.Error, ValueError) as error:
            print("Error:", error)
            return None

        finally:
            cursor.close()
            connection.close()

    return None


def select_train_for_booking():

    print("\n===== SELECT TRAIN FOR BOOKING =====")

    source = input("Enter source station: ").strip()
    destination = input("Enter destination station: ").strip()
    journey_date = input("Enter journey date (YYYY-MM-DD): ").strip()

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT
            s.schedule_id,
            t.train_number,
            t.train_name,
            t.source_station,
            t.destination_station,
            s.departure_datetime,
            s.arrival_datetime
        FROM trains t
        JOIN schedules s
            ON t.train_id = s.train_id
        WHERE LOWER(t.source_station) = LOWER(%s)
          AND LOWER(t.destination_station) = LOWER(%s)
          AND DATE(s.departure_datetime) = %s
          AND s.schedule_status != 'CANCELLED'
        ORDER BY s.departure_datetime
        """

        try:
            cursor.execute(
                query,
                (source, destination, journey_date)
            )

            trains = cursor.fetchall()

            if not trains:
                print("No trains found for this route and date!")
                return None

            print("\nAvailable Trains:")

            for train in trains:
                print("-----------------------------")
                print("Schedule ID:", train[0])
                print("Train Number:", train[1])
                print("Train Name:", train[2])
                print("Source:", train[3])
                print("Destination:", train[4])
                print("Departure:", train[5])
                print("Arrival:", train[6])

            schedule_id = int(
                input("\nEnter Schedule ID to select: ")
            )

            selected_train = next(
                (train for train in trains if train[0] == schedule_id),
                None
            )

            if selected_train:
                print("\nTrain selected successfully!")
                print("Train:", selected_train[2])
                print("Schedule ID:", selected_train[0])

                return selected_train[0]

            else:
                print("Invalid Schedule ID!")
                return None

        except (mysql.connector.Error, ValueError) as error:
            print("Error:", error)
            return None

        finally:
            cursor.close()
            connection.close()

    return None


def select_class_for_booking(schedule_id):

    print("\n===== SELECT TRAVEL CLASS =====")

    print("1. SL - Sleeper")
    print("2. 3A - AC 3 Tier")
    print("3. 2A - AC 2 Tier")
    print("4. 1A - AC First Class")
    print("5. CC - Chair Car")

    class_options = {
        "1": "SL",
        "2": "3A",
        "3": "2A",
        "4": "1A",
        "5": "CC"
    }

    choice = input("\nSelect travel class: ").strip()

    if choice not in class_options:
        print("Invalid class selection!")
        return None

    seat_class = class_options[choice]

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT
            COUNT(*) AS total_seats,
            SUM(
                CASE
                    WHEN seat_status = 'AVAILABLE'
                    THEN 1 ELSE 0
                END
            ) AS available_seats
        FROM seats
        WHERE schedule_id = %s
          AND seat_class = %s
        """

        try:
            cursor.execute(query, (schedule_id, seat_class))
            result = cursor.fetchone()

            total_seats = result[0]
            available_seats = result[1] or 0

            print("\n===== SEAT AVAILABILITY =====")
            print("Travel Class:", seat_class)
            print("Total Seats:", total_seats)
            print("Available Seats:", available_seats)

            if available_seats == 0:
                print("No seats available in this class!")
                return None

            print("\nTravel class selected successfully!")

            return seat_class

        except mysql.connector.Error as error:
            print("Error:", error)
            return None

        finally:
            cursor.close()
            connection.close()

    return None


def select_seat_for_booking(schedule_id, seat_class):

    print("\n===== SELECT YOUR SEAT =====")

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT seat_id, seat_number, seat_class
        FROM seats
        WHERE schedule_id = %s
          AND seat_class = %s
          AND seat_status = 'AVAILABLE'
        ORDER BY seat_number
        """

        try:
            cursor.execute(query, (schedule_id, seat_class))
            seats = cursor.fetchall()

            if not seats:
                print("No available seats found!")
                return None

            print("\nAvailable Seats:")

            for seat in seats:
                print(
                    "Seat ID:", seat[0],
                    "| Seat Number:", seat[1],
                    "| Class:", seat[2]
                )

            seat_id = int(input("\nEnter Seat ID to select: "))

            selected_seat = next(
                (seat for seat in seats if seat[0] == seat_id),
                None
            )

            if selected_seat:
                print("\nSeat selected successfully!")
                print("Seat Number:", selected_seat[1])
                print("Seat ID:", selected_seat[0])

                return selected_seat[0]

            else:
                print("Invalid Seat ID!")
                return None

        except (mysql.connector.Error, ValueError) as error:
            print("Error:", error)
            return None

        finally:
            cursor.close()
            connection.close()

    return None


def reserve_seat(schedule_id, seat_id, seat_class):
    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return False

    cursor = connection.cursor(dictionary=True)

    try:
        # Start a database transaction
        connection.start_transaction()

        # Lock the selected seat until this transaction finishes
        cursor.execute("""
            SELECT seat_id, seat_number, seat_status
            FROM seats
            WHERE seat_id = %s
              AND schedule_id = %s
              AND seat_class = %s
              AND seat_status = 'AVAILABLE'
            FOR UPDATE
        """, (seat_id, schedule_id, seat_class))

        seat = cursor.fetchone()

        if seat is None:
            print("Sorry! This seat is not available.")
            connection.rollback()
            return False

        # Change the seat status to BOOKED
        cursor.execute("""
            UPDATE seats
            SET seat_status = 'BOOKED'
            WHERE seat_id = %s
              AND seat_status = 'AVAILABLE'
        """, (seat_id,))

        if cursor.rowcount != 1:
            print("Seat reservation failed!")
            connection.rollback()
            return False

        connection.commit()

        print(f"Seat {seat['seat_number']} reserved successfully!")
        return True

    except mysql.connector.Error as error:
        connection.rollback()
        print("Seat reservation error:", error)
        return False

    finally:
        cursor.close()
        connection.close()


def calculate_booking_fare(seat_class, number_of_passengers):

    print("\n===== BOOKING FARE CALCULATION =====")

    fare_chart = {
        "SL": 250,
        "3A": 750,
        "2A": 1200,
        "1A": 2000,
        "CC": 500
    }

    if seat_class not in fare_chart:
        print("Invalid seat class!")
        return None

    if number_of_passengers <= 0:
        print("Invalid passenger count!")
        return None

    fare_per_person = fare_chart[seat_class]

    total_fare = fare_per_person * number_of_passengers

    print("\n===== FARE DETAILS =====")
    print("Travel Class:", seat_class)
    print("Fare Per Passenger: ₹", fare_per_person)
    print("Number of Passengers:", number_of_passengers)
    print("Total Booking Fare: ₹", total_fare)

    return total_fare


def select_seat():

    print("\n===== SELECT YOUR SEAT =====")

    train_number = input("Enter train number: ").strip()
    journey_date = input("Enter journey date (YYYY-MM-DD): ").strip()
    seat_class = input("Enter class (SL/3A/2A/1A/CC): ").strip().upper()

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        query = """
        SELECT
            se.seat_id,
            se.seat_number,
            se.seat_class
        FROM seats se
        JOIN schedules s
            ON se.schedule_id = s.schedule_id
        JOIN trains t
            ON s.train_id = t.train_id
        WHERE t.train_number = %s
          AND DATE(s.departure_datetime) = %s
          AND se.seat_class = %s
          AND se.seat_status = 'AVAILABLE'
          AND s.schedule_status != 'CANCELLED'
        ORDER BY se.seat_number
        """

        try:
            cursor.execute(
                query,
                (train_number, journey_date, seat_class)
            )

            seats = cursor.fetchall()

            if seats:
                print("\nAvailable Seats:")

                for seat in seats:
                    print(
                        "Seat ID:", seat[0],
                        "| Seat Number:", seat[1],
                        "| Class:", seat[2]
                    )

                seat_id = int(input("\nEnter Seat ID to select: "))

                selected_seat = next(
                    (seat for seat in seats if seat[0] == seat_id),
                    None
                )

                if selected_seat:
                    print("\nSeat selected successfully!")
                    print("Selected Seat:", selected_seat[1])
                    print("Seat ID:", selected_seat[0])
                else:
                    print("Invalid seat selection!")

            else:
                print("No available seats found!")

        except (mysql.connector.Error, ValueError) as error:
            print("Error:", error)

        finally:
            cursor.close()
            connection.close()

def calculate_fare():

    print("\n===== TICKET FARE CALCULATOR =====")

    fare_chart = {
        "SL": 250,
        "3A": 750,
        "2A": 1200,
        "1A": 2000,
        "CC": 500
    }

    seat_class = input(
        "Enter seat class (SL/3A/2A/1A/CC): "
    ).strip().upper()

    number_of_passengers = int(
        input("Enter number of passengers: ")
    )

    if seat_class not in fare_chart:
        print("Invalid seat class!")
        return

    if number_of_passengers <= 0:
        print("Invalid passenger count!")
        return

    fare_per_person = fare_chart[seat_class]

    total_fare = fare_per_person * number_of_passengers

    print("\n===== FARE DETAILS =====")
    print("Seat Class:", seat_class)
    print("Fare Per Passenger: ₹", fare_per_person)
    print("Number of Passengers:", number_of_passengers)
    print("Total Fare: ₹", total_fare)

import random


def generate_pnr():

    pnr = ""

    for i in range(10):
        digit = secrets.randbelow(10)
        pnr += str(digit)

    return pnr


def save_booking(schedule_id, total_fare):

    print("\n===== SAVE TICKET BOOKING =====")

    if logged_in_user is None:
        print("Please login first!")
        return None

    user_id = logged_in_user["user_id"]

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        try:
            # Generate a unique PNR
            while True:
                pnr = generate_pnr()

                cursor.execute(
                    "SELECT booking_id FROM bookings WHERE pnr_number = %s",
                    (pnr,)
                )

                if cursor.fetchone() is None:
                    break

            query = """
            INSERT INTO bookings
            (pnr_number, user_id, schedule_id, total_fare)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (pnr, user_id, schedule_id, total_fare)
            )

            connection.commit()

            booking_id = cursor.lastrowid

            print("\nBooking saved successfully!")
            print("Booking ID:", booking_id)
            print("PNR Number:", pnr)
            print("Total Fare: ₹", total_fare)
            print("Booking Status: CONFIRMED")

            return booking_id

        except mysql.connector.Error as error:
            connection.rollback()
            print("Booking failed:", error)
            return None

        finally:
            cursor.close()
            connection.close()

    return None


def add_passenger_to_booking(booking_id, passenger_id, seat_id, passenger_fare):

    print("\n===== ADD PASSENGER TO BOOKING =====")

    connection = create_connection()

    if connection:
        cursor = connection.cursor()

        try:
            # Verify that the passenger belongs to the logged-in user
            query = """
            SELECT passenger_id
            FROM passengers
            WHERE passenger_id = %s
              AND user_id = %s
            """

            cursor.execute(
                query,
                (passenger_id, logged_in_user["user_id"])
            )

            passenger = cursor.fetchone()

            if passenger is None:
                print("Invalid passenger or passenger does not belong to you!")
                return None

            # Insert passenger into booking
            insert_query = """
            INSERT INTO booking_passengers
            (booking_id, passenger_id, seat_id, passenger_fare)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                insert_query,
                (booking_id, passenger_id, seat_id, passenger_fare)
            )

            connection.commit()

            booking_passenger_id = cursor.lastrowid

            print("\nPassenger added to booking successfully!")
            print("Booking Passenger ID:", booking_passenger_id)

            return booking_passenger_id

        except mysql.connector.Error as error:
            connection.rollback()
            print("Error:", error)
            return None

        finally:
            cursor.close()
            connection.close()

    return None


def confirm_booking(passenger_id, schedule_id, seat_class, seat_id, total_fare):

    if logged_in_user is None:
        print("Please login first!")
        return None

    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        # Start one transaction
        connection.start_transaction()

        user_id = logged_in_user["user_id"]

        # Step 1: Verify passenger ownership
        cursor.execute("""
            SELECT passenger_id, full_name
            FROM passengers
            WHERE passenger_id = %s
              AND user_id = %s
        """, (passenger_id, user_id))

        passenger = cursor.fetchone()

        if passenger is None:
            print("Invalid passenger selection!")
            connection.rollback()
            return None

        # Step 2: Lock and verify the selected seat
        cursor.execute("""
            SELECT seat_id, seat_number
            FROM seats
            WHERE seat_id = %s
              AND schedule_id = %s
              AND seat_class = %s
              AND seat_status = 'AVAILABLE'
            FOR UPDATE
        """, (seat_id, schedule_id, seat_class))

        seat = cursor.fetchone()

        if seat is None:
            print("Selected seat is no longer available!")
            connection.rollback()
            return None

        # Step 3: Generate a unique PNR
        while True:
            pnr = generate_pnr()

            cursor.execute("""
                SELECT booking_id
                FROM bookings
                WHERE pnr_number = %s
            """, (pnr,))

            if cursor.fetchone() is None:
                break

        # Step 4: Insert booking
        cursor.execute("""
            INSERT INTO bookings
            (pnr_number, user_id, schedule_id, total_fare)
            VALUES (%s, %s, %s, %s)
        """, (pnr, user_id, schedule_id, total_fare))

        booking_id = cursor.lastrowid

        # Step 5: Link passenger and seat to booking
        cursor.execute("""
            INSERT INTO booking_passengers
            (booking_id, passenger_id, seat_id, passenger_fare)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, passenger_id, seat_id, total_fare))

        # Step 6: Mark seat as BOOKED
        cursor.execute("""
            UPDATE seats
            SET seat_status = 'BOOKED'
            WHERE seat_id = %s
              AND seat_status = 'AVAILABLE'
        """, (seat_id,))

        if cursor.rowcount != 1:
            raise Exception("Seat reservation failed!")

        # Step 7: Commit all operations together
        connection.commit()

        print("\n========== BOOKING CONFIRMED ==========")
        print("Booking ID:", booking_id)
        print("PNR Number:", pnr)
        print("Passenger:", passenger["full_name"])
        print("Seat Number:", seat["seat_number"])
        print("Travel Class:", seat_class)
        print("Total Fare: ₹", total_fare)
        print("Booking Status: CONFIRMED")
        print("=======================================")

        return booking_id

    except Exception as error:
        connection.rollback()
        print("Booking failed:", error)
        print("All database changes have been rolled back.")
        return None

    finally:
        cursor.close()
        connection.close()


def book_ticket():

    print("\n========== TRAIN TICKET BOOKING ==========")

    if logged_in_user is None:
        print("Please login first!")
        return

    # 1. Select passenger
    passenger_id = select_passenger_for_booking()

    if passenger_id is None:
        return

    # 2. Select train and schedule
    schedule_id = select_train_for_booking()

    if schedule_id is None:
        return

    # 3. Select travel class
    seat_class = select_class_for_booking(schedule_id)

    if seat_class is None:
        return

    # 4. Select available seat
    seat_id = select_seat_for_booking(schedule_id, seat_class)

    if seat_id is None:
        return

    # 5. Calculate fare for one passenger
    total_fare = calculate_booking_fare(seat_class, 1)

    if total_fare is None:
        return

    print("\n========== BOOKING SUMMARY ==========")
    print("Passenger ID:", passenger_id)
    print("Schedule ID:", schedule_id)
    print("Travel Class:", seat_class)
    print("Seat ID:", seat_id)
    print("Total Fare: ₹", total_fare)

    confirmation = input("\nConfirm booking? (Y/N): ").strip().upper()

    if confirmation != "Y":
        print("Booking cancelled by user.")
        return

    # 6. Save everything in one transaction
    confirm_booking(
        passenger_id,
        schedule_id,
        seat_class,
        seat_id,
        total_fare
    )



def process_payment():

    print("\n========== PAYMENT PROCESSING ==========")

    if logged_in_user is None:
        print("Please login first!")
        return

    try:
        booking_id = int(input("Enter Booking ID: "))
    except ValueError:
        print("Invalid Booking ID!")
        return

    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = connection.cursor(dictionary=True)

    try:
        # Step 1: Verify booking ownership
        cursor.execute("""
            SELECT booking_id, pnr_number, total_fare, booking_status
            FROM bookings
            WHERE booking_id = %s
              AND user_id = %s
        """, (booking_id, logged_in_user["user_id"]))

        booking = cursor.fetchone()

        if booking is None:
            print("Booking not found or does not belong to you!")
            return

        if booking["booking_status"] != "CONFIRMED":
            print("Only confirmed bookings can be paid!")
            return

        # Step 2: Prevent duplicate successful payments
        cursor.execute("""
            SELECT payment_id
            FROM payments
            WHERE booking_id = %s
              AND payment_status = 'SUCCESS'
        """, (booking_id,))

        if cursor.fetchone():
            print("This booking has already been paid successfully!")
            return

        print("\nBooking ID:", booking["booking_id"])
        print("PNR:", booking["pnr_number"])
        print("Amount: ₹", booking["total_fare"])

        # Step 3: Select payment method
        print("\nPayment Methods:")
        print("1. UPI")
        print("2. Card")
        print("3. Net Banking")
        print("4. Wallet")
        print("5. Cash")

        methods = {
            "1": "UPI",
            "2": "CARD",
            "3": "NET_BANKING",
            "4": "WALLET",
            "5": "CASH"
        }

        choice = input("Select payment method: ").strip()

        if choice not in methods:
            print("Invalid payment method!")
            return

        payment_method = methods[choice]

        # Step 4: Simulate payment result
        print("\n1. Simulate Successful Payment")
        print("2. Simulate Failed Payment")

        result = input("Select payment result: ").strip()

        if result == "1":
            payment_status = "SUCCESS"
        elif result == "2":
            payment_status = "FAILED"
        else:
            print("Invalid payment result!")
            return

        # Step 5: Generate transaction ID
        transaction_id = "TXN" + secrets.token_hex(6).upper()

        # Step 6: Save payment record
        cursor.execute("""
            INSERT INTO payments
            (booking_id, transaction_id, payment_method,
             payment_amount, payment_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            booking_id,
            transaction_id,
            payment_method,
            booking["total_fare"],
            payment_status
        ))

        connection.commit()

        print("\n========== PAYMENT RESULT ==========")
        print("Booking ID:", booking_id)
        print("Transaction ID:", transaction_id)
        print("Payment Method:", payment_method)
        print("Payment Amount: ₹", booking["total_fare"])
        print("Payment Status:", payment_status)

        if payment_status == "SUCCESS":
            print("Payment completed successfully!")
        else:
            print("Payment failed. You can retry later.")

        print("====================================")

    except mysql.connector.Error as error:
        connection.rollback()
        print("Payment processing error:", error)

    finally:
        cursor.close()
        connection.close()


def generate_ticket():

    print("\n========== TRAIN TICKET GENERATION ==========")

    if logged_in_user is None:
        print("Please login first!")
        return

    pnr = input("Enter your PNR number: ").strip()

    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                b.booking_id,
                b.pnr_number,
                b.booking_status,
                b.total_fare,
                p.full_name,
                p.age,
                p.gender,
                t.train_number,
                t.train_name,
                t.source_station,
                t.destination_station,
                s.departure_datetime,
                s.arrival_datetime,
                se.seat_number,
                se.seat_class,
                py.payment_status
            FROM bookings b
            JOIN booking_passengers bp
                ON b.booking_id = bp.booking_id
            JOIN passengers p
                ON bp.passenger_id = p.passenger_id
            JOIN schedules s
                ON b.schedule_id = s.schedule_id
            JOIN trains t
                ON s.train_id = t.train_id
            LEFT JOIN seats se
                ON bp.seat_id = se.seat_id
            LEFT JOIN payments py
                ON b.booking_id = py.booking_id
            WHERE b.pnr_number = %s
              AND b.user_id = %s
            ORDER BY py.payment_date DESC
            LIMIT 1
        """

        cursor.execute(
            query,
            (pnr, logged_in_user["user_id"])
        )

        ticket = cursor.fetchone()

        if ticket is None:
            print("Ticket not found!")
            return

        if ticket["booking_status"] != "CONFIRMED":
            print("Booking is not confirmed!")
            return

        if ticket["payment_status"] != "SUCCESS":
            print("Payment is not successful. Ticket cannot be generated!")
            print("Current payment status:", ticket["payment_status"] or "NOT PAID")
            return

        print("\n")
        print("=" * 55)
        print("              TRAIN E-TICKET")
        print("=" * 55)

        print("PNR Number       :", ticket["pnr_number"])
        print("Booking ID       :", ticket["booking_id"])
        print("Passenger Name   :", ticket["full_name"])
        print("Age              :", ticket["age"])
        print("Gender           :", ticket["gender"])
        print("-" * 55)

        print("Train Number     :", ticket["train_number"])
        print("Train Name       :", ticket["train_name"])
        print("From             :", ticket["source_station"])
        print("To               :", ticket["destination_station"])
        print("Departure        :", ticket["departure_datetime"])
        print("Arrival          :", ticket["arrival_datetime"])
        print("-" * 55)

        print("Seat Number      :", ticket["seat_number"])
        print("Travel Class     :", ticket["seat_class"])
        print("Total Fare       : ₹", ticket["total_fare"])
        print("Payment Status   :", ticket["payment_status"])
        print("Booking Status   :", ticket["booking_status"])

        print("=" * 55)
        print("          HAPPY AND SAFE JOURNEY!")
        print("=" * 55)

    except mysql.connector.Error as error:
        print("Ticket generation error:", error)

    finally:
        cursor.close()
        connection.close()


def view_booking_history():

    print("\n========== MY BOOKING HISTORY ==========")

    if logged_in_user is None:
        print("Please login first!")
        return

    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                b.booking_id,
                b.pnr_number,
                t.train_name,
                t.train_number,
                t.source_station,
                t.destination_station,
                s.departure_datetime,
                b.total_fare,
                b.booking_status,
                COALESCE(
                    MAX(CASE
                        WHEN py.payment_status = 'SUCCESS'
                        THEN 'SUCCESS'
                    END),
                    'NOT PAID'
                ) AS payment_status
            FROM bookings b
            JOIN schedules s
                ON b.schedule_id = s.schedule_id
            JOIN trains t
                ON s.train_id = t.train_id
            LEFT JOIN payments py
                ON b.booking_id = py.booking_id
            WHERE b.user_id = %s
            GROUP BY
                b.booking_id,
                b.pnr_number,
                t.train_name,
                t.train_number,
                t.source_station,
                t.destination_station,
                s.departure_datetime,
                b.total_fare,
                b.booking_status
            ORDER BY b.booking_id DESC
        """

        cursor.execute(query, (logged_in_user["user_id"],))
        bookings = cursor.fetchall()

        if not bookings:
            print("No booking history found!")
            return

        for booking in bookings:
            print("\n----------------------------------------")
            print("Booking ID:", booking["booking_id"])
            print("PNR:", booking["pnr_number"])
            print("Train:", booking["train_name"])
            print("Train Number:", booking["train_number"])
            print("From:", booking["source_station"])
            print("To:", booking["destination_station"])
            print("Journey Date:", booking["departure_datetime"])
            print("Fare: ₹", booking["total_fare"])
            print("Booking Status:", booking["booking_status"])
            print("Payment Status:", booking["payment_status"])
            print("----------------------------------------")

    except mysql.connector.Error as error:
        print("Booking history error:", error)

    finally:
        cursor.close()
        connection.close()


def check_pnr_status():

    print("\n========== PNR STATUS CHECK ==========")

    if logged_in_user is None:
        print("Please login first!")
        return

    pnr = input("Enter your PNR number: ").strip()

    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                b.booking_id,
                b.pnr_number,
                b.booking_status,
                b.total_fare,
                t.train_name,
                t.train_number,
                t.source_station,
                t.destination_station,
                s.departure_datetime,
                p.full_name,
                se.seat_number,
                se.seat_class
            FROM bookings b
            JOIN schedules s ON b.schedule_id = s.schedule_id
            JOIN trains t ON s.train_id = t.train_id
            JOIN booking_passengers bp ON b.booking_id = bp.booking_id
            JOIN passengers p ON bp.passenger_id = p.passenger_id
            LEFT JOIN seats se ON bp.seat_id = se.seat_id
            WHERE b.pnr_number = %s
              AND b.user_id = %s
        """

        cursor.execute(
            query,
            (pnr, logged_in_user["user_id"])
        )

        results = cursor.fetchall()

        if not results:
            print("Invalid PNR or booking not found!")
            return

        for result in results:
            print("\n========== PNR DETAILS ==========")
            print("Booking ID:", result["booking_id"])
            print("PNR:", result["pnr_number"])
            print("Passenger:", result["full_name"])
            print("Train:", result["train_name"])
            print("Train Number:", result["train_number"])
            print("From:", result["source_station"])
            print("To:", result["destination_station"])
            print("Departure:", result["departure_datetime"])
            print("Seat:", result["seat_number"] or "Not assigned")
            print("Class:", result["seat_class"] or "Not assigned")
            print("Fare: ₹", result["total_fare"])
            print("Booking Status:", result["booking_status"])
            print("=================================")

    except mysql.connector.Error as error:
        print("PNR checking error:", error)

    finally:
        cursor.close()
        connection.close()


from datetime import datetime

def cancel_ticket():

    print("\n========== TICKET CANCELLATION ==========")

    if logged_in_user is None:
        print("Please login first!")
        return

    pnr = input("Enter PNR number: ").strip()
    reason = input("Enter cancellation reason: ").strip()

    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        # Step 1: Find and lock the booking
        cursor.execute("""
            SELECT
                b.booking_id,
                b.total_fare,
                b.booking_status,
                s.departure_datetime
            FROM bookings b
            JOIN schedules s ON b.schedule_id = s.schedule_id
            WHERE b.pnr_number = %s
              AND b.user_id = %s
            FOR UPDATE
        """, (pnr, logged_in_user["user_id"]))

        booking = cursor.fetchone()

        if booking is None:
            print("Booking not found!")
            connection.rollback()
            return

        if booking["booking_status"] != "CONFIRMED":
            print("This booking cannot be cancelled!")
            connection.rollback()
            return

        # Step 2: Check successful payment
        cursor.execute("""
            SELECT payment_id, payment_amount
            FROM payments
            WHERE booking_id = %s
              AND payment_status = 'SUCCESS'
            ORDER BY payment_id DESC
            LIMIT 1
            FOR UPDATE
        """, (booking["booking_id"],))

        payment = cursor.fetchone()

        if payment is None:
            print("No successful payment found. Cancellation refund unavailable.")
            connection.rollback()
            return

        # Step 3: Calculate refund
        now = datetime.now()
        departure = booking["departure_datetime"]
        hours_left = (departure - now).total_seconds() / 3600

        if hours_left > 24:
            refund_percentage = 0.90
        elif hours_left >= 0:
            refund_percentage = 0.50
        else:
            print("Journey has already started. Cancellation is not allowed.")
            connection.rollback()
            return

        refund_amount = round(
            float(payment["payment_amount"]) * refund_percentage, 2
        )

        print("\nCancellation Summary")
        print("PNR:", pnr)
        print("Original Payment: ₹", payment["payment_amount"])
        print("Refund Percentage:", refund_percentage * 100, "%")
        print("Refund Amount: ₹", refund_amount)

        confirmation = input(
            "\nConfirm cancellation? (Y/N): "
        ).strip().upper()

        if confirmation != "Y":
            connection.rollback()
            print("Cancellation aborted.")
            return

        # Step 4: Update booking status
        cursor.execute("""
            UPDATE bookings
            SET booking_status = 'CANCELLED'
            WHERE booking_id = %s
        """, (booking["booking_id"],))

        # Step 5: Release assigned seats
        cursor.execute("""
            UPDATE seats
            SET seat_status = 'AVAILABLE'
            WHERE seat_id IN (
                SELECT seat_id
                FROM (
                    SELECT seat_id
                    FROM booking_passengers
                    WHERE booking_id = %s
                      AND seat_id IS NOT NULL
                ) AS assigned_seats
            )
        """, (booking["booking_id"],))

        # Step 6: Save cancellation record
        cursor.execute("""
            INSERT INTO cancellations
            (booking_id, cancellation_reason,
             refund_amount, cancellation_status)
            VALUES (%s, %s, %s, 'PROCESSED')
        """, (
            booking["booking_id"],
            reason,
            refund_amount
        ))

        # Step 7: Update payment status
        cursor.execute("""
            UPDATE payments
            SET payment_status = 'REFUNDED'
            WHERE payment_id = %s
        """, (payment["payment_id"],))

        # Step 8: Commit everything
        connection.commit()

        print("\n========== CANCELLATION SUCCESSFUL ==========")
        print("PNR:", pnr)
        print("Booking Status: CANCELLED")
        print("Refund Amount: ₹", refund_amount)
        print("Refund Status: PROCESSED")
        print("Seat released successfully!")
        print("=============================================")

    except Exception as error:
        connection.rollback()
        print("Cancellation error:", error)

    finally:
        cursor.close()
        connection.close()



def add_to_waitlist(booking_id, passenger_id, schedule_id):
    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        # Validate booking and passenger
        cursor.execute("""
            SELECT booking_status
            FROM bookings
            WHERE booking_id = %s
              AND schedule_id = %s
              AND EXISTS (
                  SELECT 1
                  FROM booking_passengers
                  WHERE booking_id = %s
                    AND passenger_id = %s
              )
        """, (booking_id, schedule_id, booking_id, passenger_id))

        booking = cursor.fetchone()

        if booking is None:
            print("Invalid booking or passenger details.")
            return

        if booking[0] != "WAITLIST":
            print("Only WAITLIST bookings can be added here.")
            return

        # Check duplicate
        cursor.execute("""
            SELECT waitlist_id
            FROM waitlist
            WHERE booking_id = %s
              AND passenger_id = %s
        """, (booking_id, passenger_id))

        if cursor.fetchone():
            print("This passenger is already in the waitlist.")
            return

        # Calculate position
        cursor.execute("""
            SELECT COALESCE(MAX(waitlist_position), 0) + 1
            FROM waitlist
            WHERE schedule_id = %s
              AND waitlist_status = 'WAITING'
        """, (schedule_id,))

        position = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO waitlist
            (booking_id, passenger_id, schedule_id,
             waitlist_position, waitlist_status)
            VALUES (%s, %s, %s, %s, 'WAITING')
        """, (booking_id, passenger_id, schedule_id, position))

        connection.commit()

        print("Passenger added to waitlist successfully!")
        print("Waitlist Position:", position)

    except mysql.connector.Error as error:
        connection.rollback()
        print("Waitlist Error:", error)

    finally:
        cursor.close()
        connection.close()


def view_waitlist(schedule_id):
    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                w.waitlist_position,
                p.full_name,
                w.waitlist_status,
                w.created_at
            FROM waitlist w
            JOIN passengers p
                ON w.passenger_id = p.passenger_id
            WHERE w.schedule_id = %s
            ORDER BY w.waitlist_position ASC
        """, (schedule_id,))

        records = cursor.fetchall()

        print("\n========== WAITLIST ==========")

        if not records:
            print("No passengers in the waitlist.")
            return

        for record in records:
            print("--------------------------------")
            print("Position:", record[0])
            print("Passenger:", record[1])
            print("Status:", record[2])
            print("Added On:", record[3])

        print("==============================")

    except mysql.connector.Error as error:
        print("Waitlist Error:", error)

    finally:
        cursor.close()
        connection.close()



def promote_waitlisted_passenger(schedule_id):

    connection = create_connection()

    if connection is None:
        print("Database connection failed!")
        return

    cursor = connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        # Step 1: Find the first waiting passenger
        cursor.execute("""
            SELECT
                w.waitlist_id,
                w.booking_id,
                w.passenger_id,
                b.total_fare,
                b.booking_status,
                p.full_name,
                bp.booking_passenger_id
            FROM waitlist w
            JOIN bookings b
                ON w.booking_id = b.booking_id
            JOIN passengers p
                ON w.passenger_id = p.passenger_id
            JOIN booking_passengers bp
                ON bp.booking_id = w.booking_id
               AND bp.passenger_id = w.passenger_id
            WHERE w.schedule_id = %s
              AND w.waitlist_status = 'WAITING'
              AND b.booking_status = 'WAITLIST'
            ORDER BY w.waitlist_position ASC
            LIMIT 1
            FOR UPDATE
        """, (schedule_id,))

        passenger = cursor.fetchone()

        if passenger is None:
            print("No eligible passengers waiting.")
            connection.rollback()
            return

        # Step 2: Find an available CC seat
        cursor.execute("""
            SELECT seat_id, seat_number
            FROM seats
            WHERE schedule_id = %s
              AND seat_class = 'CC'
              AND seat_status = 'AVAILABLE'
            ORDER BY seat_number
            LIMIT 1
            FOR UPDATE
        """, (schedule_id,))

        seat = cursor.fetchone()

        if seat is None:
            print("No available CC seats.")
            connection.rollback()
            return

        # Step 3: Assign the seat
        cursor.execute("""
            UPDATE booking_passengers
            SET seat_id = %s
            WHERE booking_passenger_id = %s
              AND seat_id IS NULL
        """, (
            seat["seat_id"],
            passenger["booking_passenger_id"]
        ))

        if cursor.rowcount != 1:
            raise Exception("Passenger seat assignment failed!")

        # Step 4: Mark seat as booked
        cursor.execute("""
            UPDATE seats
            SET seat_status = 'BOOKED'
            WHERE seat_id = %s
              AND seat_status = 'AVAILABLE'
        """, (seat["seat_id"],))

        if cursor.rowcount != 1:
            raise Exception("Seat allocation failed!")

        # Step 5: Confirm the booking
        cursor.execute("""
            UPDATE bookings
            SET booking_status = 'CONFIRMED'
            WHERE booking_id = %s
              AND booking_status = 'WAITLIST'
        """, (passenger["booking_id"],))

        if cursor.rowcount != 1:
            raise Exception("Booking confirmation failed!")

        # Step 6: Update waitlist status
        cursor.execute("""
            UPDATE waitlist
            SET waitlist_status = 'PROMOTED'
            WHERE waitlist_id = %s
              AND waitlist_status = 'WAITING'
        """, (passenger["waitlist_id"],))

        if cursor.rowcount != 1:
            raise Exception("Waitlist update failed!")

        # Step 7: Commit everything
        connection.commit()

        print("\n========== WAITLIST PROMOTION SUCCESS ==========")
        print("Passenger:", passenger["full_name"])
        print("Booking ID:", passenger["booking_id"])
        print("Seat Number:", seat["seat_number"])
        print("Travel Class: CC")
        print("Fare: ₹", passenger["total_fare"])
        print("Booking Status: CONFIRMED")
        print("Waitlist Status: PROMOTED")
        print("================================================")

    except Exception as error:
        connection.rollback()
        print("Promotion Error:", error)
        print("All changes rolled back.")

    finally:
        cursor.close()
        connection.close()


def check_admin_access():

    if logged_in_user is None:
        print("Please login first!")
        return False

    if logged_in_user["user_role"] != "ADMIN":
        print("Access Denied! Admin privileges required.")
        return False

    return True


def admin_view_users():

    if not check_admin_access():
        return

    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT user_id, full_name, email, phone, user_role
            FROM users
            ORDER BY user_id
        """)

        users = cursor.fetchall()

        print("\n========== ALL REGISTERED USERS ==========")

        for user in users:
            print("------------------------------------------")
            print("User ID:", user[0])
            print("Name:", user[1])
            print("Email:", user[2])
            print("Phone:", user[3])
            print("Role:", user[4])

        print("==========================================")

    except mysql.connector.Error as error:
        print("Admin Error:", error)

    finally:
        cursor.close()
        connection.close()


def admin_view_bookings():
    if not check_admin_access():
        return

    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                b.booking_id,
                b.pnr_number AS pnr,
                u.full_name AS user_name,
                t.train_name,
                b.booking_status,
                b.total_fare
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN schedules s ON b.schedule_id = s.schedule_id
            JOIN trains t ON s.train_id = t.train_id
            ORDER BY b.booking_id DESC
        """

        cursor.execute(query)
        bookings = cursor.fetchall()

        if not bookings:
            print("\nNo bookings found.")
            return

        print("\n========== ALL BOOKINGS ==========")

        for booking in bookings:
            print("----------------------------------")
            print("Booking ID :", booking["booking_id"])
            print("PNR        :", booking["pnr"])
            print("Customer   :", booking["user_name"])
            print("Train      :", booking["train_name"])
            print("Status     :", booking["booking_status"])
            print("Fare       :", booking["total_fare"])

    except mysql.connector.Error as error:
        print("Error fetching bookings:", error)

    finally:
        cursor.close()
        connection.close()


def admin_view_payments():
    if not check_admin_access():
        return

    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                p.payment_id,
                p.booking_id,
                b.pnr_number AS pnr,
                p.transaction_id,
                p.payment_method,
                p.payment_amount,
                p.payment_status,
                p.payment_date
            FROM payments p
            JOIN bookings b ON p.booking_id = b.booking_id
            ORDER BY p.payment_id DESC
        """

        cursor.execute(query)
        payments = cursor.fetchall()

        if not payments:
            print("\nNo payment records found.")
            return

        print("\n========== ALL PAYMENTS ==========")

        for payment in payments:
            print("----------------------------------")
            print("Payment ID     :", payment["payment_id"])
            print("Booking ID     :", payment["booking_id"])
            print("PNR            :", payment["pnr"])
            print("Transaction ID :", payment["transaction_id"])
            print("Method         :", payment["payment_method"])
            print("Amount         :", payment["payment_amount"])
            print("Status         :", payment["payment_status"])
            print("Payment Date   :", payment["payment_date"])

    except mysql.connector.Error as error:
        print("Error fetching payments:", error)

    finally:
        cursor.close()
        connection.close()


def admin_view_cancellations():
    if not check_admin_access():
        return

    connection = create_connection()

    if connection is None:
        return

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                c.cancellation_id,
                c.booking_id,
                b.pnr_number AS pnr,
                u.full_name AS customer_name,
                c.cancellation_reason,
                c.refund_amount,
                c.cancellation_status,
                c.cancellation_date
            FROM cancellations c
            JOIN bookings b ON c.booking_id = b.booking_id
            JOIN users u ON b.user_id = u.user_id
            ORDER BY c.cancellation_id DESC
        """

        cursor.execute(query)
        cancellations = cursor.fetchall()

        if not cancellations:
            print("\nNo cancellation records found.")
            return

        print("\n========== ALL CANCELLATIONS ==========")

        for item in cancellations:
            print("----------------------------------")
            print("Cancellation ID :", item["cancellation_id"])
            print("Booking ID      :", item["booking_id"])
            print("PNR             :", item["pnr"])
            print("Customer        :", item["customer_name"])
            print("Reason          :", item["cancellation_reason"])
            print("Refund Amount   :", item["refund_amount"])
            print("Status          :", item["cancellation_status"])
            print("Cancellation Date:", item["cancellation_date"])

    except mysql.connector.Error as error:
        print("Error fetching cancellations:", error)

    finally:
        cursor.close()
        connection.close()


# Main Menu
def main():
    global logged_in_user

    while True:

        print("\n===== TRAIN RESERVATION SYSTEM =====")
        print("1. Register User")
        print("2. Login User")
        print("3. Search Trains")
        print("4. Check Seat Availability")
        print("5. Register Passenger")
        print("6. View Registered Passengers")
        print("7. Select Seat")
        print("8. Calculate Ticket Fare")
        print("9. Logout")
        print("10. Select Passenger for Booking")
        print("11. Select Train for Booking")
        print("12. Select Travel Class")
        print("13. Select Seat for Booking")
        print("14. Calculate Booking Fare")
        print("15. Book Train Ticket")
        print("16. Process Payment")
        print("17. Generate Train Ticket")
        print("18. View Booking History")
        print("19. Check PNR Status")
        print("20. Cancel Train Ticket")
        print("21. Add Passenger to Waitlist")
        print("22. View Waitlist")
        print("23. Promote Waitlisted Passenger")
        print("24. Admin - View All Users")
        print("25. Admin - View All Bookings")
        print("26. Admin - View All Payments")
        print("27. Admin - View All Cancellations")
        print("28. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            register_user()

        elif choice == "2":
            login_user()

        elif choice == "3":
            search_trains()

        elif choice == "4":
            check_seat_availability()

        elif choice == "5":
            register_passenger()
            
        elif choice == "6":
            view_passengers()
            
        elif choice == "7":
            select_seat()
            
        elif choice == "8":
            calculate_fare()
            
        elif choice == "9":
            if logged_in_user is not None:
                logged_in_user = None
                print("Logged out successfully!")
            else:
                print("You are not logged in!")
                
        elif choice == "10":
            select_passenger_for_booking()
            
        elif choice == "11":
            select_train_for_booking()
            
        elif choice == "12":
            schedule_id = int(input("Enter Schedule ID: "))

            selected_class = select_class_for_booking(schedule_id)

            if selected_class:
                print("Selected Class:", selected_class)
                
        elif choice == "13":
            schedule_id = int(input("Enter Schedule ID: "))
            seat_class = input("Enter Seat Class: ").strip().upper()

            selected_seat_id = select_seat_for_booking(
            schedule_id, seat_class
            )

            if selected_seat_id:
                print("Selected Seat ID:", selected_seat_id)

        elif choice == "14":
            seat_class = input("Enter seat class: ").strip().upper()
            number_of_passengers = int(
            input("Enter number of passengers: ")
            )

            total_fare = calculate_booking_fare(
            seat_class, number_of_passengers
            )

            if total_fare is not None:
                print("Final Fare: ₹", total_fare)
        
        
        elif choice == "15":
            book_ticket()
            
        elif choice == "16":
            process_payment()
            
        elif choice == "17":
            generate_ticket()
            
        elif choice == "18":
            view_booking_history()

        elif choice == "19":
            check_pnr_status()
            
        elif choice == "20":
            cancel_ticket()
            
        elif choice == "21":
            booking_id = int(input("Enter Booking ID: "))
            passenger_id = int(input("Enter Passenger ID: "))
            schedule_id = int(input("Enter Schedule ID: "))
            add_to_waitlist(booking_id, passenger_id, schedule_id)

        elif choice == "22":
            schedule_id = int(input("Enter Schedule ID: "))
            view_waitlist(schedule_id)

        elif choice == "23":
            schedule_id = int(input("Enter Schedule ID: "))
            promote_waitlisted_passenger(schedule_id)
            
        elif choice == "24":
            admin_view_users()
            
        elif choice == "25":
            admin_view_bookings()
        
        elif choice == "26":
            admin_view_payments()
            
        elif choice == "27":
            admin_view_cancellations()
        
        elif choice == "28":
            print("Thank you for using Train Reservation System!")
            break
        

        else:
            print("Invalid choice! Please try again.")



if __name__ == "__main__":
    main()
    
    
    

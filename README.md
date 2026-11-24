# 🚆 Train Reservation System

A console-based Train Reservation System developed using Python and MySQL. This application allows users to register, search trains, reserve seats, book tickets, process payments, manage cancellations, and handle waitlisted passengers.

## 📌 Project Overview

The Train Reservation System is designed to simplify railway ticket booking operations through a menu-driven Python application integrated with a MySQL database.

It supports customer and administrator operations with database-backed booking management.

## ✨ Features

### 👤 User Management

- User Registration
- User Login
- Password Hashing
- User Authentication

### 🚉 Train Management

- Search Available Trains
- Check Seat Availability
- Select Train
- Select Travel Class

### 🎫 Ticket Booking

- Passenger Registration
- Seat Selection
- Automatic Fare Calculation
- Ticket Booking
- PNR Generation
- E-Ticket Generation

### 💳 Payment Management

- Payment Processing Simulation
- Payment Status Tracking
- Transaction ID Generation

### ❌ Cancellation Management

- Ticket Cancellation
- Refund Calculation
- Seat Availability Update
- Cancellation History

### ⏳ Waitlist Management

- Add Passengers to Waitlist
- View Waitlist
- Promote Waitlisted Passengers

### 🔐 Admin Features

- View All Users
- View All Bookings
- View All Payments
- View All Cancellations

## 🛠️ Technologies Used

- Python
- MySQL
- MySQL Connector
- python-dotenv
- SQL
- Git
- GitHub

## 📂 Project Structure

```text
Train_Reservation_System/
│
├── main.py
├── database.py
├── database.sql
├── requirements.txt
├── .env
├── .gitignore
└── README.md

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vikas160405/Train_Reservation_System.git
```

### 2. Navigate to the Project Folder

```bash
cd Train_Reservation_System
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure MySQL Database

Create a MySQL database:

```sql
CREATE DATABASE train_reservation_system;
```

Create a `.env` file in the project directory:

```env
DB_HOST=127.0.0.1
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=train_reservation_system
```

Replace the values with your own MySQL credentials.

**Note:** The required database tables and initial data must also be created before running the application.

### 7. Run the Application

```bash
python main.py
```

## 🗄️ Database

The application uses MySQL to store and manage:

- User Details
- Passenger Details
- Train Details
- Station Details
- Train Schedules
- Seat Details
- Booking Records
- Payment Records
- Cancellation Records
- Waitlist Records
- Ticket Details

## 👨‍💻 Developer

**Vikas Relangi**

GitHub: [vikas160405](https://github.com/vikas160405)

## 📌 Project Status

Developed as a Python and MySQL database management project.

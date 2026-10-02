# 🚗 Smart Parking System

### Full-Stack Parking Management Platform with React, FastAPI, C++, SQLite & Docker

A modern full-stack parking management system designed to automate vehicle entry, parking-slot allocation, EV parking management, checkout, billing, transaction tracking, and parking analytics through a web-based dashboard.

This project evolves a traditional C++ console-based parking application into a complete software system with a **React frontend, FastAPI backend, SQLite database, C++ fee-calculation engine, JWT authentication, automated testing, and Docker-based deployment**.

---

## 📌 Why This Project?

Traditional parking applications often rely on manual tracking or basic console interfaces.

This project demonstrates how a parking system can be transformed into a maintainable full-stack application with:

- 🌐 Web-based dashboard
- 🔐 Authentication and protected APIs
- 🚘 Automated vehicle management
- 🅿️ Intelligent parking-slot allocation
- ⚡ Dedicated EV parking
- 💳 Automatic billing
- 📊 Parking and revenue analytics
- 🗄️ Persistent database storage
- 🔗 C++ and Python integration
- 🧪 Automated testing
- 🐳 Dockerized deployment

The goal is not just to build a UI, but to demonstrate **backend engineering, database design, API development, native-code integration, testing, and deployment practices in one project**.

---

# ✨ Key Features

## 🔐 Authentication & Security

- JWT-based authentication
- Protected API endpoints
- Secure password hashing using PBKDF2-HMAC-SHA256
- Configurable administrator credentials
- Environment-variable based secrets
- Request validation using Pydantic
- Parameterized SQL queries

---

## 🚘 Vehicle Management

The system supports:

- Vehicle registration
- License plate validation and normalization
- Regular cars
- Electric vehicles
- Duplicate active-vehicle prevention
- Vehicle search
- Vehicle history

Example:

```text
Vehicle
├── License Plate
├── Vehicle Type
└── Parking Status

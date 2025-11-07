# Django E-Commerce Project Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Project Setup](#project-setup)
4. [Database Configuration](#database-configuration)
5. [Running the Application](#running-the-application)
6. [Access Credentials](#access-credentials)
7. [Project Structure](#project-structure)
8. [Key Features](#key-features)
9. [Development Commands](#development-commands)
10. [Recent Enhancements](#recent-enhancements)

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment tool (venv)

## Installation

### 1. Create a Virtual Environment
```bash
python -m venv .venv
```
This command creates a new virtual environment named `.venv` in the current directory. A virtual environment isolates the project dependencies from other Python projects.

### 2. Activate the Virtual Environment
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```
This activates the virtual environment, ensuring that any packages installed will be contained within this environment rather than the global Python installation.

### 3. Install Django and Required Packages
```bash
pip install django
```
Installs the Django web framework, which is the foundation of this project.

```bash
pip install pillow
```
Installs Pillow, a Python imaging library required for handling image uploads in the project.

```bash
pip install crispy-bootstrap5
```
Installs crispy-bootstrap5, which provides Bootstrap 5 styling for Django forms.

```bash
pip install reportlab
```
Installs ReportLab, a Python library for generating PDF documents used for invoice generation.

## Project Setup

### 1. Create Django Project
```bash
django-admin startproject ecommerce .
```
Creates a new Django project named `ecommerce` in the current directory. The `.` at the end ensures the project is created in the current directory rather than a subdirectory.

### 2. Create Django Apps
```bash
python manage.py startapp accounts
```
Creates a new Django app named `accounts` for handling user authentication and profile management.

```bash
python manage.py startapp shop
```
Creates a new Django app named `shop` for handling product catalog and main shop functionality.

```bash
python manage.py startapp cart
```
Creates a new Django app named `cart` for handling shopping cart functionality.

```bash
python manage.py startapp orders
```
Creates a new Django app named `orders` for handling order processing and management.

```bash
python manage.py startapp dashboard
```
Creates a new Django app named `dashboard` for handling the manager dashboard and admin interface.

```bash
python manage.py startapp security_scanner
```
Creates a new Django app named `security_scanner` for handling security assessment and scanning functionality.

### 3. Install the Project
```bash
pip install -r requirements.txt
```
Installs all the Python package dependencies listed in the `requirements.txt` file, ensuring all required packages are available.

## Database Configuration

### 1. Run Migrations
```bash
python manage.py makemigrations
```
Creates new migration files based on changes to the Django models. These files contain the SQL commands needed to update the database schema.

```bash
python manage.py migrate
```
Applies the migration files to the database, creating or updating the database tables to match the current Django models.

### 2. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Creates a superuser account with administrative privileges that can access the Django admin panel.

### 3. Create Manager User
The manager user is automatically created when the application starts.

## Running the Application

### Start the Development Server
```bash
python manage.py runserver
```
Starts the Django development server, which allows you to view and test the application in a web browser. By default, it runs on http://127.0.0.1:8000/

### Access URLs

#### User Access Points:
- **Home Page**: http://127.0.0.1:8000/
- **User Registration**: http://127.0.0.1:8000/accounts/register/
- **User Login**: http://127.0.0.1:8000/accounts/login/
- **User Profile**: http://127.0.0.1:8000/accounts/profile/edit
- **Shopping Cart**: http://127.0.0.1:8000/cart/
- **User Orders**: http://127.0.0.1:8000/orders/
- **Address Management**: http://127.0.0.1:8000/accounts/addresses/
- **FAQ Page**: http://127.0.0.1:8000/faq/
- **Return Policy**: http://127.0.0.1:8000/return-policy/
- **Privacy Policy**: http://127.0.0.1:8000/privacy-policy/
- **Terms of Service**: http://127.0.0.1:8000/terms-of-service/
- **Security Scanner**: http://127.0.0.1:8000/security/

#### Admin Access Points:
- **Django Admin Panel**: http://127.0.0.1:8000/admin/
- **Manager Login**: http://127.0.0.1:8000/accounts/login/manager/
- **Manager Dashboard**: http://127.0.0.1:8000/dashboard/
- **Security Assessment**: http://127.0.0.1:8000/security/

## Access Credentials

### Manager Credentials:
- **Email**: manager@example.com
- **Password**: Inamsyed@123

### Django Admin Credentials:
- **Email**: admin@example.com
- **Password**: adminpass123

## Project Structure

```
ecommerce/
├── accounts/           # User authentication and profile management
├── cart/               # Shopping cart functionality
├── dashboard/          # Manager dashboard and admin interface
├── orders/             # Order processing and management
├── security_scanner/   # Security assessment and scanning tool
├── shop/               # Product catalog and main shop functionality
├── online_shop/        # Main Django project settings
├── static/             # CSS, JavaScript, and other static files
├── media/              # Uploaded images and media files
├── requirements.txt    # Python package dependencies
└── manage.py           # Django management script
```

## Key Features

### For Users:
- User registration and authentication
- Product browsing and search
- Shopping cart management
- Order placement and history
- Profile management with email verification
- Password reset functionality
- Address management system
- Order tracking with visual progress bar
- Favorite products management
- Access to static information pages (FAQ, Return Policy, etc.)
- Security assessment tools

### For Managers:
- Dashboard with statistics
- Product management (add, edit, delete)
- Category management
- Order management with status updates
- User management capabilities
- Custom dashboard interface
- Security monitoring and assessment

## Development Commands

### Collect Static Files
```bash
python manage.py collectstatic
```
Collects all static files (CSS, JavaScript, images) from all apps into a single directory for production deployment.

### Create New Migrations
```bash
python manage.py makemigrations
```
Generates new migration files when Django models have been modified, preparing the database schema changes.

### Apply Migrations
```bash
python manage.py migrate
```
Applies migration files to the database, implementing any pending schema changes.

### Create Superuser
```bash
python manage.py createsuperuser
```
Creates a new superuser account that can access the Django admin interface with full administrative privileges.

### Run Tests
```bash
python manage.py test
```
Runs all automated tests in the project to ensure the application is working correctly.

## Recent Enhancements

### Address Management System
Users can now add, edit, and manage multiple addresses with the ability to set a default address. Addresses can be named (Home, Office, etc.) similar to Amazon's format.

### Enhanced Order Tracking
Visual progress bar showing order status stages (Pending, Processing, Shipped, Delivered) with current status highlighted.

### Improved Invoice System
Professional invoice generation with detailed formatting and PDF export capabilities. Payment method storage with proper COD handling.

### Email Verification
Email verification flow for profile updates to enhance account security.

### Modern UI/UX
Updated styling with consistent form controls, password visibility toggles, and improved navigation.

### Security Scanner
Integrated security assessment tool to evaluate application security measures with professional loading screens and detailed reporting.

### Enhanced Loading Experience
Professional loading screens with progress indicators for asynchronous operations, providing better user feedback during long-running processes.
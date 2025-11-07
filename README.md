# ShopEase: Modern E-Commerce Platform with Django

## Table of Contents
1. [App Preview](#app-preview)
2. [Features](#features)
   - [Available to the Users](#available-to-the-users)
   - [Available to the Managers](#available-to-the-managers)
3. [Manager Dashboard Access](#manager-dashboard-access)
4. [Technologies Used](#technologies-used)
5. [How to Run the Application](#how-to-run-the-application)
6. [Key Enhancements](#key-enhancements)
7. [Documentation](#documentation)
8. [How to Contribute](#how-to-contribute)
9. [License](#license)

![ShopEase E-Commerce Platform]

This project is a modern, feature-rich e-commerce platform built with Django. The application provides a custom dashboard for managers to manage products and orders, while offering users a seamless shopping experience with advanced features.

## App Preview

### Features

There are two types of users in this app: regular users and managers.

#### Available to the Users:

- **User Authentication**: Secure registration, login, and password reset functionality
- **Product Catalog**: Browse products with categories, search functionality, and detailed product pages
- **Shopping Cart**: Add, remove, and manage items in the shopping cart
- **Address Management**: Add and manage multiple delivery addresses with naming (Home, Office, etc.)
- **Order Processing**: Place orders with order tracking and visual progress bar
- **Order History**: View past orders with detailed information
- **Invoice Generation**: Download professional PDF invoices for orders
- **Profile Management**: Update personal information with email verification for security
- **Password Management**: Secure password change functionality
- **Favorites**: Save favorite products for quick access
- **Static Information Pages**: Access FAQ, Return Policy, Privacy Policy, and Terms of Service
- **Security Scanner**: Run comprehensive security assessments of the application

#### Available to the Managers:

Managers can access all the features available to regular users, along with additional capabilities, through the custom dashboard accessible at [http://127.0.0.1:8000/accounts/login/manager](http://127.0.0.1:8000/accounts/login/manager).

- **Dashboard Overview**: Statistics and quick access to key functions
- **Product Management**: Add, edit, and delete products
- **Category Management**: Create and manage product categories
- **Order Management**: View and manage all orders with status updates
- **User Management**: Access to user information and management capabilities
- **Security Assessment**: Monitor application security through integrated scanning tools

### Manager Dashboard Access

To access the custom dashboard for managers, please use the following credentials:

- Email: manager@example.com
- Password: managerpass1234

### Technologies Used

- Python 3
- Django
- Bootstrap 5
- SQLite3 database
- ReportLab (for PDF generation)
- Crispy Forms (for form styling)
- JavaScript (for interactive features)

### How to Run the Application

1. Clone or download the project to your local machine.
2. Change directory to the project folder.
3. Ensure that you have Python 3, pip, and virtualenv installed on your machine.
4. Create a virtual environment using the following command:
   - For Mac and Linux: `python3 -m venv .venv`
   - For Windows: `python3 -m venv .venv`
5. Activate the virtual environment:
   - For Mac and Linux: `source .venv/bin/activate`
   - For Windows: `.venv\scripts\activate`
6. Install the application requirements by running: `pip3 install -r requirements.txt`
7. Migrate the database by executing: `python3 manage.py migrate`
8. Start the server: `python3 manage.py runserver`
9. You should now be able to access the application by visiting: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Key Enhancements

1. **Address Management System**: Users can add multiple addresses with custom names (Home, Office, etc.) and select from saved addresses during checkout.
2. **Order Tracking**: Visual progress bar showing order status stages (Pending, Processing, Shipped, Delivered).
3. **Professional Invoice System**: Detailed invoice generation with PDF export capabilities.
4. **Email Verification**: Enhanced security with email verification for profile updates.
5. **Modern UI/UX**: Improved styling with consistent form controls, password visibility toggles, and responsive design.
6. **Static Information Pages**: Comprehensive FAQ, Return Policy, Privacy Policy, and Terms of Service pages.
7. **Security Scanner**: Integrated security assessment tool to evaluate application security measures.
8. **Enhanced Loading Experience**: Professional loading screens with progress indicators for asynchronous operations.

### Documentation

For detailed information about the project, please refer to the following documentation files:

- [Project Structure](PROJECT_STRUCTURE.md): Detailed explanation of the directory structure and file purposes
- [Django Setup Guide](DJANGO_SETUP_GUIDE.md): Comprehensive guide for setting up the Django development environment
- [Cybersecurity Measures](CYBERSECURITY_MEASURES.md): Documentation of implemented cybersecurity measures

### How to Contribute

I welcome contributions to enhance and customize this project. If you would like to contribute, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch with a descriptive name for your feature or bug fix.
3. Make the necessary changes in your branch.
4. Test your changes thoroughly.
5. Commit your changes and push them to your forked repository.
6. Submit a pull request, clearly describing the changes you have made.

### License

Released under the [MIT License](LICENSE). Feel free to use, modify, and distribute it as per the terms of the license.

Feel free to explore, contribute, and customize this according to your needs!
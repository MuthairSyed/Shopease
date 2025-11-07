# Project Structure Documentation

## Table of Contents
1. [Root Directory](#root-directory)
2. [Detailed Directory Breakdown](#detailed-directory-breakdown)
   - [accounts/ - User Authentication and Management](#1-accounts---user-authentication-and-management)
   - [cart/ - Shopping Cart Functionality](#2-cart---shopping-cart-functionality)
   - [dashboard/ - Manager Dashboard](#3-dashboard---manager-dashboard)
   - [online_shop/ - Main Project Configuration](#4-online_shop---main-project-configuration)
   - [orders/ - Order Processing](#5-orders---order-processing)
   - [security_scanner/ - Security Assessment Tool](#6-security_scanner---security-assessment-tool)
   - [shop/ - Product Catalog](#7-shop---product-catalog)
   - [static/ - Static Files](#8-static---static-files)
   - [staticfiles/ - Collected Static Files](#9-staticfiles---collected-static-files)
   - [templates/ - Global Templates](#10-templates---global-templates)
3. [Root Files](#root-files)
4. [Why This Structure?](#why-this-structure)
5. [Recent Additions](#recent-additions)

This document explains the directory structure and the purpose of each file in the ShopEase Django ecommerce application.

## Root Directory

```
ecommerce/
├── accounts/              # User authentication and management
├── cart/                  # Shopping cart functionality
├── dashboard/             # Manager dashboard and admin interface
├── online_shop/           # Main Django project configuration
├── orders/                # Order processing and management
├── security_scanner/      # Security assessment and scanning tool
├── shop/                  # Product catalog and main shop functionality
├── static/                # Static files (CSS, JavaScript, images)
├── staticfiles/           # Collected static files for production
├── templates/             # Global templates and admin overrides
├── manage.py              # Django command-line utility
├── requirements.txt       # Python package dependencies
├── README.md              # Project overview and setup instructions
├── DJANGO_SETUP_GUIDE.md  # Detailed Django setup guide
├── CYBERSECURITY_MEASURES.md # Security implementation documentation
└── db.sqlite3             # SQLite database file
```

## Detailed Directory Breakdown

### 1. `accounts/` - User Authentication and Management

This directory handles all user-related functionality including registration, login, profile management, and password reset.

```
accounts/
├── migrations/                 # Database migration files for user model changes
│   ├── 0001_initial.py         # Initial migration creating the User model
│   ├── 0002_user_cart.py       # Added cart field to User model
│   ├── 0003_remove_user_cart.py # Removed cart field from User model
│   └── 0004_user_likes.py      # Added likes field for product favorites
├── templates/                  # User authentication templates
│   ├── addresses.html          # User address management page
│   ├── add_address.html        # Form to add new address
│   ├── edit_address.html       # Form to edit existing address
│   ├── edit_profile.html       # User profile editing page
│   ├── email_template.html     # Plain text password reset email template
│   ├── email_template_html.html # HTML password reset email template
│   ├── email_verification.html # HTML email verification template
│   ├── email_verification.txt  # Plain text email verification template
│   ├── login.html              # User login page
│   ├── manager_login.html      # Manager login page
│   ├── password_reset.html     # Password reset request form
│   ├── password_reset_complete.html # Password reset completion page
│   ├── password_reset_confirm.html # Password reset confirmation form
│   ├── password_reset_done.html # Password reset request confirmation
│   ├── password_reset_subject.txt # Password reset email subject line
│   └── register.html           # User registration page
├── admin.py                    # Django admin configuration for User model
├── apps.py                     # Django app configuration
├── forms.py                    # Form definitions for user authentication
├── managers.py                 # Custom user manager for User model
├── models.py                   # User model definition and Address model
├── tests.py                    # Unit tests for accounts functionality
├── urls.py                     # URL routing for authentication views
└── views.py                    # View functions for user authentication
```

### 2. `cart/` - Shopping Cart Functionality

This directory manages the shopping cart system, allowing users to add, remove, and update items.

```
cart/
├── utils/                      # Utility functions for cart operations
│   └── cart.py                 # Core cart logic and session management
├── templates/                  # Cart display template
│   └── cart.html               # Shopping cart page
├── admin.py                    # Django admin configuration
├── apps.py                     # Django app configuration
├── forms.py                    # Form definitions for cart operations
├── models.py                   # Cart-related model definitions
├── tests.py                    # Unit tests for cart functionality
├── urls.py                     # URL routing for cart views
└── views.py                    # View functions for cart operations
```

### 3. `dashboard/` - Manager Dashboard

This directory provides the administrative interface for managers to manage products, categories, and orders.

```
dashboard/
├── templates/                  # Dashboard templates
│   ├── dashboard/              # Dashboard base templates
│   │   ├── base.html           # Base template for dashboard pages
│   │   └── edit_profile.html   # Manager profile editing page
│   ├── add_category.html       # Form to add new product categories
│   ├── add_product.html        # Form to add new products
│   ├── dashboard.html          # Main dashboard overview page
│   ├── edit_product.html       # Form to edit existing products
│   ├── order_detail.html       # Detailed view of individual orders
│   ├── orders.html             # List of all orders
│   └── products.html           # List of all products
├── admin.py                    # Django admin configuration
├── apps.py                     # Django app configuration
├── forms.py                    # Form definitions for dashboard operations
├── models.py                   # Dashboard-related model definitions
├── tests.py                    # Unit tests for dashboard functionality
├── urls.py                     # URL routing for dashboard views
└── views.py                    # View functions for dashboard operations
```

### 4. `online_shop/` - Main Project Configuration

This directory contains the main Django project settings and configuration files.

```
online_shop/
├── asgi.py                     # ASGI configuration for asynchronous support
├── context_processors.py       # Context processors for global template variables
├── settings.py                 # Main Django settings and configuration
├── urls.py                     # Main URL routing configuration
└── wsgi.py                     # WSGI configuration for web server deployment
```

### 5. `orders/` - Order Processing

This directory handles order creation, processing, payment, and order history.

```
orders/
├── migrations/                 # Database migration files for order models
│   ├── 0001_initial.py         # Initial migration creating Order and OrderItem models
│   ├── 0002_alter_order_status.py # Modified order status choices
│   └── 0003_order_payment_method.py # Added payment method field to Order model
├── templates/                  # Order-related templates
│   ├── checkout.html           # Checkout page
│   ├── invoice_pdf.html        # PDF invoice template
│   ├── invoice_modern.html     # Modern HTML invoice template
│   ├── order_confirmation_email.html # Order confirmation email template
│   ├── order_tracking.html     # Order tracking with visual progress bar
│   ├── payment.html            # Payment processing page
│   ├── payment_success.html    # Payment success confirmation page
│   └── user_orders.html        # User's order history page
├── templatetags/               # Custom template tags
│   ├── math_extras.py          # Mathematical template filters
│   └── __init__.py             # Package initialization
├── admin.py                    # Django admin configuration for orders
├── apps.py                     # Django app configuration
├── models.py                   # Order and OrderItem model definitions
├── tests.py                    # Unit tests for order functionality
├── urls.py                     # URL routing for order views
└── views.py                    # View functions for order processing
```

### 6. `security_scanner/` - Security Assessment Tool

This directory provides an integrated security assessment tool for evaluating the application's security measures.

```
security_scanner/
├── templates/                  # Security scanner templates
│   └── security_scanner/       # Security scanner base templates
│       ├── base.html           # Base template for security scanner pages
│       ├── dashboard.html      # Main security scanner dashboard
│       ├── vulnerability_report.html # Security measures report
│       └── test_cases.html     # Detailed test cases report
├── admin.py                    # Django admin configuration
├── apps.py                     # Django app configuration
├── models.py                   # Security scanner model definitions
├── tests.py                    # Unit tests for security scanner functionality
├── urls.py                     # URL routing for security scanner views
└── views.py                    # View functions for security assessment
```

### 7. `shop/` - Product Catalog

This directory manages the product catalog, home page, and product browsing functionality.

```
shop/
├── migrations/                 # Database migration files for shop models
│   ├── 0001_initial.py         # Initial migration creating Category and Product models
│   ├── 0002_alter_product_slug.py # Modified product slug field
│   ├── 0003_alter_product_options_remove_product_category_and_more.py # Restructured product model
│   ├── 0004_alter_product_slug_alter_product_title.py # Modified product fields
│   ├── 0005_alter_product_slug.py # Further product slug modifications
│   ├── 0006_alter_category_options_alter_product_options_and_more.py # Model options changes
│   ├── 0007_alter_category_options.py # Category options adjustments
│   └── 0008_alter_product_slug.py # Final product slug modifications
├── templates/                  # Shop templates
│   ├── about.html              # About page
│   ├── base.html               # Base template for shop pages
│   ├── contact.html            # Contact page
│   ├── faq.html                # Frequently Asked Questions page
│   ├── favorites.html          # User's favorite products page
│   ├── home_page.html          # Main home page
│   ├── privacy_policy.html     # Privacy Policy page
│   ├── product_detail.html     # Individual product detail page
│   ├── return_policy.html      # Return Policy page
│   └── terms_of_service.html   # Terms of Service page
├── admin.py                    # Django admin configuration for products
├── apps.py                     # Django app configuration
├── forms.py                    # Form definitions for shop operations
├── models.py                   # Category and Product model definitions
├── tests.py                    # Unit tests for shop functionality
├── urls.py                     # URL routing for shop views
└── views.py                    # View functions for shop operations
```

### 8. `static/` - Static Files

This directory contains static assets like CSS, JavaScript, and images.

```
static/
├── css/                        # CSS stylesheets
│   └── style.css               # Main stylesheet for the application
├── js/                         # JavaScript files (currently empty)
└── media/                      # Media files including images and logos
    └── shopping_bags.png       # Application logo image
```

### 9. `staticfiles/` - Collected Static Files

This directory is created by Django's `collectstatic` command and contains all static files for production deployment.

```
staticfiles/
├── admin/                      # Django admin static files
└── css/                        # Copied CSS files
```

### 10. `templates/` - Global Templates

This directory contains global templates and Django admin overrides.

```
templates/
└── admin/                      # Django admin template overrides
    ├── base.html               # Custom admin base template
    └── orders/                 # Order-specific admin templates
        └── order/              # Order model admin templates
            └── change_form.html # Custom order change form template
```

## Root Files

### `manage.py`
Django's command-line utility for administrative tasks. Used to run the development server, create migrations, and perform other management operations.

### `requirements.txt`
Lists all Python package dependencies required for the project, including Django, Pillow for image handling, and crispy forms for better form rendering.

### `README.md`
Project overview and basic setup instructions for new developers.

### `DJANGO_SETUP_GUIDE.md`
Detailed guide for setting up the Django development environment.

### `CYBERSECURITY_MEASURES.md`
Documentation of implemented cybersecurity measures (created separately).

### `db.sqlite3`
SQLite database file containing all application data in development.

## Why This Structure?

This directory structure follows Django's best practices and provides several benefits:

1. **Separation of Concerns**: Each directory handles a specific aspect of the application, making it easier to maintain and understand.

2. **Scalability**: The modular structure allows for easy addition of new features without disrupting existing functionality.

3. **Reusability**: Each app (accounts, cart, dashboard, orders, shop) can potentially be reused in other projects.

4. **Maintainability**: Related files are grouped together, making it easier to locate and modify specific functionality.

5. **Django Conventions**: Follows Django's recommended project structure, making it familiar to other Django developers.

6. **Security**: Sensitive files like [settings.py](file:///Users/msyed1/Downloads/ecommerce/online_shop/settings.py) are properly isolated in the main project directory.

This structure allows developers to quickly understand where to find specific functionality and makes the project easier to maintain and extend over time.

## Recent Additions

### Address Management System
- Added [Address](file:///Users/msyed1/Downloads/ecommerce/accounts/models.py#L37-L66) model for storing user addresses
- Created address management views and templates
- Integrated address selection into checkout process

### Enhanced Order Tracking
- Added visual progress bar for order tracking
- Created order tracking template with status visualization

### Improved Invoice System
- Enhanced invoice templates with better formatting
- Added modern invoice PDF generation
- Integrated payment method storage in order model

### Email Verification
- Added email verification flow for profile updates
- Created email verification templates

### Static Pages
- Added FAQ, Return Policy, Privacy Policy, and Terms of Service pages
- Integrated these pages into navigation and footer

### Security Scanner
- Added integrated security assessment tool
- Created security scanner views, templates, and URL routing
- Implemented comprehensive security testing functionality

This updated structure reflects the enhanced functionality and security features added to the application.
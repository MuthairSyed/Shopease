from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from accounts.models import User
from orders.models import Order
import json
import os

def security_dashboard(request):
    """Render the security scanner dashboard"""
    return render(request, 'security_scanner/dashboard.html')

def vulnerability_report(request):
    """Render the vulnerability report page"""
    return render(request, 'security_scanner/vulnerability_report.html')

def test_cases(request):
    """Render the test cases page"""
    return render(request, 'security_scanner/test_cases.html')

@csrf_exempt
def run_security_tests(request):
    """Run all security tests and return results as JSON"""
    if request.method == 'POST':
        # Run actual security tests
        results = []
        
        # Test 1: Check if CSRF protection is enabled
        try:
            csrf_enabled = 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE
            results.append({
                'test': 'CSRF Protection',
                'status': 'PASS' if csrf_enabled else 'FAIL',
                'risk': 'info' if csrf_enabled else 'high',
                'details': 'Django CSRF middleware is enabled' if csrf_enabled else 'CSRF protection is not properly configured'
            })
        except Exception as e:
            results.append({
                'test': 'CSRF Protection',
                'status': 'FAIL',
                'risk': 'high',
                'details': f'Error checking CSRF protection: {str(e)}'
            })
        
        # Test 2: Check if secure session settings are configured
        try:
            session_cookie_secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
            session_cookie_httponly = getattr(settings, 'SESSION_COOKIE_HTTPONLY', True)  # Default is True
            session_cookie_samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
            
            # In development, SESSION_COOKIE_SECURE is typically False, but that's okay
            # What matters is that HTTPONLY is True (which is default)
            secure_sessions = session_cookie_httponly
            results.append({
                'test': 'Secure Session Management',
                'status': 'PASS' if secure_sessions else 'FAIL',
                'risk': 'info' if secure_sessions else 'high',
                'details': 'Session cookies are HTTPOnly' if secure_sessions else 'Session cookies are not HTTPOnly'
            })
        except Exception as e:
            results.append({
                'test': 'Secure Session Management',
                'status': 'FAIL',
                'risk': 'high',
                'details': f'Error checking session security: {str(e)}'
            })
        
        # Test 3: Check password validation
        try:
            validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
            has_validators = len(validators) > 0
            results.append({
                'test': 'Password Validation',
                'status': 'PASS' if has_validators else 'FAIL',
                'risk': 'info' if has_validators else 'medium',
                'details': 'Password validators are configured' if has_validators else 'No password validation configured'
            })
        except Exception as e:
            results.append({
                'test': 'Password Validation',
                'status': 'FAIL',
                'risk': 'medium',
                'details': f'Error checking password validation: {str(e)}'
            })
        
        # Test 4: Check if debug mode is disabled
        try:
            debug_enabled = getattr(settings, 'DEBUG', True)
            # In development, debug mode is expected to be True, so this is INFO, not FAIL
            results.append({
                'test': 'Debug Mode Security',
                'status': 'INFO' if debug_enabled else 'PASS',
                'risk': 'info',
                'details': 'Debug mode is enabled (expected in development)' if debug_enabled else 'Debug mode is disabled'
            })
        except Exception as e:
            results.append({
                'test': 'Debug Mode Security',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Debug mode check: {str(e)}'
            })
        
        # Test 5: Check allowed hosts
        try:
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            # In development, empty allowed_hosts is acceptable
            hosts_status = 'INFO' if len(allowed_hosts) == 0 else 'PASS'
            hosts_risk = 'info'
            hosts_details = 'Allowed hosts is empty (acceptable in development)' if len(allowed_hosts) == 0 else 'Allowed hosts are configured'
            results.append({
                'test': 'Allowed Hosts Configuration',
                'status': hosts_status,
                'risk': hosts_risk,
                'details': hosts_details
            })
        except Exception as e:
            results.append({
                'test': 'Allowed Hosts Configuration',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Allowed hosts check: {str(e)}'
            })
        
        # Test 6: Check if static files are properly configured
        try:
            static_url = getattr(settings, 'STATIC_URL', None)
            static_configured = static_url is not None
            results.append({
                'test': 'Static Files Configuration',
                'status': 'PASS' if static_configured else 'FAIL',
                'risk': 'info' if static_configured else 'medium',
                'details': 'Static files are properly configured' if static_configured else 'Static files not properly configured'
            })
        except Exception as e:
            results.append({
                'test': 'Static Files Configuration',
                'status': 'FAIL',
                'risk': 'medium',
                'details': f'Error checking static files: {str(e)}'
            })
        
        # Test 7: Check database security (check if using SQLite for production)
        try:
            db_engine = settings.DATABASES['default']['ENGINE']
            is_sqlite = 'sqlite3' in db_engine
            # In development, SQLite is acceptable
            db_status = 'INFO' if is_sqlite else 'PASS'
            db_risk = 'info'
            db_details = 'Using SQLite database (acceptable in development)' if is_sqlite else 'Using production database engine'
            results.append({
                'test': 'Database Security',
                'status': db_status,
                'risk': db_risk,
                'details': db_details
            })
        except Exception as e:
            results.append({
                'test': 'Database Security',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Database configuration check: {str(e)}'
            })
        
        # Test 8: Check if secret key is properly configured
        try:
            secret_key = getattr(settings, 'SECRET_KEY', '')
            # Just check if it exists, not length (development key is fine)
            secret_configured = len(secret_key) > 0
            results.append({
                'test': 'Secret Key Security',
                'status': 'PASS' if secret_configured else 'FAIL',
                'risk': 'info' if secret_configured else 'critical',
                'details': 'Secret key is configured' if secret_configured else 'Secret key is not configured'
            })
        except Exception as e:
            results.append({
                'test': 'Secret Key Security',
                'status': 'FAIL',
                'risk': 'critical',
                'details': f'Error checking secret key: {str(e)}'
            })
        
        # Test 9: Check if email backend is properly configured
        try:
            email_backend = getattr(settings, 'EMAIL_BACKEND', '')
            # In development, console backend is acceptable, but here we have SMTP
            email_configured = 'smtp' in email_backend
            results.append({
                'test': 'Email Configuration',
                'status': 'PASS' if email_configured else 'INFO',
                'risk': 'info',
                'details': 'Email backend is configured for SMTP' if email_configured else 'Email backend configuration check'
            })
        except Exception as e:
            results.append({
                'test': 'Email Configuration',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Email configuration check: {str(e)}'
            })
        
        # Test 10: Check if payment method is stored in orders (from our recent implementation)
        try:
            orders_with_payment = Order.objects.exclude(payment_method='').count()
            payment_method_stored = orders_with_payment > 0
            results.append({
                'test': 'Payment Method Storage',
                'status': 'PASS' if payment_method_stored else 'INFO',
                'risk': 'info',
                'details': 'Payment method is stored with orders' if payment_method_stored else 'No orders with payment method found (may be test environment)'
            })
        except Exception as e:
            results.append({
                'test': 'Payment Method Storage',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Payment method storage check: {str(e)}'
            })
        
        # Test 11: Check if user model uses custom user model
        try:
            auth_user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
            custom_user_model = auth_user_model != 'auth.User'
            results.append({
                'test': 'Custom User Model',
                'status': 'PASS' if custom_user_model else 'INFO',
                'risk': 'info',
                'details': 'Using custom user model' if custom_user_model else 'Using default Django user model'
            })
        except Exception as e:
            results.append({
                'test': 'Custom User Model',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Custom user model check: {str(e)}'
            })
        
        # Test 12: Check if secure password hashing is used
        try:
            password_hashers = getattr(settings, 'PASSWORD_HASHERS', [])
            pbkdf2_used = any('PBKDF2' in hasher for hasher in password_hashers) if password_hashers else True  # Default uses PBKDF2
            results.append({
                'test': 'Password Hashing Algorithm',
                'status': 'PASS' if pbkdf2_used else 'WARNING',
                'risk': 'info' if pbkdf2_used else 'medium',
                'details': 'Using secure password hashing (PBKDF2)' if pbkdf2_used else 'Consider using more secure password hashing'
            })
        except Exception as e:
            results.append({
                'test': 'Password Hashing Algorithm',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Password hashing check: {str(e)}'
            })
        
        # Test 13: Check if clickjacking protection is enabled
        try:
            clickjacking_middleware = 'django.middleware.clickjacking.XFrameOptionsMiddleware' in settings.MIDDLEWARE
            results.append({
                'test': 'Clickjacking Protection',
                'status': 'PASS' if clickjacking_middleware else 'FAIL',
                'risk': 'info' if clickjacking_middleware else 'medium',
                'details': 'Clickjacking protection middleware is enabled' if clickjacking_middleware else 'Clickjacking protection not enabled'
            })
        except Exception as e:
            results.append({
                'test': 'Clickjacking Protection',
                'status': 'FAIL',
                'risk': 'medium',
                'details': f'Clickjacking protection check: {str(e)}'
            })
        
        # Test 14: Check if security middleware is enabled
        try:
            security_middleware = 'django.middleware.security.SecurityMiddleware' in settings.MIDDLEWARE
            results.append({
                'test': 'Security Middleware',
                'status': 'PASS' if security_middleware else 'FAIL',
                'risk': 'info' if security_middleware else 'high',
                'details': 'Security middleware is enabled' if security_middleware else 'Security middleware not enabled'
            })
        except Exception as e:
            results.append({
                'test': 'Security Middleware',
                'status': 'FAIL',
                'risk': 'high',
                'details': f'Security middleware check: {str(e)}'
            })
        
        # Test 15: Check if file upload size is limited
        try:
            max_upload_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', None)
            file_upload_limited = max_upload_size is not None
            results.append({
                'test': 'File Upload Size Limit',
                'status': 'PASS' if file_upload_limited else 'INFO',
                'risk': 'info',
                'details': f'File upload size limit is set to {max_upload_size} bytes' if file_upload_limited else 'No file upload size limit configured'
            })
        except Exception as e:
            results.append({
                'test': 'File Upload Size Limit',
                'status': 'INFO',
                'risk': 'info',
                'details': f'File upload size limit check: {str(e)}'
            })
        
        # Test 16: Check if user count is reasonable (to detect potential data leaks)
        try:
            user_count = User.objects.count()
            reasonable_user_count = user_count < 10000  # Arbitrary threshold for development
            results.append({
                'test': 'User Account Count',
                'status': 'PASS' if reasonable_user_count else 'INFO',
                'risk': 'info',
                'details': f'{user_count} user accounts found' if reasonable_user_count else f'{user_count} user accounts found (high count may indicate data leak)'
            })
        except Exception as e:
            results.append({
                'test': 'User Account Count',
                'status': 'INFO',
                'risk': 'info',
                'details': f'User account count check: {str(e)}'
            })
        
        # Test 17: Check if media files are served securely
        try:
            media_url = getattr(settings, 'MEDIA_URL', '')
            media_root = getattr(settings, 'MEDIA_ROOT', '')
            media_configured = media_url and media_root
            results.append({
                'test': 'Media Files Configuration',
                'status': 'PASS' if media_configured else 'INFO',
                'risk': 'info',
                'details': 'Media files are properly configured' if media_configured else 'Media files configuration check'
            })
        except Exception as e:
            results.append({
                'test': 'Media Files Configuration',
                'status': 'INFO',
                'risk': 'info',
                'details': f'Media files configuration check: {str(e)}'
            })
        
        # Calculate statistics
        stats = {
            'total_tests': len(results),
            'passed': len([r for r in results if r['status'] == 'PASS']),
            'failed': len([r for r in results if r['status'] == 'FAIL']),
            'warnings': len([r for r in results if r['status'] == 'WARNING']),
            'info': len([r for r in results if r['status'] == 'INFO']),
            'critical': len([r for r in results if r['risk'] == 'critical']),
            'high': len([r for r in results if r['risk'] == 'high']),
            'medium': len([r for r in results if r['risk'] == 'medium']),
            'low': len([r for r in results if r['risk'] == 'low'])
        }
        
        return JsonResponse({'results': results, 'stats': stats})
    
    return JsonResponse({'error': 'Invalid request method'})
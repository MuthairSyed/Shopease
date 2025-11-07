from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .forms import UserRegistrationForm, UserLoginForm, ManagerLoginForm, EditProfileForm, AddressForm
from .tokens import email_change_token
from accounts.models import User, Address, EmailChangeRequest


def create_manager():
    """
    to execute once on startup:
    this function will call in online_shop/urls.py
    """
    if not User.objects.filter(email="manager@example.com").first():
        user = User.objects.create_user(
            "manager@example.com", 'shop manager' ,'managerpass1234'
        )
        # give this user manager role
        user.is_manager = True
        user.save()


def manager_login(request):
    if request.method == 'POST':
        form = ManagerLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                request, email=data['email'], password=data['password']
            )
            if user is not None and user.is_manager:
                login(request, user)
                return redirect('dashboard:dashboard')
            else:
                messages.error(
                    request, 'username or password is wrong', 'danger'
                )
                return redirect('accounts:manager_login')
    else:
        form = ManagerLoginForm()
    context = {'form': form}
    return render(request, 'manager_login.html', context)


def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Check if email already exists
            if User.objects.filter(email=data['email']).exists():
                messages.error(request, 'An account with this email already exists. Please use a different email or login instead.')
                return render(request, 'register.html', {'title': 'Signup', 'form': form})
            
            user = User.objects.create_user(
                data['email'], data['full_name'], data['password1']
            )
            
            # Send professional HTML welcome email
            subject = '🎉 Welcome to ShopEase - Your Shopping Journey Starts Here!'
            
            # Plain text version (fallback)
            text_message = """
🎉 Welcome to ShopEase — Your One-Stop Destination for Effortless Shopping! 🎉

Dear valued customer,

We're thrilled to have you join our growing community of smart shoppers at ShopEase!

At ShopEase, we're committed to making your shopping experience simple, enjoyable, and rewarding. Whether you're looking for trendy fashion, home essentials, or the latest gadgets, you'll find everything you love — all at your fingertips.

WHAT YOU CAN EXPECT FROM US:

🛍️  Exclusive Member-Only Deals & Discounts
🚚  Fast & Reliable Delivery
💬  Personalized Recommendations
💳  Secure Checkout Process
🛡️  Easy Returns Policy
🔔  24/7 Customer Support

START EXPLORING TODAY:

Begin your journey with us by browsing our extensive collection of quality products. 
Don't forget to check out our weekly deals and seasonal promotions!

If you have any questions, feel free to reach out to our support team at support@shopease.com.

Thank you for choosing ShopEase. We look forward to serving you!

Best regards,

The ShopEase Team
📧 support@shopease.com  |  📞 +91 8971278930
🌐 www.shopease.com

Follow us on social media for the latest updates and exclusive offers:
📘 Facebook  |  🐦 Twitter  |  📷 Instagram  |  💼 LinkedIn
            """
            
            # HTML version
            html_message = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to ShopEase</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            background-color: #f5f7fa;
            padding: 20px;
        }
        .email-container {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid #e1e8ed;
        }
        .email-header {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .email-header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }
        .email-content {
            padding: 30px;
        }
        .section {
            margin-bottom: 25px;
        }
        .section-title {
            color: #2575fc;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e1e8ed;
        }
        .benefits {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        .benefit-item {
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 12px;
            border-left: 3px solid #2575fc;
            font-size: 14px;
        }
        .benefit-icon {
            font-size: 18px;
            margin-right: 8px;
            vertical-align: middle;
            color: #2575fc;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 15px;
            margin: 15px 0;
            text-align: center;
            box-shadow: 0 4px 15px rgba(37, 117, 252, 0.3);
            transition: all 0.3s ease;
        }
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(37, 117, 252, 0.4);
        }
        .footer {
            background-color: #1a1a1a;
            color: #ffffff;
            padding: 20px;
            text-align: center;
            font-size: 13px;
        }
        .footer a {
            color: #2575fc;
            text-decoration: none;
        }
        .social-links {
            margin-top: 15px;
        }
        .social-link {
            display: inline-block;
            margin: 0 8px;
            color: #2575fc;
            text-decoration: none;
            font-size: 18px;
        }
        @media (max-width: 480px) {
            body {
                padding: 10px;
            }
            .email-content {
                padding: 20px;
            }
            .benefits {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>🎉 Welcome to ShopEase</h1>
            <p>Your One-Stop Destination for Effortless Shopping!</p>
        </div>
        
        <div class="email-content">
            <div class="section">
                <h2 class="section-title">Dear Valued Customer,</h2>
                <p>We're thrilled to have you join our growing community of smart shoppers at <strong>ShopEase</strong>!</p>
                <p>At ShopEase, we're committed to making your shopping experience simple, enjoyable, and rewarding. Whether you're looking for trendy fashion, home essentials, or the latest gadgets, you'll find everything you love — all at your fingertips.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">🛍️ WHAT YOU CAN EXPECT FROM US</h2>
                <div class="benefits">
                    <div class="benefit-item">
                        <span class="benefit-icon">🎉</span> Exclusive Member-Only Deals
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon">🚚</span> Fast & Reliable Delivery
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon">💬</span> Personalized Recommendations
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon">💳</span> Secure Checkout Process
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon">🛡️</span> Easy Returns Policy
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon">🔔</span> 24/7 Customer Support
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">🚀 START EXPLORING TODAY</h2>
                <p>Begin your journey with us by browsing our extensive collection of quality products.</p>
                <center>
                    <a href="http://127.0.0.1:8000/" class="cta-button" style="color: white;">Start Shopping Now</a>
                </center>
                <p>Don't forget to check out our weekly deals and seasonal promotions!</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Thank you for choosing ShopEase. We look forward to serving you!</strong></p>
            <div class="contact-info">
                <p>📧 <a href="mailto:support@shopease.com">support@shopease.com</a> | 📞 +91 8971278930</p>
                <p>🌐 ShopEase E-commerce Platform</p>
            </div>
            <div class="social-links">
                <a href="#" class="social-link">📘</a>
                <a href="#" class="social-link">🐦</a>
                <a href="#" class="social-link">📷</a>
                <a href="#" class="social-link">💼</a>
            </div>
            <p>© 2025 ShopEase. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(
                request, 'Account created successfully. Welcome to ShopEase!', 'success'
            )
            login(request, user)
            return redirect('shop:home_page')
    else:
        form = UserRegistrationForm()
    context = {'title': 'Signup', 'form': form}
    return render(request, 'register.html', context)


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Check if user with this email exists
            try:
                user = User.objects.get(email=data['email'])
                # Authenticate the user
                user = authenticate(
                    request, email=data['email'], password=data['password']
                )
                if user is not None:
                    login(request, user)
                    # Redirect managers to dashboard, regular users to home page
                    if user.is_manager:
                        return redirect('dashboard:dashboard')
                    else:
                        return redirect('shop:home_page')
                else:
                    messages.error(
                        request, 'Incorrect password. Please try again.', 'danger'
                    )
                    return redirect('accounts:user_login')
            except User.DoesNotExist:  # type: ignore
                messages.error(
                    request, 'No account found with this email address. Please register first.', 'danger'
                )
                return redirect('accounts:user_login')
        else:
            # Form is not valid, render the form with errors
            context = {'title': 'Login', 'form': form}
            return render(request, 'login.html', context)
    else:
        form = UserLoginForm()
    context = {'title': 'Login', 'form': form}
    return render(request, 'login.html', context)


def user_logout(request):
    logout(request)
    return redirect('accounts:user_login')


def send_email_verification(request, user, new_email):
    """Send email verification for email change"""
    try:
        # Check if this email is already taken by another user
        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            messages.error(request, 'This email address is already registered. Please try a different email address.', 'danger')
            return False
        
        # Create or update email change request
        token = email_change_token.make_token(user)
        email_change_request, created = EmailChangeRequest.objects.update_or_create(  # pyright: ignore[reportAttributeAccessIssue]
            user=user,
            new_email=new_email,
            defaults={'token': token}
        )  # type: ignore  # type: ignore
        
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'
        
        # Create verification URL
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
        verification_url = f"{protocol}://{domain}{verification_url}"
        
        # Render email templates
        context = {
            'user': user,
            'new_email': new_email,
            'verification_url': verification_url,
        }
        
        # Plain text version
        text_message = render_to_string('email_verification.txt', context)
        
        # HTML version
        html_message = render_to_string('email_verification.html', context)
        
        # Send email
        subject = '📧 Verify Your New Email Address - ShopEase'
        result = send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [new_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return result > 0
        
    except Exception as e:
        messages.error(request, f'There was an error sending the verification email: {str(e)}. Please try again.')
        return False


def verify_email(request, uidb64, token):
    """Verify email change request"""
    try:
        # Decode user ID
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        
        # Retrieve email change request
        try:
            email_change_request = EmailChangeRequest.objects.get(user=user, token=token)  # type: ignore
        except EmailChangeRequest.DoesNotExist:  # type: ignore
            messages.error(request, 'Invalid verification link. Please try again.', 'danger')
            return redirect('accounts:user_login')
        
        # Check if request is expired
        if email_change_request.is_expired():
            email_change_request.delete()
            messages.error(request, 'This verification link has expired. Please request a new email change.', 'danger')
            return redirect('accounts:edit_profile')
        
        new_email = email_change_request.new_email
        
        # Check if email already exists for another user
        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            email_change_request.delete()
            messages.error(request, 'This email address is already registered. Please try a different email address.', 'danger')
            return redirect('accounts:user_login')
        
        # Update user's email
        old_email = user.email
        user.email = new_email
        user.save()
        
        # Delete the email change request
        email_change_request.delete()
        
        # Log out all sessions for this user
        from django.contrib.sessions.models import Session
        sessions = Session.objects.all()
        for session in sessions:
            session_data = session.get_decoded()
            if str(session_data.get('_auth_user_id')) == str(user.pk):
                session.delete()
        
        messages.success(request, f'Your email address has been successfully updated from {old_email} to {new_email}! Please log in with your new email address.', 'success')
        return redirect('accounts:user_login')
        
    except (TypeError, ValueError, OverflowError):
        messages.error(request, 'Invalid verification link. Please try again.', 'danger')
        return redirect('accounts:user_login')
    except ObjectDoesNotExist:
        messages.error(request, 'Invalid verification link. Please try again.', 'danger')
        return redirect('accounts:user_login')
    except Exception as e:
        messages.error(request, f'An error occurred during email verification: {str(e)}. Please try again.', 'danger')
        return redirect('accounts:user_login')


def edit_profile(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        form = EditProfileForm(request.POST, instance=request.user, user=request.user)
        
        if form_type == 'password':
            # Handle password change form
            if form.is_valid():
                old_password = form.cleaned_data.get('old_password')
                new_password1 = form.cleaned_data.get('new_password1')
                new_password2 = form.cleaned_data.get('new_password2')
                
                # Check if password fields are filled
                if old_password and new_password1 and new_password2:
                    # Validate and save password
                    form.save()
                    messages.success(request, 'Your password has been updated successfully', 'success')
                else:
                    messages.error(request, 'Please fill in all password fields', 'danger')
                return redirect('accounts:edit_profile')
        else:
            # Handle profile update form
            if form.is_valid():
                # Check if email is being changed
                new_email = form.cleaned_data.get('email')
                current_email = request.user.email
                email_changed = new_email and new_email != current_email
                
                if email_changed:
                    # Check if the new email is already taken
                    if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                        messages.error(request, 'This email address is already registered. Please try a different email address.', 'danger')
                        return redirect('accounts:edit_profile')
                    
                    # Send verification email
                    email_sent = send_email_verification(request, request.user, new_email)
                    if email_sent:
                        # Show info message
                        messages.info(request, f'A verification email has been sent to {new_email}. Please check your email to verify the change.', 'info')
                    else:
                        # Show error message if email failed to send
                        messages.error(request, 'Failed to send verification email. Please try again.', 'danger')
                    return redirect('accounts:edit_profile')
                else:
                    # No email change, save profile information
                    form.save()
                    messages.success(request, 'Your profile has been updated successfully', 'success')
                    # Redirect to appropriate profile page based on user type
                    if hasattr(request.user, 'is_manager') and request.user.is_manager:
                        return redirect('dashboard:dashboard')  # Redirect managers to dashboard
                    else:
                        return redirect('accounts:edit_profile')
    else:
        form = EditProfileForm(instance=request.user, user=request.user)
    
    context = {'title':'Edit Profile', 'form':form}
    
    # Render appropriate template based on user type
    if hasattr(request.user, 'is_manager') and request.user.is_manager:
        return render(request, 'dashboard/edit_profile.html', context)
    else:
        return render(request, 'edit_profile.html', context)


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    context = {'title': 'My Addresses', 'addresses': addresses}
    return render(request, 'addresses.html', context)


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm(user=request.user)
    
    context = {'title': 'Add New Address', 'form': form}
    return render(request, 'add_address.html', context)


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address, user=request.user)
    
    context = {'title': 'Edit Address', 'form': form, 'address': address}
    return render(request, 'edit_address.html', context)


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Allow deletion of any address, including the last one
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    
    return redirect('accounts:address_list')


@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Set this address as default and unset others
    request.user.addresses.update(is_default=False)
    address.is_default = True
    address.save()
    
    messages.success(request, f'{address.title} has been set as your default address.')
    return redirect('accounts:address_list')
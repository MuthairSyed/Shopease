from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
from django.conf import settings

from shop.models import Product, Category
from cart.forms import QuantityForm
from .forms import ContactForm


def paginat(request, list_objects):
	p = Paginator(list_objects, 20)
	page_number = request.GET.get('page')
	try:
		page_obj = p.get_page(page_number)
	except PageNotAnInteger:
		page_obj = p.page(1)
	except EmptyPage:
		page_obj = p.page(p.num_pages)
	return page_obj


def home_page(request):
	products = Product.objects.all()
	context = {'products': paginat(request ,products)}
	return render(request, 'home_page.html', context)


def product_detail(request, slug):
	form = QuantityForm()
	product = get_object_or_404(Product, slug=slug)
	related_products = Product.objects.filter(category=product.category).all()[:5]
	context = {
		'title':product.title,
		'product':product,
		'form':form,
		'favorites':'favorites',
		'related_products':related_products
	}
	# Check if user is authenticated before accessing likes
	if request.user.is_authenticated and request.user.likes.filter(id=product.id).first():
		context['favorites'] = 'remove'
	return render(request, 'product_detail.html', context)


@login_required
def add_to_favorites(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	request.user.likes.add(product)
	return redirect('shop:product_detail', slug=product.slug)


@login_required
def remove_from_favorites(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	request.user.likes.remove(product)
	return redirect('shop:favorites')


@login_required
def favorites(request):
	products = request.user.likes.all()
	context = {'title':'Favorites', 'products':products}
	return render(request, 'favorites.html', context)


def search(request):
	query = request.GET.get('q')
	products = Product.objects.filter(title__icontains=query).all()
	context = {'products': paginat(request ,products)}
	return render(request, 'home_page.html', context)


def filter_by_category(request, slug):
	"""when user clicks on parent category
	we want to show all products in its sub-categories too
	"""
	result = []
	category = Category.objects.filter(slug=slug).first()
	[result.append(product) \
		for product in Product.objects.filter(category=category.id).all()]
	# check if category is parent then get all sub-categories
	if not category.is_sub:
		sub_categories = category.sub_categories.all()
		# get all sub-categories products 
		for category in sub_categories:
			[result.append(product) \
				for product in Product.objects.filter(category=category).all()]
	context = {'products': paginat(request ,result)}
	return render(request, 'home_page.html', context)


def about(request):
    context = {'title': 'About Us'}
    return render(request, 'about.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Prepare the email content with better formatting
            full_message = f"""
New Contact Form Submission

----------------------------------------
Sender Information:
----------------------------------------
Name: {name}
Email: {email}

----------------------------------------
Message Details:
----------------------------------------
Subject: {subject}

Message:
{message}

----------------------------------------
Sent from ShopEase Contact Form
Support: support@shopease.com
Phone: +91 8971278930
            """
            
            # Send email
            try:
                send_mail(
                    f"ShopEase Contact Form: {subject}",
                    full_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your message. We will get back to you soon!')
                return redirect('shop:contact')
            except Exception as e:
                messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
                print(f"Email sending error: {e}")
    else:
        form = ContactForm()
    
    context = {'title': 'Contact Us', 'form': form}
    return render(request, 'contact.html', context)


def faq(request):
    context = {'title': 'Frequently Asked Questions'}
    return render(request, 'faq.html', context)


def return_policy(request):
    context = {'title': 'Return Policy'}
    return render(request, 'return_policy.html', context)


def privacy_policy(request):
    context = {'title': 'Privacy Policy'}
    return render(request, 'privacy_policy.html', context)


def terms_of_service(request):
    context = {'title': 'Terms of Service'}
    return render(request, 'terms_of_service.html', context)

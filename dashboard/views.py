from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404

from shop.models import Product
from accounts.models import User
from orders.models import Order, OrderItem
from .forms import AddProductForm, AddCategoryForm, EditProductForm


def is_manager(user):
    try:
        if not user.is_manager:
            return False
        return True
    except:
        return False


@user_passes_test(is_manager)
@login_required
def dashboard(request):
    # Handle status update
    if request.method == 'POST' and 'update_status' in request.POST:
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(id=order_id)
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}')
            else:
                messages.error(request, 'Invalid status')
        except Exception as e:
            messages.error(request, 'Error updating order status')
        return redirect('dashboard:dashboard')
    
    # Get dashboard statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    
    # Get recent orders
    recent_orders = Order.objects.all().order_by('-created')[:5]
    
    context = {
        'title': 'Dashboard',
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'recent_orders': recent_orders
    }
    return render(request, 'dashboard.html', context)


@user_passes_test(is_manager)
@login_required
def products(request):
    # Handle price update
    if request.method == 'POST' and 'update_price' in request.POST:
        product_id = request.POST.get('product_id')
        new_price = request.POST.get('price')
        try:
            product = Product.objects.get(id=product_id)
            product.price = int(new_price)
            product.save()
            messages.success(request, f'Price updated for {product.title}')
        except Exception as e:
            messages.error(request, 'Error updating price')
        return redirect('dashboard:products')
    
    products = Product.objects.all()
    context = {'title':'Products' ,'products':products}
    return render(request, 'products.html', context)


@user_passes_test(is_manager)
@login_required
def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added Successfuly!')
            return redirect('dashboard:add_product')
    else:
        form = AddProductForm()
    context = {'title':'Add Product', 'form':form}
    return render(request, 'add_product.html', context)


@user_passes_test(is_manager)
@login_required
def delete_product(request, id):
    product = Product.objects.filter(id=id).delete()
    messages.success(request, 'product has been deleted!', 'success')
    return redirect('dashboard:products')


@user_passes_test(is_manager)
@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been updated', 'success')
            return redirect('dashboard:products')
    else:
        form = EditProductForm(instance=product)
    context = {'title': 'Edit Product', 'form':form}
    return render(request, 'edit_product.html', context)


@user_passes_test(is_manager)
@login_required
def add_category(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added Successfuly!')
            return redirect('dashboard:add_category')
    else:
        form = AddCategoryForm()
    context = {'title':'Add Category', 'form':form}
    return render(request, 'add_category.html', context)


@user_passes_test(is_manager)
@login_required
def orders(request):
    # Handle status update
    if request.method == 'POST' and 'update_status' in request.POST:
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(id=order_id)
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}')
            else:
                messages.error(request, 'Invalid status')
        except Exception as e:
            messages.error(request, 'Error updating order status')
        return redirect('dashboard:orders')
    
    orders = Order.objects.all()
    context = {'title':'Orders', 'orders':orders}
    return render(request, 'orders.html', context)


@user_passes_test(is_manager)
@login_required
def order_detail(request, id):
    order = Order.objects.filter(id=id).first()
    items = OrderItem.objects.filter(order=order).all()
    
    # Handle status update
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
            return redirect('dashboard:order_detail', id=order.id)
    
    context = {'title':'Order Detail', 'items':items, 'order':order}
    return render(request, 'order_detail.html', context)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'status', 'order_status', 'total_price_inr')
    list_filter = ('status', 'created')
    search_fields = ('user__email', 'user__full_name', 'id')
    list_editable = ('status',)
    readonly_fields = ('created', 'updated', 'user', 'get_total_price')
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'created', 'updated')
        }),
        ('Items', {
            'fields': ()
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__product')
    
    @admin.display(description='Total Price (₹)')
    def total_price_inr(self, obj):
        return format_html('₹{}', obj.get_total_price)
        
    @admin.display(description='Order Status')
    def order_status(self, obj):
        status_colors = {
            'pending': 'orange',
            'processing': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span class="status-badge status-{}" style="background-color: {}; color: white;">{}</span>',
            obj.status,
            color,
            obj.get_status_display()
        )
    
    def has_add_permission(self, request):
        # Disable add permission as orders are created by users
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_inr', 'total_cost_inr')
    list_filter = ('order__status', 'order__created')
    readonly_fields = ('order', 'product', 'price', 'quantity', 'get_cost')
    
    @admin.display(description='Price (₹)')
    def price_inr(self, obj):
        return format_html('₹{}', obj.price)
    
    @admin.display(description='Total Cost (₹)')
    def total_cost_inr(self, obj):
        return format_html('₹{}', obj.get_cost())
    
    def has_add_permission(self, request):
        # Disable add permission as order items are created with orders
        return False
    
    def has_change_permission(self, request, obj=None):
        # Disable change permission
        return False
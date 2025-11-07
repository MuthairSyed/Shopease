from django.db import models
from typing import Any

from accounts.models import User, Address
from shop.models import Product


class Order(models.Model):
    # Type hints for Django's automatic fields to help type checkers
    id: int
    items: Any
    objects: Any
    
    # Order status choices
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]
    
    # Payment method choices
    PAYMENT_CREDIT_CARD = 'credit_card'
    PAYMENT_PAYPAL = 'paypal'
    PAYMENT_UPI = 'upi'
    PAYMENT_COD = 'cod'
    
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CREDIT_CARD, 'Credit/Debit Card'),
        (PAYMENT_PAYPAL, 'PayPal'),
        (PAYMENT_UPI, 'UPI'),
        (PAYMENT_COD, 'Cash on Delivery'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_CREDIT_CARD)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.id)

    @property
    def get_total_price(self) -> int:
        total = sum(item.get_cost() for item in self.items.all())
        return total  # type: ignore
    

class OrderItem(models.Model):
    # Type hints for Django's automatic fields to help type checkers
    id: int
    order: Any
    product: Any
    objects: Any
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.IntegerField()
    quantity = models.SmallIntegerField(default=1)  # type: ignore

    def __str__(self):
        return str(self.id)

    def get_cost(self) -> int:
        return self.price * self.quantity  # type: ignore
from django.urls import path

from orders import views

app_name = "orders"

urlpatterns = [
    path('create', views.create_order, name='create_order'),
    path('list', views.user_orders, name='user_orders'),
    path('checkout/<int:order_id>', views.checkout, name='checkout'),
    path('payment/<int:order_id>', views.payment_page, name='payment'),
    path('process-payment/<int:order_id>', views.process_payment, name='process_payment'),
    path('payment-success/<int:order_id>', views.payment_success, name='payment_success'),
    path('fake-payment/<int:order_id>', views.process_payment, name='pay_order'),
    path('download-invoice/<int:order_id>', views.download_invoice, name='download_invoice'),
    path('tracking/<int:order_id>', views.order_tracking, name='order_tracking'),
    path('cancel/<int:order_id>', views.cancel_order, name='cancel_order'),
    path('invoice/<int:order_id>', views.invoice_detail, name='invoice_detail'),
]
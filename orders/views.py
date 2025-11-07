from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import reverse

from .models import Order, OrderItem
from accounts.models import Address
from cart.utils.cart import Cart

import os
from reportlab.platypus import Image

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


@login_required
def create_order(request):
    cart = Cart(request)
    
    # Create order first
    order = Order.objects.create(user=request.user)
    
    # Add items to order
    for item in cart:
        OrderItem.objects.create(
            order=order, product=item['product'],
            price=item['price'], quantity=item['quantity']
        )
    
    # If user has a default address, assign it to the order
    default_address = request.user.addresses.filter(is_default=True).first()
    if default_address:
        order.delivery_address = default_address
        order.save()
    
    return redirect('orders:checkout', order_id=order.id)


@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get user's addresses
    addresses = request.user.addresses.all()
    default_address = request.user.addresses.filter(is_default=True).first()
    
    # Calculate GST and total
    subtotal = order.get_total_price
    gst = subtotal * 0.18
    total = subtotal + gst
    
    if request.method == 'POST':
        address_id = request.POST.get('delivery_address')
        if address_id:
            try:
                address = request.user.addresses.get(id=address_id)
                order.delivery_address = address
                order.save()
                return redirect('orders:payment', order_id=order.id)
            except Exception:
                messages.error(request, 'Invalid address selected.')
        else:
            messages.error(request, 'Please select a delivery address.')
    
    context = {
        'title': 'Checkout',
        'order': order,
        'addresses': addresses,
        'default_address': default_address,
        'gst': gst,
        'total': total
    }
    return render(request, 'checkout.html', context)


@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Calculate GST and total
    subtotal = order.get_total_price
    gst = subtotal * 0.18
    total = subtotal + gst
    
    context = {
        'title': 'Payment', 
        'order': order,
        'gst': gst,
        'total': total
    }
    return render(request, 'payment.html', context)


@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Only process payment on POST request
    if request.method == 'POST':
        # Get the selected payment method from the form
        payment_method = request.POST.get('payment_method', 'credit_card')
        
        # Save payment method to the order
        order.payment_method = payment_method
        order.save()
        
        # Clear the cart
        cart = Cart(request)
        cart.clear()
        
        # Update order status to processing (not delivered)
        order.status = Order.PROCESSING
        order.save()
        
        # Send confirmation email with invoice
        send_order_confirmation_email(request.user, order)
        
        # Redirect to success page to prevent reprocessing on refresh
        return redirect('orders:payment_success', order_id=order.id)
    
    # For GET requests, just show the success page if order is already processed
    if order.status == Order.PROCESSING:
        context = {'title': 'Payment Successful', 'order': order}
        return render(request, 'payment_success.html', context)
    
    # If order is not processed yet, redirect to payment page
    return redirect('orders:payment', order_id=order.id)


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'title': 'Payment Successful', 'order': order}
    return render(request, 'payment_success.html', context)


def send_order_confirmation_email(user, order):
    # Prepare email content
    subject = '🛍️ Order Confirmation - ShopEase'
    
    # Render HTML email
    html_message = render_to_string('order_confirmation_email.html', {
        'user': user,
        'order': order,
        'items': order.items.all()
    })
    
    # Plain text version
    plain_message = strip_tags(html_message)
    
    # Generate PDF invoice
    pdf_buffer = None
    try:
        pdf_buffer = generate_modern_invoice_pdf(user, order)
    except Exception as e:
        print(f"Failed to generate PDF invoice: {e}")
        # Fallback to original invoice
        try:
            pdf_buffer = generate_invoice_pdf(user, order)
        except Exception as e2:
            print(f"Failed to generate fallback PDF invoice: {e2}")
    
    # Send email with PDF attachment
    try:
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_message, "text/html")
        
        # Attach PDF invoice if generated successfully
        if pdf_buffer:
            email.attach(f'invoice-{order.id}.pdf', pdf_buffer.getvalue(), 'application/pdf')
        
        email.send()
    except Exception as e:
        # Log the error but don't fail the payment
        print(f"Failed to send order confirmation email: {e}")


def generate_invoice_pdf(user, order):
    """Generate PDF invoice for the order using ReportLab"""
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Sample stylesheet
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("ShopEase Invoice", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Order details
    elements.append(Paragraph(f"Invoice #SE-{order.id}", styles['Heading2']))
    elements.append(Paragraph(f"Order Date: {order.created.strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Customer details
    elements.append(Paragraph("Billing To:", styles['Heading3']))
    elements.append(Paragraph(f"{user.full_name or user.email}", styles['Normal']))
    elements.append(Paragraph(f"{user.email}", styles['Normal']))
    elements.append(Paragraph("+91 89712 78930", styles['Normal']))
    elements.append(Paragraph("123 Shopping Street, Retail City, 560032", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Items table
    data = [['Item', 'SKU', 'Qty', 'Unit Price', 'Total']]
    for item in order.items.all():
        data.append([
            item.product.title,
            f"SE-{item.product.id}",
            str(item.quantity),
            f"₹{item.price}",
            f"₹{item.get_cost()}"
        ])
    
    # Add totals
    data.append(['', '', '', 'Subtotal', f"₹{order.get_total_price}"])
    gst = order.get_total_price * 0.18
    data.append(['', '', '', 'GST (18%)', f"₹{gst:.2f}"])
    data.append(['', '', '', 'Total', f"₹{order.get_total_price + gst:.2f}"])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # Notes
    elements.append(Paragraph("Notes:", styles['Heading3']))
    elements.append(Paragraph("Thank you for shopping with ShopEase! If you have questions about this invoice, please contact support@shopease.com or call +91 89712 78930.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Reset buffer position to beginning
    buffer.seek(0)
    
    return buffer


def generate_modern_invoice_pdf(user, order):
    """Generate modern PDF invoice for the order using ReportLab"""
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=30, bottomMargin=30)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles - using only basic fonts to avoid encoding issues
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1779ba'),
        alignment=1,  # Center alignment
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#9b9b9b'),
        alignment=1,  # Center alignment
        spaceAfter=20,
        fontName='Helvetica'
    )
    
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor('#1779ba'),
        alignment=0,  # Left alignment
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    company_subtitle_style = ParagraphStyle(
        'CompanySubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=0,  # Left alignment
        spaceAfter=20,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1779ba'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        fontName='Helvetica'
    )
    
    bold_style = ParagraphStyle(
        'BoldText',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )
    
    right_align_style = ParagraphStyle(
        'RightAlign',
        parent=normal_style,
        alignment=2  # Right alignment
    )
    
    center_align_style = ParagraphStyle(
        'CenterAlign',
        parent=normal_style,
        alignment=1,  # Center alignment
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9b9b9b'),
        alignment=1,  # Center alignment
    )
    
    # Header with logo
    # Add the shopping bag image to the header
    try:
        # Get the absolute path to the image
        image_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'shopping_bags.png')
        if os.path.exists(image_path):
            # Add image to the header
            logo = Image(image_path, width=30, height=30)
            logo.hAlign = 'LEFT'
            
            # Create a table to align the logo and text
            header_data = [
                [logo, Paragraph("ShopEase Invoice", title_style)],
                ['', Paragraph("Professional E-commerce Invoice", subtitle_style)]
            ]
            
            header_table = Table(header_data, colWidths=[40, 460])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(header_table)
        else:
            # Fallback if image is not found
            elements.append(Paragraph("🛍️ ShopEase Invoice", title_style))
            elements.append(Paragraph("Professional E-commerce Invoice", subtitle_style))
    except:
        # Fallback if there's any error with the image
        elements.append(Paragraph("🛍️ ShopEase Invoice", title_style))
        elements.append(Paragraph("Professional E-commerce Invoice", subtitle_style))
    
    elements.append(Spacer(1, 8))  # Further reduced spacing
    
    # Company Info and Invoice Header - More compact
    header_data = [
        [Paragraph("ShopEase", company_style), Paragraph("INVOICE", title_style)],
        [Paragraph("Simple. Fast. Delightful.", company_subtitle_style), Paragraph("", normal_style)]
    ]
    
    header_table = Table(header_data, colWidths=[300, 200])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 12))  # Reduced spacing
    
    # Customer Greeting and Invoice Info - Enhanced greeting
    customer_name = user.full_name or user.email
    customer_info = Paragraph(f"<b>Hello, {customer_name}!</b><br/>Thank you for choosing ShopEase. We're delighted to serve you and hope you love your purchase!", normal_style)
    order_info = Paragraph(f"<b>Order #{order.id}</b><br/>{order.created.strftime('%B %d, %Y')}", right_align_style)
    
    intro_data = [
        [customer_info, order_info]
    ]
    
    intro_table = Table(intro_data, colWidths=[300, 200])
    intro_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(intro_table)
    elements.append(Spacer(1, 25))  # Adjusted spacing
    
    # Items table header
    elements.append(Paragraph("Order Items", heading_style))
    
    # Items table
    items_header = [
        [Paragraph("Item Description", subheading_style), 
         Paragraph("Item ID", subheading_style), 
         Paragraph("Quantity", subheading_style), 
         Paragraph("Subtotal", subheading_style)]
    ]
    
    # Add items
    items_data = []
    for item in order.items.all():
        items_data.append([
            Paragraph(item.product.title, normal_style),
            Paragraph(f"SE-{item.product.id}", normal_style),
            Paragraph(str(item.quantity), center_align_style),
            Paragraph(f"Rs. {item.get_cost()}", right_align_style)
        ])
    
    # Combine header and items
    all_items_data = items_header + items_data
    
    items_table = Table(all_items_data, colWidths=[250, 80, 80, 90])
    items_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#c8c3be')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eeeeee')),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Totals
    subtotal = order.get_total_price
    gst = subtotal * 0.18
    total = subtotal + gst
    
    totals_data = [
        ['', Paragraph("Subtotal", bold_style), Paragraph(f"Rs. {subtotal}", right_align_style)],
        ['', Paragraph("Shipping & Handling", bold_style), Paragraph("Rs. 0.00", right_align_style)],
        ['', Paragraph("GST (18%)", bold_style), Paragraph(f"Rs. {gst:.2f}", right_align_style)],
        ['', Paragraph("Total", bold_style), Paragraph(f"Rs. {total:.2f}", right_align_style)]
    ]
    
    totals_table = Table(totals_data, colWidths=[350, 100, 100])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (1, 3), (2, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LINEABOVE', (1, 2), (2, 2), 1, colors.HexColor('#1779ba')),
        ('LINEBELOW', (1, 2), (2, 2), 1, colors.HexColor('#1779ba')),
        ('LINEABOVE', (1, 3), (2, 3), 1, colors.black),
        ('LINEBELOW', (1, 3), (2, 3), 1, colors.black),
        ('LINEWIDTH', (1, 3), (2, 3), 2),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    
    # Additional Information Header
    elements.append(Paragraph("Additional Information", heading_style))
    elements.append(Spacer(1, 10))
    
    # Get the delivery address if available, otherwise use default user info
    if order.delivery_address:
        billing_name = order.delivery_address.full_name
        billing_phone = order.delivery_address.phone_number
        billing_address = f"{order.delivery_address.street_address} {order.delivery_address.city}, {order.delivery_address.state} {order.delivery_address.postal_code} {order.delivery_address.country}"
    else:
        billing_name = user.full_name or user.email
        billing_phone = "+91 89712 78930"
        billing_address = "123 Shopping Street Retail City, 560032 India"
    
    # Billing Information
    elements.append(Paragraph("Billing Information", subheading_style))
    elements.append(Paragraph(billing_name, normal_style))
    elements.append(Paragraph(billing_phone, normal_style))
    elements.append(Paragraph(billing_address, normal_style))
    elements.append(Spacer(1, 15))
    
    # Payment Information
    elements.append(Paragraph("Payment Information", subheading_style))
    
    # Determine payment method from the order
    if order.payment_method == 'cod':
        payment_method = "Cash on Delivery"
        transaction_id = f"COD-SE-{order.id}{order.created.strftime('%Y%m%d')}"
        payment_status = "Unpaid (COD)"
    elif order.payment_method == 'paypal':
        payment_method = "PayPal"
        transaction_id = f"TXN-SE-{order.id}{order.created.strftime('%Y%m%d')}"
        payment_status = "Paid"
    elif order.payment_method == 'upi':
        payment_method = "UPI"
        transaction_id = f"TXN-SE-{order.id}{order.created.strftime('%Y%m%d')}"
        payment_status = "Paid"
    else:
        payment_method = "Credit/Debit Card"
        transaction_id = f"TXN-SE-{order.id}{order.created.strftime('%Y%m%d')}"
        payment_status = "Paid"
    
    amount_paid = f"Rs. {total:.2f}"
    
    elements.append(Paragraph(f"Method: {payment_method}", normal_style))
    elements.append(Paragraph(f"Transaction ID: {transaction_id}", normal_style))
    elements.append(Paragraph(f"Amount: {amount_paid}", normal_style))
    elements.append(Paragraph(f"Status: {payment_status}", normal_style))
    elements.append(Spacer(1, 30))
    
    # Footer
    elements.append(Paragraph("ShopEase E-commerce Platform support@shopease.com +91 89712 78930", footer_style))
    elements.append(Paragraph("123 Shopping Street, Retail City, 560032, India", footer_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Thank you for your business!", center_align_style))
    
    # Build PDF
    doc.build(elements)
    
    # Reset buffer position to beginning
    buffer.seek(0)
    
    return buffer


@login_required
def user_orders(request):
    orders = request.user.orders.all()
    context = {'title':'Orders', 'orders': orders}
    return render(request, 'user_orders.html', context)


@login_required
def order_tracking(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'title': 'Order Tracking', 'order': order}
    return render(request, 'order_tracking.html', context)


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order can be cancelled (not already cancelled or delivered)
    if order.status not in [Order.CANCELLED, Order.DELIVERED]:
        order.status = Order.CANCELLED
        order.save()
        
        # Send cancellation email
        send_cancellation_email(request, order)
        
        messages.success(request, 'Your order has been successfully cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('orders:user_orders')


def send_cancellation_email(request, order):
    """Send order cancellation email to the user"""
    subject = '🛍️ Order Cancelled - ShopEase'
    
    # Calculate refund amount (full amount in this case)
    refund_amount = order.get_total_price
    
    # Format items list
    items = order.items.all()
    items_list = ", ".join([f"{item.product.title} (x{item.quantity})" for item in items])
    
    # Get the base URL for links
    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
    
    # Render HTML email
    html_message = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width">
      <title>Order Cancelled</title>
    </head>
    <body style="margin:0;padding:0;background:#f6f8fa;font-family:system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
      <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:680px;margin:28px auto;background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.06);">
        
        <!-- Header -->
        <tr>
          <td style="padding:20px 24px;background:#1e3a8a;color:#ffffff;">
            <h1 style="margin:0;font-size:20px;font-weight:600;">We're sorry to see you go 😔</h1>
            <p style="margin:6px 0 0;font-size:13px;opacity:0.9;">Your order #{order.id} has been cancelled.</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:24px;">
            <p style="margin:0 0 12px;font-size:15px;color:#0f172a;">
              Hi {order.user.full_name or order.user.email},
            </p>

            <p style="margin:0 0 16px;font-size:15px;color:#334155;line-height:1.5;">
              We noticed you've cancelled your recent order <strong>#{order.id}</strong> placed on <strong>{order.created.strftime('%B %d, %Y')}</strong>.  
              We're genuinely sorry to see you go — your satisfaction means a lot to us.
            </p>

            <p style="margin:0 0 16px;font-size:15px;color:#334155;line-height:1.5;">
              If something didn't meet your expectations, please let us know. Your feedback helps us improve and serve you better next time.
            </p>

            <!-- Order summary -->
            <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;margin:16px 0 20px;">
              <tr>
                <td style="padding:12px;border:1px solid #e6eef8;border-radius:6px;background:#fbfdff;">
                  <strong style="display:block;margin-bottom:6px;font-size:14px;color:#0b1a2b;">Order summary</strong>
                  <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                      <td style="font-size:14px;color:#475569;padding:6px 0;width:70%;">Item(s)</td>
                      <td style="font-size:14px;color:#0b1a2b;padding:6px 0;text-align:right;">{items.count()} • {items_list}</td>
                    </tr>
                    <tr>
                      <td style="font-size:14px;color:#475569;padding:6px 0;">Subtotal</td>
                      <td style="font-size:14px;color:#0b1a2b;padding:6px 0;text-align:right;">₹{order.get_total_price}</td>
                    </tr>
                    <tr>
                      <td style="font-size:14px;color:#475569;padding:6px 0;">Shipping</td>
                      <td style="font-size:14px;color:#0b1a2b;padding:6px 0;text-align:right;">₹0</td>
                    </tr>
                    <tr>
                      <td style="font-size:14px;color:#475569;padding:6px 0;border-top:1px solid #eef3fb;padding-top:10px;">Refund amount</td>
                      <td style="font-size:14px;color:#1e3a8a;padding:6px 0;border-top:1px solid #eef3fb;padding-top:10px;text-align:right;font-weight:600;">₹{refund_amount}</td>
                    </tr>
                    <tr>
                      <td colspan="2" style="padding-top:10px;font-size:13px;color:#64748b;">Refund status: <strong>Processing</strong> — expected to appear on your original payment method within <strong>5-7 business days</strong>.</td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>

            <!-- CTA -->
            <div style="text-align:center;margin:18px 0;">
              <a href="mailto:support@shopease.com?subject=Feedback for Order #{order.id}" style="text-decoration:none;display:inline-block;padding:12px 22px;border-radius:8px;background:#1e3a8a;color:#ffffff;font-weight:600;">
                Share feedback
              </a>
              <a href="{base_url}/shop/" style="text-decoration:none;display:inline-block;padding:12px 22px;border-radius:8px;background:#f1f5f9;color:#1e3a8a;font-weight:600;margin-left:10px;">
                Shop again
              </a>
            </div>

            <p style="margin:0 0 12px;font-size:14px;color:#334155;line-height:1.45;">
              We hope to have the opportunity to serve you again soon.  
              Thank you for considering <strong>ShopEase</strong>.
            </p>

            <p style="margin:12px 0 0;font-size:13px;color:#64748b;">
              Need help? Contact us at <a href="mailto:support@shopease.com" style="color:#1e3a8a;text-decoration:underline;">support@shopease.com</a> or call +91 89712 78930.
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:18px 24px;background:#f8fafc;color:#667085;font-size:12px;">
            <div style="margin-bottom:8px;">Order ID: <strong>#{order.id}</strong></div>
            <div style="color:#94a3b8;">ShopEase · 123 Shopping Street, Retail City, 560032 · <a href="#" style="color:#94a3b8;text-decoration:underline;">Manage preferences</a></div>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    
    # Plain text version
    plain_message = f"""
    We're sorry to see you go 😔
    
    Your order #{order.id} has been cancelled.
    
    Hi {order.user.full_name or order.user.email},
    
    We noticed you've cancelled your recent order #{order.id} placed on {order.created.strftime('%B %d, %Y')}.
    We're genuinely sorry to see you go — your satisfaction means a lot to us.
    
    If something didn't meet your expectations, please let us know. Your feedback helps us improve and serve you better next time.
    
    Order summary:
    Item(s): {items.count()} • {items_list}
    Subtotal: ₹{order.get_total_price}
    Shipping: ₹0
    Refund amount: ₹{refund_amount}
    
    Refund status: Processing — expected to appear on your original payment method within 5-7 business days.
    
    We hope to have the opportunity to serve you again soon.
    Thank you for considering ShopEase.
    
    Need help? Contact us at support@shopease.com or call +91 89712 78930.
    
    Order ID: #{order.id}
    ShopEase · 123 Shopping Street, Retail City, 560032
    """
    
    # Send email
    try:
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
    except Exception as e:
        # Log the error but don't fail the cancellation
        print(f"Failed to send cancellation email: {e}")


@login_required
def invoice_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    
    # Calculate GST and total
    subtotal = order.get_total_price
    gst = subtotal * 0.18
    total = subtotal + gst
    
    context = {
        'title': 'Invoice Details',
        'order': order,
        'items': items,
        'user': request.user,
        'gst': gst,
        'total': total
    }
    return render(request, 'invoice_detail.html', context)


@login_required
def download_invoice(request, order_id):
    """Download invoice as PDF"""
    try:
        print(f"Attempting to download invoice for order {order_id}")
        # Get the order
        order = get_object_or_404(Order, id=order_id)
        # Get the user from the order
        user = order.user
        items = order.items.all()
        
        # Calculate GST and total
        subtotal = order.get_total_price
        gst = subtotal * 0.18
        total = subtotal + gst
        
        print(f"Found order {order.id} for user {user.email}")
        
        # Generate PDF using ReportLab with our modern design
        pdf_buffer = generate_modern_invoice_pdf(user, order)
        
        # Create response
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice-{order.id}.pdf"'
        print("Response created successfully")
        
        return response
    except Exception as e:
        print(f"Error generating invoice: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to return a simple PDF with error message
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph("Invoice Download Error", styles['Title']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Could not generate invoice for order {order_id}", styles['Normal']))
            elements.append(Paragraph(f"Error: {str(e)}", styles['Normal']))
            
            doc.build(elements)
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="error-invoice-{order_id}.pdf"'
            return response
        except Exception as e2:
            print(f"Error generating error PDF: {e2}")
            # Final fallback - return a simple text response
            return HttpResponse(f"Error generating invoice: {str(e)}".encode('utf-8'), content_type='text/plain')

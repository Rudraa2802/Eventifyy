# Payment Gateway Integration & Ticket System Setup Guide

## Overview
Your Local Event Finder application now includes:
1. **Razorpay Payment Gateway Integration** - Secure payment processing
2. **Automated Ticket Generation** - QR codes and unique ticket IDs
3. **Ticket Display System** - Beautiful ticket display with QR codes

## What's New

### 1. Updated Models
- **EventRegistration**: Added payment tracking fields
  - `payment_status`: Tracks payment state (Pending, Completed, Failed, Refunded)
  - `razorpay_order_id`: Stores Razorpay order ID
  - `razorpay_payment_id`: Stores Razorpay payment ID

- **Ticket**: New model for ticket generation
  - `ticket_id`: Unique ticket identifier (auto-generated)
  - `qr_code`: QR code image for event entry
  - `created_at`: Timestamp of ticket generation

### 2. New Views Added
- `verify_payment()`: Verifies Razorpay payment and creates tickets
- `generate_ticket()`: Generates QR codes and ticket records
- `view_ticket()`: Displays ticket to user
- `download_ticket()`: Downloads ticket (PDF ready for enhancement)

### 3. Updated Templates
- **checkout.html**: Now uses Razorpay payment form
- **ticket.html**: New beautiful ticket display page
- **dashboard.html**: Added "View Ticket" button for confirmed payments

### 4. New URLs
```
/payment/verify/           - Payment verification endpoint
/ticket/<registration_id>/ - View ticket
/ticket/<ticket_id>/download/ - Download ticket
```

## Installation Steps

### Step 1: Install Required Packages
```bash
pip install razorpay qrcode[pil] pillow
```

### Step 2: Update Settings
Edit `local_event_finder/settings.py` and add your Razorpay credentials:

```python
# Razorpay Configuration
RAZORPAY_KEY_ID = 'your_razorpay_key_id'
RAZORPAY_KEY_SECRET = 'your_razorpay_key_secret'
```

**To get your Razorpay credentials:**
1. Sign up at https://razorpay.com
2. Go to Settings → API Keys
3. Copy your Key ID and Key Secret

### Step 3: Create Migrations
```bash
python manage.py makemigrations events
python manage.py migrate events
```

### Step 4: Create Media Directory for Tickets
```bash
mkdir media/tickets/
```

## How It Works

### Payment Flow
1. User clicks "Register" on an event
2. User selects ticket quantity and proceeds to checkout
3. On checkout page, user selects payment method
4. User clicks "Pay" button
5. Razorpay modal opens with payment form
6. User completes payment
7. Frontend verifies payment with backend
8. If successful, ticket is generated with QR code
9. User is redirected to ticket display page

### Ticket Generation Process
1. After successful payment verification
2. `generate_ticket()` function creates:
   - Unique ticket ID (format: event-id-user-id-random)
   - QR code containing ticket ID
   - Ticket database record
3. User can view ticket with QR code
4. User can print ticket for event entry

## Testing

### Test Razorpay Credentials
For testing purposes, use Razorpay's test mode:

Test Card Details:
- Card Number: 4111 1111 1111 1111
- Expiry: Any future date (MM/YY)
- CVV: Any 3 digits

Test UPI:
- Any VPA will work in test mode (e.g., success@razorpay)

### Test Payment Flow
1. Create a test event with price > 0
2. Add to cart and proceed to checkout
3. Use test credentials above
4. Complete payment
5. Verify ticket is generated and displayed

## Database Fields

### EventRegistration Model Updates
```python
payment_status = CharField(
    choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded')
    ],
    default='Pending'
)
razorpay_order_id = CharField(max_length=255, blank=True, null=True)
razorpay_payment_id = CharField(max_length=255, blank=True, null=True)
```

### Ticket Model
```python
class Ticket(models.Model):
    registration = OneToOneField(EventRegistration, ...)
    ticket_id = CharField(max_length=255, unique=True)
    qr_code = ImageField(upload_to='tickets/')
    created_at = DateTimeField(auto_now_add=True)
```

## Security Considerations

✅ **Implemented:**
- CSRF protection on all forms
- Payment verification on backend
- User ownership validation on ticket view
- Payment amount verification
- Signature verification with Razorpay secret key

**Additional Security for Production:**
1. Use environment variables for API keys (not hardcoded)
2. Enable HTTPS only
3. Implement rate limiting on payment endpoints
4. Add logging for all payments
5. Implement webhook for Razorpay payment updates
6. Add email confirmation with ticket attachment

## Customization Options

### 1. Customize Ticket QR Code
Edit in `generate_ticket()` function:
```python
qr = qrcode.QRCode(
    version=1,  # Size of QR code
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,  # Pixel size
    border=4,  # Border size
)
```

### 2. Customize Ticket Appearance
Edit `templates/ticket.html`:
- Change colors in `.ticket-card` CSS
- Modify layout and information displayed
- Add your branding/logo

### 3. Add Refund Functionality
Create a refund view:
```python
@login_required
def refund_ticket(request, registration_id):
    # Implement Razorpay refund API
    # Update payment_status to 'Refunded'
    # Send email confirmation
```

### 4. Generate PDF Tickets
Install: `pip install reportlab`

```python
def generate_pdf_ticket(registration):
    # Use reportlab to create PDF
    # Include QR code, event details
    # Return downloadable PDF
```

## Troubleshooting

### Issue: Payment verification fails
- ✅ Check Razorpay API credentials are correct
- ✅ Verify payment amount is correct (in paise)
- ✅ Check order_id matches between front and backend

### Issue: QR code not generating
- ✅ Ensure `qrcode` and `pillow` packages are installed
- ✅ Check `media/tickets/` directory exists and is writable
- ✅ Check Django MEDIA_ROOT setting is correct

### Issue: Ticket not showing
- ✅ Verify payment_status is 'Completed' in database
- ✅ Check user ownership validation
- ✅ Clear browser cache

### Issue: "Unable to import" Razorpay
- ✅ `pip install razorpay` in your virtual environment
- ✅ Verify package is in `requirements.txt`

## Next Steps (Optional Enhancements)

1. **Email Notifications**
   - Send ticket via email after purchase
   - Send event reminder before date

2. **Analytics**
   - Track payment success rates
   - Monitor popular events
   - Revenue reports

3. **Refunds**
   - Implement refund functionality
   - Track refund status

4. **Admin Dashboard**
   - View payment analytics
   - Export payment reports
   - Manual refund processing

5. **Webhooks**
   - Implement Razorpay webhooks for real-time updates
   - Handle payment failures asynchronously

6. **Group Tickets**
   - Allow users to manage multiple tickets
   - Generate group tickets

## Support

For Razorpay integration support:
- Documentation: https://razorpay.com/docs/api/
- API Reference: https://razorpay.com/docs/payments/

For ticket generation:
- QRCode library: https://github.com/lincolnloop/python-qrcode
- Pillow documentation: https://python-pillow.org/

---

**Setup Complete!** Your payment gateway is now ready. Test with the provided test credentials and deploy with your actual credentials.

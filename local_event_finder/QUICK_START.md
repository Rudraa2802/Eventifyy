# Quick Start Guide

## 1. Install Required Packages

Open PowerShell/Terminal in your project directory and run:

```bash
pip install razorpay qrcode[pil] pillow
```

## 2. Get Razorpay API Keys

1. Go to https://razorpay.com
2. Sign up or login
3. Go to Settings → API Keys
4. Copy your test keys

## 3. Configure Settings

Edit `local_event_finder/settings.py` (around line 127):

Find this section:
```python
RAZORPAY_KEY_ID = 'your_razorpay_key_id_here'
RAZORPAY_KEY_SECRET = 'your_razorpay_key_secret_here'
```

Replace with your actual test keys:
```python
RAZORPAY_KEY_ID = 'rzp_test_xxxxxxxxxxxx'
RAZORPAY_KEY_SECRET = 'bxxxxxxxxxxxxxxxxxx'
```

## 4. Run Migrations

In your project directory, run:

```bash
python manage.py makemigrations events
python manage.py migrate events
```

You should see output like:
```
Migrations for 'events':
  events/migrations/0008_*.py
    - Add field payment_status to eventregistration
    - Add field razorpay_order_id to eventregistration
    - Add field razorpay_payment_id to eventregistration
    - Create model Ticket
```

Then:
```
Running migrations:
  Applying events.0008_* ... OK
```

## 5. Create Media Tickets Directory

```bash
mkdir media/tickets
```

Or in Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Path media/tickets -Force
```

## 6. Start Server

```bash
python manage.py runserver
```

## 7. Test Payment Flow

1. Create a test event with price (e.g., ₹100)
2. Login with test user
3. Click "Register" on the event
4. Click "Proceed to Payment"
5. Select "Credit Card" as payment method
6. Click "Pay & Register"
7. Use test card: **4111 1111 1111 1111** (any future date, any CVV)
8. Complete payment
9. View your ticket with QR code!

## Common Issues

**Error: "No module named 'razorpay'"**
→ Run: `pip install razorpay`

**Error: "Migration errors"**
→ Run: 
```bash
python manage.py makemigrations
python manage.py migrate
```

**Error: "Media directory not found"**
→ Create `media/tickets/` folder manually

## Test Razorpay Credentials

**Credit Card:**
- Number: 4111 1111 1111 1111
- Expiry: Any future month/year (e.g., 12/25)
- CVV: Any 3 digits (e.g., 123)

**Debit Card:**
- Number: 5104 0600 0000 0008
- Same expiry and CVV format

**UPI:**
- Any VPA will work in test mode
- Example: success@razorpay

## Files Changed

✅ `events/models.py` - Added payment fields and Ticket model
✅ `events/views.py` - Added payment and ticket views
✅ `events/urls.py` - Added new URL routes
✅ `local_event_finder/settings.py` - Added Razorpay config
✅ `templates/checkout.html` - Updated with Razorpay form
✅ `templates/ticket.html` - New ticket display page
✅ `templates/dashboard.html` - Added View Ticket button

## Next: Run Migration

👉 Run these commands in order:

```bash
python manage.py makemigrations events
python manage.py migrate events
python manage.py runserver
```

Then open: http://localhost:8000

Enjoy! 🎉

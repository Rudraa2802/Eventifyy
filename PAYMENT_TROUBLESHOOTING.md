# Payment Gateway Troubleshooting Guide

## Issues Fixed ✅

The following issues have been corrected:

1. **Amount Calculation Bug** - Fixed incorrect paise conversion
   - Before: `{{ total_price|add:"00"|stringformat:"d" }}` (wrong)
   - After: `Math.round({{ total_price }} * 100)` (correct)

2. **Error Handling** - Improved payment verification error messages
   - Added better exception handling
   - Clear error messages for missing fields
   - Validation for payment method selection

3. **Ticket Admin** - Added Ticket model to Django admin for debugging

---

## Testing Checklist

### ✅ Step 1: Install Dependencies
```powershell
pip install razorpay qrcode[pil] pillow
```

### ✅ Step 2: Run Migrations
```powershell
python manage.py makemigrations events
python manage.py migrate events
```

### ✅ Step 3: Create Tickets Directory
```powershell
New-Item -ItemType Directory -Path media/tickets -Force
```

### ✅ Step 4: Verify Razorpay Keys
Check `local_event_finder/settings.py`:
```python
RAZORPAY_KEY_ID = 'rzp_test_STzWjB52P2T1SF'
RAZORPAY_KEY_SECRET = 'mhx8dM3vAktFFPBJFLA3vfpoe'
```
Keys look configured ✓

### ✅ Step 5: Test Payment Flow

**1. Start server:**
```powershell
python manage.py runserver
```

**2. Create test event:**
- Login with existing account
- Go to Admin Dashboard → Add Event
- Set price to ₹100 or more
- Save event

**3. Register for event:**
- Go back to Home
- Find your event
- Click Register
- Select ticket quantity (e.g., 1)
- Click "Proceed to Checkout"

**4. Select payment method:**
- Select any payment method (Credit Card, UPI, etc.)
- Click "Proceed to Payment"

**5. Pay with test card:**
- Razorpay modal should open
- Use test card: **4111 1111 1111 1111**
- Expiry: Any future date (e.g., 12/25)
- CVV: Any 3 digits (e.g., 123)
- Click Pay

**6. Check ticket:**
- You should see success message
- Ticket page with QR code should appear
- Go to Dashboard → Your registration should show "View Ticket" button

---

## Common Issues & Solutions

### Issue 1: "Razorpay is not defined"
**Cause:** Razorpay SDK not loading  
**Fix:**
- Open browser DevTools (F12)
- Go to Console tab
- Check for red errors about `checkout.razorpay.com`
- Ensure you have internet connection
- Clear browser cache and reload

### Issue 2: "Missing payment details" or "Invalid request format"
**Cause:** Payment data not being sent correctly  
**Fix:**
- Open DevTools → Network tab
- Try payment again
- Look for `verify_payment` POST request
- Check if request shows payment data

### Issue 3: "Payment verification failed"
**Cause:** Signature verification failed  
**Fix:**
- Check Razorpay keys are correct in `settings.py`
- Check amount calculation (should be in paise)
- Try test credentials again
- Check server logs for detailed error

### Issue 4: "QR code not generating"
**Cause:** PIL/Pillow issue  
**Fix:**
```powershell
pip install --upgrade pillow
```
- Restart server
- Try payment again

### Issue 5: "Ticket not showing after payment"
**Cause:** Payment verified but ticket not generated  
**Fix:**
- Check `media/tickets/` directory exists
- Go to Django admin → Tickets
- Check if ticket record exists
- Check logs for errors during QR generation

---

## Debug Mode: Checking Logs

### In Terminal/PowerShell:
When you run `python manage.py runserver`, watch for errors:

```
[22/Mar/2026 12:34:56] "POST /payment/verify/ HTTP/1.1" 200 OK
```

If you see errors, they'll be printed above this line.

### In Django Admin:
1. Go to `http://localhost:8000/admin`
2. Login with superuser account
3. Check these sections:
   - **Events** - Your test event exists?
   - **Event Registrations** - Registration created with "Pending" status?
   - **Tickets** - Ticket created after payment?

---

## Manual Testing in Django Shell

```powershell
python manage.py shell
```

Then run:
```python
# Check if Razorpay is working
from events.views import generate_ticket
from events.models import EventRegistration

# Get your pending registration
reg = EventRegistration.objects.filter(payment_status='Pending').first()
print(f"Registration: {reg}")

# Try generating ticket manually
if reg:
    generate_ticket(reg)
    print("Ticket generated!")
```

Exit with `exit()`

---

## What to Check in settings.py

Make sure these are configured:

```python
# Line ~125-130
RAZORPAY_KEY_ID = 'rzp_test_STzWjB52P2T1SF'
RAZORPAY_KEY_SECRET = 'mhx8dM3vAktFFPBJFLA3vfpoe'

# Line ~120
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## Browser Console Check

Open DevTools (F12 or Right-Click → Inspect):

1. **Console tab:** Any red errors?
2. **Network tab:** 
   - Look for `checkout.razorpay.com` - should load successfully
   - Look for `verify_payment` - should return JSON with status
3. **Storage tab:**
   - Application → Cookies
   - Look for `csrftoken` - important for CSRF protection

---

## Test Razorpay Credentials (All Modes)

### Credit Card - Success
- Number: `4111 1111 1111 1111`
- Expiry: `any future date`
- CVV: `any 3 digits`
- Result: ✅ Payment successful

### Credit Card - Failure
- Number: `4000 0000 0000 0002`
- Any expiry/CVV
- Result: ❌ Payment fails (test declined card)

### UPI - Success
- Any VPA (e.g., `success@razorpay`)
- Result: ✅ Payment successful

### Netbanking
- Select any bank
- Result: ✅ Simulates bank payment

---

## Still Having Issues?

### Check these files were modified:
- ✅ `checkout.html` - Has Razorpay SDK and fixed amount calculation
- ✅ `views.py` - Has improved error handling
- ✅ `admin.py` - Has Ticket model registered
- ✅ `settings.py` - Has Razorpay keys

### Run migrations again:
```powershell
python manage.py migrate events
```

### Clear Django cache:
```powershell
python manage.py migrate events --fake-initial
```

### Reset database (CAREFUL - deletes all data):
```powershell
Remove-Item db.sqlite3
python manage.py migrate events
```

---

## Expected Database State After Successful Payment

After completing a payment:

1. **EventRegistration record:**
   - `payment_status` = "Completed"
   - `razorpay_order_id` = populated
   - `razorpay_payment_id` = populated

2. **Ticket record:**
   - `ticket_id` = unique identifier
   - `qr_code` = image file in `media/tickets/`
   - `created_at` = timestamp

3. **File system:**
   - `media/tickets/ticket_<id>.png` = QR code image

---

**Let me know if you encounter any specific errors!** 🎉

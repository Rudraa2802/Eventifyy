# Authentication Failed - Razorpay Payment Debugging Guide

## 🔴 **Authentication Failed Error**

This error typically means your **Razorpay API keys are invalid or incorrect**.

---

## ✅ **Step 1: Check Your Razorpay Keys**

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Login to your account
3. Go to **Settings → API Keys**
4. You should see:
   - **Key ID** (starts with `rzp_test_` or `rzp_live_`)
   - **Key Secret** (starts with several characters)

---

## ✅ **Step 2: Validate Current Keys in settings.py**

Open `local_event_finder/settings.py` and check line 126-127:

```python
RAZORPAY_KEY_ID = 'rzp_test_STzWjB52P2T1SF'
RAZORPAY_KEY_SECRET = 'mhx8dM3vAktFFPBJFLA3vfpoe'
```

**Issues to check:**
- ❌ Keys start with wrong prefix (should start with `rzp_test_` for testing)
- ❌ Keys are copied from wrong environment (live vs test)
- ❌ Keys have extra spaces or were truncated
- ❌ Keys are for a different Razorpay account

---

## ✅ **Step 3: Update Keys (If Needed)**

1. Copy your **Key ID** from Razorpay Dashboard
2. Copy your **Key Secret** from Razorpay Dashboard
3. Edit `settings.py` and replace:

```python
RAZORPAY_KEY_ID = 'your_new_key_id_here'
RAZORPAY_KEY_SECRET = 'your_new_key_secret_here'
```

Example:
```python
RAZORPAY_KEY_ID = 'rzp_test_abc123xyz456'
RAZORPAY_KEY_SECRET = 'abc123def456ghi789'
```

---

## ✅ **Step 4: Restart Server**

After updating keys, restart your Django server:

```powershell
# Stop current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

---

## 🧪 **Step 5: Test Payment with Browser Console**

1. Go to your event checkout page
2. Press **F12** to open Developer Tools
3. Select **Console** tab
4. Try payment again
5. **Look for console messages** - you'll see:
   - ✅ `Payment Response:` - Shows Razorpay response
   - ✅ `Payment Data being sent:` - Shows data sent to verify
   - ✅ `Response data:` - Shows backend response

**Example of successful flow:**
```
Payment Response: {razorpay_payment_id: "pay_abc123", razorpay_order_id: "order_xyz789", razorpay_signature: "sig_abc123"}
Payment Data being sent: {razorpay_payment_id: "pay_abc123", ...}
Response status: 200
Response data: {status: "success", message: "Payment verified successfully", ticket_id: "EVT-1-5-A2F9K"}
```

**Example of authentication failure:**
```
Response status: 400
Response data: {status: "error", message: "Payment signature verification failed. Please ensure API keys are correct."}
```

---

## 🐛 **Step 6: Check Server Console Errors**

While testing, watch your PowerShell/Terminal where Django is running.

Look for error messages like:
```
Razorpay Bad Request: Invalid API Key
Signature verification failed: ...
```

---

## 🔍 **Common Authentication Errors & Fixes**

### Error 1: "Invalid API Key ID"
**Cause:** RAZORPAY_KEY_ID is incorrect  
**Fix:**
- Copy Key ID again from Razorpay Dashboard
- Ensure there are no extra spaces
- Restart server

### Error 2: "Invalid API Key Secret"
**Cause:** RAZORPAY_KEY_SECRET is incorrect  
**Fix:**
- Copy Key Secret again from Razorpay Dashboard
- Ensure full length is copied (usually 40+ characters)
- Restart server

### Error 3: "Razorpay credentials not configured"
**Cause:** Settings don't have both keys  
**Fix:**
- Verify both RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET exist
- Check they're not set to empty strings or 'None'

### Error 4: "Payment signature verification failed"
**Cause:** Keys don't match order created with  
**Fix:**
- Make sure you're using TEST mode (keys start with `rzp_test_`)
- Create a new order (don't reuse old pending orders)
- Restart server after updating keys

### Error 5: "Razorpay is not defined"
**Cause:** Razorpay SDK not loading  
**Fix:**
- Check internet connection
- Check if `https://checkout.razorpay.com/v1/checkout.js` is loading
- In DevTools → Network → Search for "checkout.razorpay.com"
- Should see a **200 status** response

---

## 🧬 **How to Get Fresh Razorpay Keys**

If your keys seem corrupted or invalid:

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Settings → API Keys
3. Click **Regenerate Key** (this invalidates old keys)
4. Copy the new Key ID and Secret
5. Update `settings.py`
6. Restart server

---

## 📋 **Verification Checklist**

Before testing payment, verify:

- [ ] Razorpay account created at https://razorpay.com
- [ ] Test mode keys generated in Dashboard
- [ ] Key ID copied (starts with `rzp_test_`)
- [ ] Key Secret copied (40+ characters)
- [ ] Both keys pasted in `settings.py` (no extra spaces)
- [ ] Server restarted after updating keys
- [ ] Tested event has price > ₹0
- [ ] Payment method selected before clicking pay
- [ ] Using test card: `4111 1111 1111 1111`

---

## 🚀 **Test Payment Flow**

1. **Create paid event** (₹100 or more)
2. **Login & register** for event
3. **Go to checkout**
4. **Select payment method** (Credit Card)
5. **Click "Pay & Register"**
6. **Use test card:**
   - Number: `4111 1111 1111 1111`
   - Expiry: Any future date (e.g., 12/25)
   - CVV: Any 3 digits (e.g., 123)
7. **Check console** (F12) for success/error messages
8. **Look at server terminal** for debug logs

---

## 🆘 **Still Getting Authentication Failed?**

### Option 1: Check Razorpay Account Status
Go to [Razorpay Dashboard](https://dashboard.razorpay.com) and verify:
- ✅ Account is active
- ✅ Test mode is enabled (blue toggle at top)
- ✅ Keys are visible (not hidden)

### Option 2: Generate New Keys
1. Settings → API Keys
2. Click "Regenerate"
3. Copy fresh keys
4. Update `settings.py`
5. Restart server

### Option 3: Manual Verification (for debugging)

Create a test script to verify keys work:

Create file: `test_razorpay.py` in project root:

```python
import razorpay
from local_event_finder.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

try:
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    
    # Try to create an order
    order = client.order.create({
        'amount': 10000,  # ₹100
        'currency': 'INR',
        'receipt': 'test_order_001'
    })
    
    print("✅ Authentication successful!")
    print(f"Order created: {order['id']}")
    
except Exception as e:
    print(f"❌ Authentication failed: {str(e)}")
```

Run it:
```powershell
python test_razorpay.py
```

---

## 📸 **Where to Find Keys in Razorpay Dashboard**

1. Log in to https://dashboard.razorpay.com
2. Top bar: Click your profile icon → **Settings**
3. Left sidebar: Click **API Keys**
4. You'll see:
   ```
   Test Mode
   Key ID: rzp_test_xxxxxxxxxxxx (copy this)
   Key Secret: xxxxxxxxxxxxxxxx (copy this)
   ```

---

## ✅ **Final Steps**

1. **Copy your actual Razorpay keys** from your account
2. **Update `settings.py`** with your keys
3. **Restart server**: `python manage.py runserver`
4. **Test payment** with card: `4111 1111 1111 1111`
5. **Open DevTools (F12)** to see debugging messages
6. **Share the error message** from console if still failing

Good luck! 🎉

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CustomUser, Category, Event, EventRegistration, Ticket
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
import uuid
from django.conf import settings
from io import BytesIO
import qrcode
from django.core.files import File

def home(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    
    if query:
        events = events.filter(Q(title__icontains=query) | Q(location__icontains=query))
    if category_id:
        events = events.filter(category_id=category_id)
        
    categories = Category.objects.all()
    return render(request, 'home.html', {'events': events, 'categories': categories})

def event_list(request):
    return redirect('home')

def event_details(request, id):
    event = get_object_or_404(Event, id=id)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(user=request.user, event=event).exists()
    return render(request, 'event_details.html', {'event': event, 'is_registered': is_registered})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        e = request.POST.get('email')
        phone = request.POST.get('phone')
        age_str = request.POST.get('age')
        
        try:
            age = int(age_str)
        except (ValueError, TypeError):
            age = 0
            
        if age < 18:
            messages.error(request, 'You must be at least 18 years old to register on Local Event Finder.')
            return render(request, 'register.html')
            
        if CustomUser.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = CustomUser.objects.create_user(username=u, email=e, password=p, phone=phone, age=age)
            login(request, user)
            return redirect('home')
    return render(request, 'register.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', request.user.email)
        request.user.phone = request.POST.get('phone', '')
        
        # We generally do not let them change age to bypass restrictions later easily, 
        # but if we do, we could enforce an update check here too.
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')
        
    return render(request, 'edit_profile.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def add_event(request):
    # Only superusers can create events
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to create events.")
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        cat_id = request.POST.get('category')
        date = request.POST.get('date')
        location = request.POST.get('location')
        price = request.POST.get('price', 0.00)
        capacity = int(request.POST.get('capacity', 0))
        image = request.FILES.get('image')
        
        category = get_object_or_404(Category, id=cat_id)
        Event.objects.create(
            title=title, description=desc, category=category,
            date=date, location=location, price=price, capacity=capacity,
            image=image, organizer=request.user
        )
        messages.success(request, 'Event added successfully!')
        return redirect('admin_dashboard')
        
    categories = Category.objects.all()
    return render(request, 'add_event.html', {'categories': categories})

@login_required
def edit_event(request, id):
    event = get_object_or_404(Event, id=id)
    # Only superusers can edit events
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit events.")
        return redirect('home')
        
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        cat_id = request.POST.get('category')
        event.category = get_object_or_404(Category, id=cat_id)
        event.date = request.POST.get('date')
        event.location = request.POST.get('location')
        event.price = request.POST.get('price', event.price)
        event.capacity = int(request.POST.get('capacity', event.capacity))
        if request.FILES.get('image'):
            event.image = request.FILES.get('image')
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('admin_dashboard')
        
    categories = Category.objects.all()
    return render(request, 'edit_event.html', {'event': event, 'categories': categories})

@login_required
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    # Only superusers can delete events
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete events.")
        return redirect('home')
    event.delete()
    messages.success(request, 'Event deleted.')
    return redirect('admin_dashboard')

@login_required
def checkout(request, id):
    event = get_object_or_404(Event, id=id)
    if EventRegistration.objects.filter(user=request.user, event=event).exists():
        messages.info(request, f'You are already registered for {event.title}.')
        return redirect('dashboard')
        
    quantity = int(request.GET.get('quantity', 1))
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

    if event.capacity > 0 and event.total_tickets_sold + quantity > event.capacity:
        messages.error(request, f'Sorry, {event.title} does not have enough capacity for {quantity} tickets.')
        return redirect('event_details', id=event.id)
        
    # If the event is free, skip checkout
    if event.price <= 0:
        return redirect('register_event', id=event.id)
        
    total_price = event.price * quantity
        
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', '').strip()
        
        # Validate payment method is selected
        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return render(request, 'checkout.html', {
                'event': event, 
                'quantity': quantity, 
                'total_price': total_price
            })
        
        # Create EventRegistration with pending status
        registration = EventRegistration.objects.create(
            user=request.user, 
            event=event, 
            payment_method=payment_method, 
            amount_paid=total_price,
            ticket_quantity=quantity,
            payment_status='Pending'
        )
        
        # Initiate Razorpay payment
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            order_data = {
                'amount': int(total_price * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': f'order_{registration.id}',
                'payment_capture': 1
            }
            
            razorpay_order = client.order.create(data=order_data)
            registration.razorpay_order_id = razorpay_order['id']
            registration.save()
            
            context = {
                'event': event,
                'quantity': quantity,
                'total_price': total_price,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'registration_id': registration.id,
                'user_email': request.user.email,
                'user_phone': request.user.phone or '',
            }
            
            return render(request, 'checkout.html', context)
        
        except Exception as e:
            # Delete registration if order creation fails
            registration.delete()
            messages.error(request, f'Payment setup failed. Please try again. Error: {str(e)}')
            return redirect('event_details', id=event.id)
        
    return render(request, 'checkout.html', {'event': event, 'quantity': quantity, 'total_price': total_price})

@login_required
def register_event(request, id):
    event = get_object_or_404(Event, id=id)
    quantity = int(request.POST.get('quantity', 1) if request.method == 'POST' else request.GET.get('quantity', 1))
    
    if event.capacity > 0 and event.total_tickets_sold + quantity > event.capacity:
        # Prevent registration if they aren't already registered
        if not EventRegistration.objects.filter(user=request.user, event=event).exists():
            messages.error(request, f'Sorry, {event.title} does not have enough capacity for {quantity} tickets.')
            return redirect('event_details', id=event.id)
            
    if event.price > 0:
        return redirect(f"/checkout/{event.id}/?quantity={quantity}")
    
    # For free events, create registration and generate ticket
    registration, created = EventRegistration.objects.get_or_create(
        user=request.user, 
        event=event, 
        defaults={
            'payment_method': 'Free', 
            'amount_paid': 0.00, 
            'ticket_quantity': quantity,
            'payment_status': 'Completed'  # Mark as completed for free events
        }
    )
    
    # Generate ticket for free event registration
    if created:
        try:
            generate_ticket(registration)
            messages.success(request, f'Successfully registered for {event.title}! Your ticket is ready.')
        except Exception as e:
            messages.success(request, f'Successfully registered for {event.title}!')
            print(f"Ticket generation error: {str(e)}")
    else:
        messages.info(request, f'You are already registered for {event.title}.')
    
    return redirect('dashboard')

@login_required
def cancel_registration(request, id):
    event = get_object_or_404(Event, id=id)
    EventRegistration.objects.filter(user=request.user, event=event).delete()
    messages.info(request, f'Registration cancelled for {event.title}.')
    return redirect('dashboard')

@login_required
def dashboard(request):
    registrations = EventRegistration.objects.filter(user=request.user).select_related('event')
    return render(request, 'dashboard.html', {'registrations': registrations})

@login_required
def admin_dashboard(request):
    # Only superusers can access the admin dashboard
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to access the admin dashboard.")
        return redirect('home')
    
    events = Event.objects.all()
    return render(request, 'admin_dashboard.html', {'events': events})

@login_required
def event_registrations(request, id):
    event = get_object_or_404(Event, id=id)
    # Only superusers can view attendees
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')
        
    registrations = EventRegistration.objects.filter(event=event).select_related('user').order_by('-registration_date')
    return render(request, 'event_registrations.html', {'event': event, 'registrations': registrations})

@login_required
def submit_feedback(request):
    from .forms import FeedbackForm
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you! Your feedback has been submitted successfully.')
            return redirect('home')
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})

@login_required
def view_feedbacks(request):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')
        
    from .models import Feedback
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'admin_feedback.html', {'feedbacks': feedbacks})


@csrf_exempt
def verify_payment(request):
    """Verify Razorpay payment and create ticket"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request format'
            }, status=400)
        
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        registration_id = data.get('registration_id')
        
        # Validate required fields
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature, registration_id]):
            missing = []
            if not razorpay_payment_id:
                missing.append('payment_id')
            if not razorpay_order_id:
                missing.append('order_id')
            if not razorpay_signature:
                missing.append('signature')
            if not registration_id:
                missing.append('registration_id')
            
            return JsonResponse({
                'status': 'error',
                'message': f'Missing payment details: {", ".join(missing)}'
            }, status=400)
        
        try:
            registration = EventRegistration.objects.get(id=registration_id)
        except EventRegistration.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Registration not found'
            }, status=404)
        
        try:
            # Validate Razorpay keys exist
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Razorpay credentials not configured. Contact administrator.'
                }, status=500)
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify signature
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
            except razorpay.errors.SignatureVerificationError as sig_error:
                print(f"Signature verification failed: {str(sig_error)}")
                registration.payment_status = 'Failed'
                registration.save()
                return JsonResponse({
                    'status': 'error',
                    'message': f'Payment signature verification failed. Please ensure API keys are correct.'
                }, status=400)
            
            # Payment verified successfully
            registration.payment_status = 'Completed'
            registration.razorpay_payment_id = razorpay_payment_id
            registration.save()
            
            # Generate ticket
            generate_ticket(registration)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment verified successfully',
                'ticket_id': registration.ticket.ticket_id
            })
            
        except razorpay.errors.BadRequestError as e:
            print(f"Razorpay Bad Request: {str(e)}")
            registration.payment_status = 'Failed'
            registration.save()
            return JsonResponse({
                'status': 'error',
                'message': f'Razorpay error: Invalid request. Check API keys.'
            }, status=400)
        
        except Exception as e:
            registration.payment_status = 'Failed'
            registration.save()
            import traceback
            error_details = traceback.format_exc()
            print(f"Payment verification error: {str(e)}")
            print(error_details)
            return JsonResponse({
                'status': 'error',
                'message': f'Payment verification failed: {str(e)}'
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def generate_ticket(registration):
    """Generate QR code and create ticket"""
    # Check if ticket already exists
    if hasattr(registration, 'ticket'):
        return registration.ticket
    
    # Generate unique ticket ID
    ticket_id = f"{registration.event.id}-{registration.user.id}-{uuid.uuid4().hex[:8].upper()}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(ticket_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to BytesIO object
    file_buffer = BytesIO()
    img.save(file_buffer, format='PNG')
    file_buffer.seek(0)
    
    # Create Ticket object
    ticket = Ticket.objects.create(
        registration=registration,
        ticket_id=ticket_id
    )
    
    # Save QR code image
    ticket.qr_code.save(
        f'ticket_{ticket_id}.png',
        File(file_buffer),
        save=True
    )
    
    return ticket


@login_required
def view_ticket(request, registration_id):
    """Display ticket for a registration"""
    registration = get_object_or_404(EventRegistration, id=registration_id)
    
    # Verify the user owns this registration
    if registration.user != request.user:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect('dashboard')
    
    # Check if ticket exists
    if not hasattr(registration, 'ticket'):
        messages.error(request, "Ticket not available yet.")
        return redirect('dashboard')
    
    ticket = registration.ticket
    context = {
        'registration': registration,
        'ticket': ticket,
        'event': registration.event,
    }
    
    return render(request, 'ticket.html', context)


@login_required
def download_ticket(request, ticket_id):
    """Download ticket as PDF (optional)"""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    registration = ticket.registration
    
    # Verify the user owns this ticket
    if registration.user != request.user:
        messages.error(request, "You do not have permission to download this ticket.")
        return redirect('dashboard')
    
    # For now, redirect to view ticket
    # You can enhance this to generate a PDF using reportlab or similar
    return redirect('view_ticket', registration_id=registration.id)

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    is_organizer = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    capacity = models.PositiveIntegerField(default=0, help_text="0 means unlimited capacity")
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organized_events')

    def __str__(self):
        return self.title

    @property
    def total_tickets_sold(self):
        from django.db.models import Sum
        return self.registrations.aggregate(total=Sum('ticket_quantity'))['total'] or 0

class EventRegistration(models.Model):
    PAYMENT_CHOICES = (
        ('Free', 'Free'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking')
    )
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded')
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Free')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ticket_quantity = models.PositiveIntegerField(default=1)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Ticket(models.Model):
    registration = models.OneToOneField(EventRegistration, on_delete=models.CASCADE, related_name='ticket')
    ticket_id = models.CharField(max_length=255, unique=True)
    qr_code = models.ImageField(upload_to='tickets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ticket {self.ticket_id}"

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedback')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} - {self.subject}"

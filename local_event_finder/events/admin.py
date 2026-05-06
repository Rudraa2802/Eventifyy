from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Event, EventRegistration, Feedback, Ticket

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Category)
admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(Feedback)
admin.site.register(Ticket)

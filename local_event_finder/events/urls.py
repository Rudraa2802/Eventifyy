from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('events/', views.event_list, name='event_list'),
    path('event/<int:id>/', views.event_details, name='event_details'),
    path('event/add/', views.add_event, name='add_event'),
    path('event/<int:id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:id>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:id>/checkout/', views.checkout, name='checkout'),
    path('event/<int:id>/register/', views.register_event, name='register_event'),
    path('event/<int:id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('event/<int:id>/attendees/', views.event_registrations, name='event_registrations'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('admin-feedback/', views.view_feedbacks, name='view_feedbacks'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('ticket/<int:registration_id>/', views.view_ticket, name='view_ticket'),
    path('ticket/<ticket_id>/download/', views.download_ticket, name='download_ticket'),
]

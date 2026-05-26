from django.urls import path
from .import views

urlpatterns = [
    # Core Pages
    path('', views.index, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('training/', views.training, name='training'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('training/enroll/<slug:slug>/', views.enroll_training, name='enroll_training'),
    path('booking/reschedule/<int:booking_id>/', views.reschedule_booking, name='reschedule_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('pay/<int:booking_id>/', views.dummy_payment, name='dummy_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),  
    path("checkout/<int:booking_id>/", views.checkout, name="checkout"),
    


    # Services Pages
    path('apply/', views.jobconsultation_view, name='apply'),
    path('appointments/', views.appointments, name='appointments'),
    path('booking/', views.booking, name='booking'),

    # Info Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]


    


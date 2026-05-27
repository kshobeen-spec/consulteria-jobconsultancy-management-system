from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking, Payment, Cancellation, TrainingProgram

from .models import Booking, Profile, UserProfile

import re
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
import io
import pdfplumber
import os
os.environ["PATH"] += r";C:\poppler\bin"

User = get_user_model()

# ---------------------------------------
# HOME
# ---------------------------------------
def index(request):
    return render(request, 'home/index.html')

# ---------------------------------------
# DASHBOARD
# ---------------------------------------
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Booking

@login_required
def dashboard(request):
    user_bookings = Booking.objects.filter(email=request.user.email).order_by('-submitted_at')

    total_bookings = user_bookings.count()
    upcoming = user_bookings.filter(date__gte=timezone.now().date())
    past = user_bookings.filter(date__lt=timezone.now().date())

    latest_booking = user_bookings.first()
    latest_score = latest_booking.ai_score if latest_booking else None

    payments = Payment.objects.filter(booking__email=request.user.email).order_by("-created_at")[:5]
    recent_cancellations = Cancellation.objects.filter(booking__email=request.user.email).order_by("-created_at")[:5]


    # average AI score
    scores = [b.ai_score for b in user_bookings if b.ai_score is not None]
    avg_score = sum(scores) / len(scores) if scores else None

    admin_notes = latest_booking.admin_notes if latest_booking else None
    context = {
        "user": request.user,
        "total_bookings": total_bookings,
        "upcoming": upcoming[:3],
        "past": past[:3],
        "latest_score": latest_score,
        "avg_score": avg_score,
        "latest_booking": latest_booking,
        "admin_notes": admin_notes,
        "payments": payments,
        "recent_cancellations": recent_cancellations,
    }

    return render(request, "dashboard/dashboard.html", context)

# ---------------------------------------
# TRAINING PAGE
# ---------------------------------------
def training(request):
    return render(request, 'training/training.html')

# ---------------------------------------
# PROFILE PAGE (FIXED)
# ---------------------------------------
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile/profile.html', {"profile": profile})

# ---------------------------------------
# EDIT PROFILE PAGE (FIXED)
# ---------------------------------------
@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user

        # Update main User fields
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        # Update Profile
        profile.phone = request.POST.get('phone')
        profile.bio = request.POST.get('bio')

        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')

        profile.save()
        return redirect('profile')

    return render(request, 'profile/edit_profile.html', {"profile": profile})


# ---------------------------------------
# APPLY PAGE
# ---------------------------------------
def jobconsultation_view(request):
    if request.method == 'POST':
        messages.success(request, "Application submitted!")
    return render(request, 'apply/apply_job.html')


# ---------------------------------------
# PDF TEXT EXTRACTION
# ---------------------------------------
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        if not text.strip():
            return "No text found in PDF."
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# ---------------------------------------
# SIMPLE AI RESUME SCREENING
# ---------------------------------------
def ai_screen_resume(text):
    txt = (text or "").lower()
    if not txt.strip():
        return 0.0, "No resume text could be extracted. Please upload a readable PDF."

    keywords = ['experience','skills','projects','education','python','javascript','lead','managed','developed','marketing','sales']
    kw_count = sum(1 for kw in keywords if kw in txt)
    word_count = len(re.findall(r'\w+', txt))
    experience_lines = sum(1 for line in txt.splitlines() if 'year' in line or 'years' in line or 'experience' in line)

    score = min(100, (kw_count * 8) + min(40, experience_lines * 8) + min(40, word_count // 50))

    feedback_parts = []
    if kw_count: feedback_parts.append(f"Keywords found: {kw_count}.")
    if experience_lines: feedback_parts.append(f"Experience lines: {experience_lines}.")
    feedback_parts.append(f"Word count: {word_count}.")
    if score > 70: feedback_parts.append("Strong resume.")
    elif score > 40: feedback_parts.append("Average resume — add more achievements.")
    else: feedback_parts.append("Weak resume — expand experience and skills.")

    return round(score, 1), " ".join(feedback_parts)


# ---------------------------------------
# BOOKING PAGE WITH AI SCREENING
# ---------------------------------------

# helper to send email (uses Django email settings)
def send_simple_email(subject, message, to_email):
    send_mail(subject, message, settings.EMAIL_HOST_USER, [to_email], fail_silently=True)

def booking(request):
    ai_result = None

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        date_str = request.POST.get('date')
        time_input = request.POST.get('time')
        resume_file = request.FILES.get("resume")

        booking_date = parse_date(date_str) if date_str else None

        if booking_date is None:
            return render(request, 'booking/booking.html', {'error': 'Please select a valid date.'})

        booking_obj = Booking.objects.create(
            full_name=name,
            email=email,
            phone=phone,
            date=booking_date,
            time=time_input,
            resume=resume_file
        )

        # process resume if uploaded
        if resume_file:
            try:
                resume_file.open()
            except Exception:
                pass

            text = extract_text_from_pdf(resume_file)
            score, feedback = ai_screen_resume(text)

            booking_obj.ai_feedback = feedback
            booking_obj.ai_score = score
            booking_obj.save()

            ai_result = {
                "score": score,
                "feedback": feedback,
                "text": text[:2000]
            }
        else:
            ai_result = {
                "score": None,
                "feedback": "No resume uploaded.",
                "text": ""
            }

        # send confirmation emails (safe, non-blocking)
        service = request.POST.get('service') or request.GET.get('service') or getattr(booking_obj, 'service', '')
        try:
            from django.conf import settings as _settings
            from django.core.mail import send_mail as _send_mail

            from_email = getattr(_settings, "DEFAULT_FROM_EMAIL", None) or getattr(_settings, "EMAIL_HOST_USER", None)
            if from_email and email:
                _send_mail(
                    "Booking Confirmation - Consulteria",
                    f"Hi {name},\n\nYour booking for {service} on {booking_obj.date} at {booking_obj.time} has been received. We'll contact you soon.\n\nThanks,\nConsulteria",
                    from_email,
                    [email],
                    fail_silently=True
                )

            # Admin alert
            admin_email = getattr(_settings, "EMAIL_HOST_USER", None)
            if admin_email:
                send_simple_email(
                    "New Booking Received",
                    f"New booking by {name} ({email}) for {service} on {booking_obj.date} at {booking_obj.time}.",
                    admin_email
                )
        except Exception:
            pass  # prevents app crash if email fails

        messages.success(request, "Booking saved successfully!")

        # Payment redirect
        return redirect("dummy_payment", booking_id=booking_obj.id)

    return render(request, 'booking/booking.html', {'ai_result': ai_result})


@login_required
def reschedule_booking(request, booking_id):
    booking_obj = get_object_or_404(Booking, id=booking_id, email=request.user.email)
    if request.method == "POST":
        date_str = request.POST.get("date")
        time_input = request.POST.get("time")
        reason = request.POST.get("reason", "")

        new_date = parse_date(date_str) if date_str else None
        if not new_date:
            messages.error(request, "Please provide a valid date.")
            return redirect("dashboard")

        # create a Cancellation entry with action Rescheduled
        Cancellation.objects.create(
            booking=booking_obj,
            action="Rescheduled",
            reason=reason,
            new_date=new_date,
            new_time=time_input
        )

        # update booking to the new schedule
        booking_obj.date = new_date
        booking_obj.time = time_input
        booking_obj.save()

        # email user + admin
        send_simple_email("Booking Rescheduled",
                          f"Your booking for {booking_obj.service} has been rescheduled to {new_date} at {time_input}.",
                          booking_obj.email)
        send_simple_email("Booking Rescheduled (admin)", f"Booking {booking_obj.id} rescheduled.", settings.EMAIL_HOST_USER)

        messages.success(request, "Booking rescheduled.")
        return redirect("dashboard")

    # GET: show a small reschedule form
    return render(request, "booking/reschedule.html", {"booking": booking_obj})

@login_required
def cancel_booking(request, booking_id):
    booking_obj = get_object_or_404(Booking, id=booking_id, email=request.user.email)
    if request.method == "POST":
        reason = request.POST.get("reason", "")
        Cancellation.objects.create(booking=booking_obj, action="Cancelled", reason=reason)
        # optionally keep booking record but notify admin
        send_simple_email("Booking Cancelled", f"{booking_obj.full_name} cancelled booking {booking_obj.id}.", settings.EMAIL_HOST_USER)
        messages.success(request, "Booking cancelled.")
        return redirect("dashboard")

    return render(request, "booking/cancel.html", {"booking": booking_obj})
def training(request):
    programs = TrainingProgram.objects.all().order_by("-created_at")
    return render(request, "training/training.html", {"programs": programs})

def enroll_training(request, slug):
    # redirect user to booking page with service prefilled as training program title
    program = get_object_or_404(TrainingProgram, slug=slug)
    # redirect to booking with service query param
    return redirect(f"{reverse('booking')}?service={program.title}")

@login_required
def dummy_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    # Always successful dummy payment
    payment = Payment.objects.create(
        booking=booking,  # your booking object
        amount=getattr(booking, "price", 0),  # or whatever amount you use
        status="Paid",
        provider_ref="DUMMY123",  # you can generate random ID if needed
        is_paid=True,
    )
    booking.is_paid = True
    booking.save()

    return redirect("checkout", booking_id=booking.id)


def payment_success(request):
    return render(request, "booking/payment_success.html")
    return redirect("consult_app:payment_success")


@login_required
def checkout(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)
    plans = [
        {"id": 1, "name": "Basic", "amount": 199, "desc": "1 session"},
        {"id": 2, "name": "Standard", "amount": 499, "desc": "3 sessions"},
        {"id": 3, "name": "Premium", "amount": 899, "desc": "Unlimited month"},
    ]

    if request.method == "POST":
        selected_plan_id = int(request.POST.get("plan_id"))
        plan = next(p for p in plans if p["id"] == selected_plan_id)

        # Create payment
        Payment.objects.create(
            booking=booking,
            amount=plan["amount"],
            status="Paid",
            provider_ref=f"DUMMY-{booking_id}-{plan['id']}",
            is_paid=True,
        )

        booking.is_paid = True
        booking.save()
        messages.success(request, f"Payment successful! You chose the {plan['name']} plan.")
        return redirect("payment_success")


    return render(request, "booking/checkout.html", {
        "booking": booking,
        "plans": plans
    })


# ---------------------------------------
# OTHER PAGES
# ---------------------------------------
def appointments(request):
    return render(request, 'appointments/appointments.html')

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    if request.method == 'POST':
        messages.success(request, "Message sent!")
    return render(request, 'pages/contact.html')



# ---------------------------------------
# AUTH — LOGIN
# ---------------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


# ---------------------------------------
# AUTH — SIGNUP
# ---------------------------------------
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password1)

        UserProfile.objects.create(user=user)

        messages.success(request, "Account created successfully!")
        auth_login(request, user)

        return redirect("dashboard")

    return render(request, "accounts/signup.html")


# ---------------------------------------
# AUTH — LOGOUT
# ---------------------------------------
def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookingForm
from .models import Booking
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from orders.models import Feedback
from orders.forms import FeedbackForm
from django.db.models import Avg



def home(request):
    return render(request, 'home.html')

def rooms(request):
    return render(request, 'rooms.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# Booking page
def booking_view(request):
    if request.method == "POST":
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save()
            
            # Send confirmation email
            send_mail(
                subject="Booking Confirmation",
                message=f"Hello {booking.name}, your booking is confirmed!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                fail_silently=False,
            )
            
            print("Booking saved:", booking)
            return render(request, 'booking_success.html')
        else:
            print("Form errors:", form.errors)
    else:
        form = BookingForm()

    return render(request, 'booking.html', {'form': form})

# Admin: Approve / Reject
def update_booking_status(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id)

    if action == "approve":
        booking.status = "APPROVED"
        subject = "Hotel Booking Approved"
        message = f"Dear {booking.name},\nYour booking for {booking.room_type} from {booking.check_in} to {booking.check_out} has been APPROVED."
    elif action == "reject":
        booking.status = "REJECTED"
        subject = "Hotel Booking Rejected"
        message = f"Dear {booking.name},\nYour booking for {booking.room_type} from {booking.check_in} to {booking.check_out} has been REJECTED."
    else:
        return redirect('admin-bookings')

    booking.save()

    # Send email
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [booking.email],
        fail_silently=False,
    )

    return redirect('admin-bookings')

# Admin: List all bookings
def admin_booking_list(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'admin_bookings.html', {'bookings': bookings})

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Booking

def owner_bookings(request):
    # 1️⃣ Get token from URL
    token = request.GET.get('token')

    # 2️⃣ Deny access if token is missing or incorrect
    if token != settings.OWNER_PAGE_TOKEN:
        return render(request, 'access_denied.html')  # create a simple access_denied.html

    # 3️⃣ Fetch all bookings
    bookings = Booking.objects.all().order_by('-created_at')

    # 4️⃣ Handle status update via POST
    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('status')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = new_status
        booking.save()
        return redirect(f'/owner/bookings/?token={token}')  # keep token in URL when redirecting

    # 5️⃣ Render page with bookings
    return render(request, 'owner_bookings.html', {'bookings': bookings})


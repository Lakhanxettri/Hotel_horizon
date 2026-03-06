from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookingForm
from .models import Booking
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from orders.models import Feedback, Order
from orders.forms import FeedbackForm
from django.db.models import Avg


# ==================== AUTH VIEWS ====================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validation
        if not username or not email or not password1:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, f'Welcome, {username}! Your account has been created.')
        return redirect('home')

    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to 'next' param if exists, else home
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ==================== PAGE VIEWS ====================

def home(request):
    return render(request, 'home.html')

def rooms(request):
    return render(request, 'rooms.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


# ==================== BOOKING VIEWS ====================

@login_required(login_url='login')
def booking_view(request):
    if request.method == "POST":
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # Auto-fill from user if fields empty
            if not booking.name or booking.name == "Guest":
                booking.name = request.user.get_full_name() or request.user.username
            if not booking.email or booking.email == "guest@example.com":
                booking.email = request.user.email
            booking.save()
            
            # Send confirmation email
            try:
                send_mail(
                    subject="Booking Confirmation",
                    message=f"Hello {booking.name}, your booking is confirmed!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            return render(request, 'booking_success.html')
        else:
            print("Form errors:", form.errors)
    else:
        # Pre-fill form with user data
        initial = {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = BookingForm(initial=initial)

    return render(request, 'booking.html', {'form': form})


@login_required(login_url='login')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


# ==================== ADMIN VIEWS ====================

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

    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [booking.email], fail_silently=True)
    except Exception:
        pass

    return redirect('admin-bookings')


def admin_booking_list(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'admin_bookings.html', {'bookings': bookings})


def owner_bookings(request):
    token = request.GET.get('token')

    if token != settings.OWNER_PAGE_TOKEN:
        return render(request, 'access_denied.html')

    bookings = Booking.objects.all().order_by('-created_at')

    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('status')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = new_status
        booking.save()
        return redirect(f'/owner/bookings/?token={token}')

    return render(request, 'owner_bookings.html', {'bookings': bookings})

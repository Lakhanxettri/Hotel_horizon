from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, MenuItem, Customer, Order, OrderItem, Review
from decimal import Decimal
from django.db import transaction
from django.conf import settings
import uuid
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Feedback
from django.db.models import Avg
from .forms import FeedbackForm
from django.contrib import messages


# ---------------- Menu Page ----------------
def menu_list(request):
    categories = Category.objects.prefetch_related('items').all()
    return render(request, 'menu.html', {'categories': categories})


# ---------------- Add to Cart (Bulk by Category) ----------------
def add_to_cart_bulk(request):
    if request.method == "POST":
        category_id = request.POST.get("category_id")
        cart = request.session.get('cart', {})

        items = MenuItem.objects.filter(category_id=category_id)

        for item in items:
            qty = request.POST.get(f"quantity_{item.id}")
            if qty and int(qty) > 0:
                cart[str(item.id)] = cart.get(str(item.id), 0) + int(qty)

        request.session['cart'] = cart

    return redirect("view_cart")


# ---------------- Add Single Item to Cart ----------------
def add_to_cart(request, item_id):
    if request.method == 'POST':
        qty = int(request.POST.get(f'quantity_{item_id}', 1))
        if qty < 1:
            qty = 1

        cart = request.session.get('cart', {})
        cart[str(item_id)] = cart.get(str(item_id), 0) + qty
        request.session['cart'] = cart

    return redirect('menu')


# ---------------- Remove Item from Cart ----------------
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
    request.session['cart'] = cart
    return redirect('view_cart')


# ---------------- View Cart ----------------
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    if cart:
        menu_items = MenuItem.objects.filter(id__in=cart.keys())
        for item in menu_items:
            qty = cart.get(str(item.id), 0)
            subtotal = item.price * qty
            total += subtotal
            items.append({'item': item, 'quantity': qty, 'subtotal': subtotal})

    return render(request, 'cart.html', {'items': items, 'total': total})


# ---------------- Checkout ----------------
@login_required(login_url='login')
@transaction.atomic
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('menu')

    if request.method == 'POST':
        name = request.POST.get('name', request.user.get_full_name() or request.user.username)
        email = request.POST.get('email', request.user.email)
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')

        # Create or get customer linked to user
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': phone, 'address': address}
        )
        # Link customer to user if not already
        if not customer.user:
            customer.user = request.user
            customer.save()

        # Create order linked to user
        total = Decimal('0.00')
        order = Order.objects.create(
            customer=customer,
            user=request.user,
            total_amount=0
        )

        menu_items = MenuItem.objects.filter(id__in=cart.keys())
        for item in menu_items:
            qty = cart.get(str(item.id), 0)
            subtotal = item.price * qty
            total += subtotal
            OrderItem.objects.create(
                order=order,
                menu_item=item,
                quantity=qty,
                price=item.price
            )

        order.total_amount = total
        order.save()

        # Clear cart
        request.session['cart'] = {}

        return redirect('order_success', order_id=order.id)

    # GET request: show checkout form
    items = []
    total = Decimal('0.00')
    menu_items = MenuItem.objects.filter(id__in=cart.keys())
    for item in menu_items:
        qty = cart.get(str(item.id), 0)
        subtotal = item.price * qty
        total += subtotal
        items.append({'item': item, 'quantity': qty, 'subtotal': subtotal})

    return render(request, 'checkout.html', {'items': items, 'total': total})


# ---------------- Order Success ----------------
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_success.html', {'order': order, 'order_items': order_items})


def test(request):
    return render(request, 'test.html')


@login_required(login_url='login')
def like_feedback(request, pk):
    feedback = get_object_or_404(Feedback, id=pk)

    if feedback.likes.filter(id=request.user.id).exists():
        feedback.likes.remove(request.user)
    else:
        feedback.likes.add(request.user)

    return redirect('feedback')


def feedback_view(request):
    form = FeedbackForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to submit feedback.')
            return redirect('login')
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            # Auto-fill name from user if empty
            if not feedback.name:
                feedback.name = request.user.get_full_name() or request.user.username
            feedback.save()
            messages.success(request, 'Feedback submitted! It will appear after approval.')
            return redirect('feedback')

    feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')
    avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'feedback.html', {
        'form': form,
        'feedbacks': feedbacks,
        'avg_rating': avg_rating
    })


def show_all_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'all_reviews.html', {'reviews': reviews})


def home(request):
    latest_reviews = Review.objects.all().order_by('-created_at')[:3]
    return render(request, 'home.html', {'latest_reviews': latest_reviews})

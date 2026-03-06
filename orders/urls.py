from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.menu_list, name='menu'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-cart-bulk/', views.add_to_cart_bulk, name='add_to_cart_bulk'),
    path('checkout/', views.checkout, name='checkout'),
    path('test/',views.test,name='test'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('like/<int:pk>/', views.like_feedback, name='like_feedback'),
    path('all_reviews/', views.show_all_reviews, name='all_reviews'),
]
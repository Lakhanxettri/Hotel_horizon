from django.contrib import admin
from .models import MenuItem,Category,OrderItem,Order,Feedback,Review
# Register your models here.

admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Order)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price')
    list_filter = ('menu_item',)
    search_fields = ('menu_item__name', 'order__customer__name')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'rating',
        'is_approved',
        'total_likes',
        'created_at'
    )

    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('name', 'message')
    ordering = ('-created_at',)

    actions = ['approve_feedback']

    def approve_feedback(self, request, queryset):
        queryset.update(is_approved=True)

    approve_feedback.short_description = "Mark selected feedback as approved"
    
admin.site.register(Review)
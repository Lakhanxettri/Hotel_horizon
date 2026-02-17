from django.db import models
from datetime import date
from django.utils import timezone
from datetime import timedelta

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    ROOM_CHOICES = (
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('suite', 'Suite'),
    )

    name = models.CharField(max_length=100, default="Guest")
    email = models.EmailField(default="guest@example.com")
    phone = models.CharField(max_length=20, default="0000000000")
    room_type = models.CharField(max_length=20, choices=ROOM_CHOICES, default='single')
    check_in = models.DateField(default=date.today)
    check_out = models.DateField(default=date.today() + timedelta(days=1))
    nationality = models.FileField(max_length=200,upload_to='id_proofs/', default='defaults/placeholder.pdf')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    owner_note = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
     return f"{self.name} - {self.room_type} ({self.status})"
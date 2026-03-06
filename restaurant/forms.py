# from django import forms
# from .models import Booking

# class BookingForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = ['name', 'email', 'phone', 'room_type', 'check_in', 'check_out', 'nationality']
        
        
        
        
from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'room_type', 'check_in', 'check_out', 'message','nationality']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

# Optional: form for owner to update status
class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']
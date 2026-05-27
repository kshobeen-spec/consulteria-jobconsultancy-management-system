from django import forms

class BookingForm(forms.ModelForm):
    name = forms.CharField(label="Full Name", max_length=100)
    email = forms.EmailField(label="Email")
    date = forms.DateField(label="Preferred Date", widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(label="Preferred Time", widget=forms.TimeInput(attrs={'type': 'time'}))
    email = forms.EmailField(label="Email")
    resume = forms.FileField(label="Upload Resume")

from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['full_name', 'email', 'phone', 'date', 'time', 'consultation_type', 'notes', 'resume']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }





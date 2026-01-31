from django import forms
from .models import ReceiptImage

class ReceiptForm(forms.Form):
    image = forms.ImageField()


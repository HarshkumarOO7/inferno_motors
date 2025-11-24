from django import forms
from .models import PurchaseRequest


class CheckoutForm(forms.Form):
    # If you expect a user passed in, pop safely
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['offer_price', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'offer_price': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

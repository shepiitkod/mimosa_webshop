from django import forms
from django.utils import timezone

from .models import CustomOrderRequest

MAX_REFERENCE_BYTES = 8 * 1024 * 1024  # 8 MB


class CustomOrderRequestForm(forms.ModelForm):
    """Sur mesure request. Field labels and help texts are translated in the
    template (data-translate); the form only validates."""

    # Honeypot: real visitors never see or fill it.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = CustomOrderRequest
        fields = (
            "name",
            "email",
            "phone",
            "occasion",
            "event_date",
            "quantity",
            "message",
            "reference_image",
        )
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "event_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "quantity": forms.NumberInput(attrs={"min": 1, "max": 5000}),
            "message": forms.Textarea(attrs={"rows": 5}),
            "reference_image": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp,image/heic"}),
        }

    def clean_event_date(self):
        value = self.cleaned_data.get("event_date")
        if value and value < timezone.localdate():
            raise forms.ValidationError("past-date")
        return value

    def clean_reference_image(self):
        image = self.cleaned_data.get("reference_image")
        if image and getattr(image, "size", 0) > MAX_REFERENCE_BYTES:
            raise forms.ValidationError("file-too-large")
        return image

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("spam")
        return cleaned

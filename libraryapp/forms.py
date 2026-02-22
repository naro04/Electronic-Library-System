from django import forms
from .models import ContactInbox, BookFeedback

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInbox
        fields = ['full_name', 'email', 'subject', 'message']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = BookFeedback
        fields = ['stars', 'comment']
        widgets = {
            'stars': forms.Select(choices=[(i, f"{i} Stars") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
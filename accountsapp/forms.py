from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class RegisterForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=30, required=False)

    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].help_text = ""
        self.fields["email"].help_text = ""

        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["full_name"].widget.attrs.update({"class": "form-control"})
        self.fields["phone"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm Password"

    def clean_username(self):
        v = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=v).exists():
            raise ValidationError("Username already used.")
        return v

    def clean_email(self):
        v = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=v).exists():
            raise ValidationError("Email already used.")
        return v

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 and len(p1) < 8:
            self.add_error("password1", "Password must be at least 8 characters.")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})
        self.fields["remember_me"].widget.attrs.update({"class": "form-check-input"})


class ProfileEditForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    avatar = forms.ImageField(required=False)

    new_password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["full_name"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["phone"].widget.attrs.update({"class": "form-control"})
        self.fields["avatar"].widget.attrs.update({"class": "form-control"})

        self.fields["new_password1"].widget.attrs.update({"class": "form-control"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control"})

        self.fields["new_password1"].label = "New Password"
        self.fields["new_password2"].label = "Confirm New Password"

    def clean_email(self):
        e = self.cleaned_data["email"]
        qs = User.objects.filter(email__iexact=e).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("This email is already used.")
        return e

    def clean(self):
        cleaned = super().clean()
        a = cleaned.get("new_password1")
        b = cleaned.get("new_password2")

        if a or b:
            if not a or not b:
                self.add_error("new_password2", "Please confirm your new password.")
            elif len(a) < 8:
                self.add_error("new_password1", "Password must be at least 8 characters.")
            elif a != b:
                self.add_error("new_password2", "Passwords do not match.")
        return cleaned
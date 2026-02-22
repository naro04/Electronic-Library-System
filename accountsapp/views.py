from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm, ProfileEditForm
from .models import StudentCard

def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )
        user.first_name = form.cleaned_data["full_name"]
        user.save()

        # ضمان وجود StudentCard
        card, _ = StudentCard.objects.get_or_create(user=user)
        card.phone = form.cleaned_data.get("phone", "")
        card.save()

        messages.success(request, "Account created. Please login.")
        return redirect("login")

    return render(request, "accountsapp/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        raw = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        username = raw
        if raw and "@" in raw:
            u = User.objects.filter(email__iexact=raw).first()
            if u:
                username = u.username

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)

            messages.success(request, "Logged in successfully.")
            return redirect("home")

        messages.error(request, "Invalid credentials.")

    return render(request, "accountsapp/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("home")


@login_required
def profile(request):
    user = request.user
    card, _ = StudentCard.objects.get_or_create(user=user)

    current = user.borrows.filter(returned_at__isnull=True).count()
    total = user.borrows.count()

    return render(request, "accountsapp/profile.html", {
        "card": card,
        "current_borrows": current,
        "total_borrows": total
    })


@login_required
def profile_edit(request):
    user = request.user
    card, _ = StudentCard.objects.get_or_create(user=user)

    initial_data = {
        "full_name": user.first_name,
        "email": user.email,
        "phone": card.phone,
        "avatar": card.avatar,
    }

    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
        initial=initial_data
    )

    if request.method == "POST" and form.is_valid():
        user.first_name = form.cleaned_data["full_name"]
        user.email = form.cleaned_data["email"]
        user.save()

        card.phone = form.cleaned_data.get("phone", "")
        if form.cleaned_data.get("avatar"):
            card.avatar = form.cleaned_data["avatar"]
        card.save()

        new_pass = form.cleaned_data.get("new_password1")
        if new_pass:
            user.set_password(new_pass)
            user.save()
            reauth = authenticate(request, username=user.username, password=new_pass)
            if reauth:
                login(request, reauth)

        messages.success(request, "Profile updated.")
        return redirect("profile")

    return render(request, "accountsapp/profile_edit.html", {"form": form})
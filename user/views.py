import os
import secrets
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views import View
from django.contrib import messages
from user.models import UserProfile
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMultiAlternatives
from django.utils.text import slugify
from django.contrib.auth.hashers import check_password

# Create your views here.


def error_404_view(request, exception):
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, "errors/404.html")


def error_500_view(request, exception):
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, "errors/500.html")


class MainView(View):
    def get(self, request):
        template_name = "main.html"
        context = {}
        return render(request, template_name, context)


class LoginView(View):
    form_class = LoginForm
    template_name = "accounts/auth/login.html"

    def get(self, request):

        if request.user.is_authenticated and request.user.is_active:
            return redirect("accounts:home")

        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = request.POST["email"]
            password = request.POST["password"]
            user = authenticate(email=email, password=password)

            if user.is_active:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                try:
                    UserProfile.objects.get(user=request.user)
                except UserProfile.DoesNotExist:
                    return redirect("accounts:signup-user-other")
                redirect_url = self.request.GET.get("redirect_to", "accounts:home")
                return redirect(redirect_url)
            else:
                messages.error(request, "You have not verified your account")
                return redirect("accounts:signup-user")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("accounts:index")


class CreateUserView(View):
    template_name = "accounts/auth/signup.html"

    def post(self, request, slug=None):
        form = CreateAccountForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")
        username = request.POST.get("username")
        profession = request.POST.get("profession")
        industry = request.POST.get("industry")
        is_private = True if int(request.POST.get("is_private")) == 1 else False
        if industry == "":
            messages.error(request, "Industry must be provided")
            return redirect("accounts:signup-user")
        if profession == "":
            messages.error(request, "Profession must be provided")
            return redirect("accounts:signup-user")
        try:
            user = User.objects.get(username=username)
            if user:
                messages.error(
                    request, "Username is already in use. Please try another one"
                )
                return redirect("accounts:signup-user")
        except User.DoesNotExist:
            pass
        try:
            user = User.objects.get(email=email)
            if user:
                messages.error(
                    request,
                    "User with this email already exists. Please login with email address",
                )
                return redirect("accounts:signup-user")
        except User.DoesNotExist:
            pass
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(password)
            user.username = username
            user.user_type = user_type
            user.is_active = False
            user.token = secrets.token_hex(16)
            user.save()

            profile = UserProfile.objects.create(
                user=user,
                profession=profession,
                slug=slugify(f"{username}-{user.id}"),
                is_private=is_private,
            )

            if slug:
                try:
                    old_user = UserProfile.objects.get(slug=slug)
                    profile.invited_by = old_user
                    profile.save()
                except User.DoesNotExist:
                    pass

            context = {
                "name": user.username,
                "email": user.email,
                "id": user.id,
                "token": user.token,
                "is_active": user.is_active,
            }
            return render(request, "accounts/auth/welcome.html", context)
        # print(form.errors)
        messages.success(request, form.errors)
        return render(request, self.template_name, {"form": form.errors})

    # return redirect('accounts:home')


def send_token(request):
    if request.method == "POST":
        urlx = request.POST.get("urlx")
        email = request.POST.get("email")
        subject, from_email, to = (
            "Welcome to Notion Africa",
            "success@notionafrica.org",
            f"{email}",
        )
        text_content = "This is an important message."
        html_content = f"<h1>Thanks for joining our world Notion Africa says hello</h1><p>click to verify: https://staging.notionafrica.org{urlx}</p><p>After clicking the link. You may be required to log in with the details you provided</p>"
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return redirect("accounts:home")


def verification(request, token, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.token == token:
            user.is_active = True
            user.save()
            if user.is_admin or user.is_superuser:
                messages.error(request, "You are not authourized.")
            else:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                return redirect("accounts:home")
    except User.DoesNotExist:
        return redirect("accounts:signup-user")


class UploadProfilePictureView(LoginRequiredMixin, View):
    login_url = "accounts:login"
    redirect_field_name = "redirect_to"
    form_class = UploadProfilePictureForm

    def post(self, request, id, *args, **kwargs):

        profile = UserProfile.objects.get(id=id)
        data = {"image": profile.image}
        form = self.form_class(request.POST, request.FILES, initial=data)
        if form.is_valid():
            # check if image field is not empty
            if profile.image:
                # check if image field path exist in directory
                if os.path.exists(profile.image.path):
                    # remove from path and reupdate with the new one
                    os.remove(profile.image.path)
                    profile.image = request.FILES["image"]
                    profile.save()
                    return JsonResponse(
                        {"message": "success", "img": profile.image.url}
                    )
                else:
                    # update new image if theres no image in directory
                    profile.image = request.FILES["image"]
                    profile.save()
                    return JsonResponse(
                        {"message": "success", "img": profile.image.url}
                    )
            else:
                # update new image if there no image in the image field
                profile.image = request.FILES["image"]
                profile.save()
                # log_activity(self.request.user, self.request.user.business_id, "deactivated branch '"+branch.name+"'")
                return JsonResponse({"message": "success", "img": profile.image.url})

        return JsonResponse({"message": "Validating image failed"})


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        template_name = "accounts/change_password.html"
        context = {}
        return render(request, template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return JsonResponse({"message": "success"})
        else:
            return JsonResponse({"message": form.errors})


def deactivate(request, user_id):
    if request.method == "POST":
        try:
            user = User.objects.get(id=user_id)
            password = request.POST.get("password")
            if check_password(password, user.password):
                user.is_active = False
                user.save()
                logout(request)
                return redirect("accounts:login")
            else:
                return JsonResponse({"data": "failed"})
        except User.DoesNotExist:
            return redirect("accounts:login")

import contextlib
import secrets
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views import View
from django.contrib import messages
from main_site.tasks import send_account_activation_email
from user.models import UserProfile, User
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.text import slugify
from django.contrib.sites.shortcuts import get_current_site  
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


class LoginView(View):
    
    template_name = "public/login.html"

    def get(self, request):

        if request.user.is_authenticated and request.user.is_active:
            return redirect("/")
        
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user= User.objects.get(email=email) or User.objects.get(username=email)
            
            if not user.user_profile.is_email_verified:
                messages.warning(request, 'Your account is not verified.')
                return HttpResponseRedirect(request.path_info)
        
            if not user.is_active:
                messages.error(request, "Your account is not active")
                return HttpResponseRedirect(request.path_info)
            
            if not check_password(password, user.password):
                messages.error(request, "Wrong Password")
                return HttpResponseRedirect(request.path_info)
            
            if user := authenticate(email=user.email, password=password):
                login(request, user)
                return redirect("management:dashboard") if user.is_staff else redirect('/') #pyright:ignore
            
        except User.DoesNotExist:
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)
        return HttpResponseRedirect(request.path_info)


class AdminLoginView(View):
    template_name = "management/login.html"

    def get(self, request):

        if request.user.is_authenticated and request.user.is_active:
            return redirect("management:dashboard")
        
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            
            user= User.objects.get(email=email) or User.objects.get(username=email)

            if not user.is_active:
                messages.error(request, "Your account is not active")
                return HttpResponseRedirect(request.path_info)

            if not check_password(password, user.password):
                messages.error(request, "Wrong Password")
                return HttpResponseRedirect(request.path_info)

            if user := authenticate(email=user.email, password=password):
                login(request, user)
                return redirect("management:dashboard") if user.is_staff else redirect('/') #pyright:ignore

        except User.DoesNotExist:
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)
        return HttpResponseRedirect(request.path_info)

# In case otp for verification
# class AdminLoginView(View):
#     template_name = "management/login.html"

#     def get(self, request):

#         if request.user.is_authenticated and request.user.is_active:
#             return redirect("management:dashboard")
        
#         return render(request, self.template_name)

#     def post(self, request, *args, **kwargs):
#         email = request.POST["email"]
#         password = request.POST["password"]
#         phone = request.POST["phone"]
#         user = authenticate(email=email, password=password)
#         if user:
#             if user.is_active:
#                 user.user_profile.otp = random.randint(1000, 9999) #pyright:ignore
#                 user.user_profile.save() #pyright:ignore
#                 message_handler = MessageHandler(phone,user.user_profile.otp) #pyright:ignore
#                 return redirect('main_site:otp')
#             else:
#                 messages.error(request, "Your account is not active")
#                 return redirect('accounts:login')
#         return redirect('management:dashboard')


# def verify_with_otp(request, profile_id):
#     otp = request.POST.get('otp')
#     profile = UserProfile.objects.get(id=profile_id)
#     if otp == profile.otp:
#         login(request, profile.user)
#         return redirect('management:dashboard')
#     return redirect('management:dashboard')

class LogoutView(View):
    def get(self, request):
        is_admin = bool(request.user.is_staff)
        logout(request)
        return redirect("accounts:admin_login") if is_admin else redirect("accounts:login")


#for the website customers
class RegisterUserView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_active:
            return redirect("/")
        return render(request, "public/register.html")
    
    def post(self, request, slug=None):
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")
        with contextlib.suppress(User.DoesNotExist):
            if user := User.objects.get(username=username):
                messages.error(
                    request, "Username is already in use. Please try another one"
                )
                return HttpResponseRedirect(request.path_info)
        with contextlib.suppress(User.DoesNotExist):
            if user := User.objects.get(email=email):
                messages.error(
                    request,
                    "User with this email already exists. Please login with email address",
                )
                return HttpResponseRedirect(request.path_info)
        return self.create_new_user(password, username, email, request)

    def create_new_user(self, password, username, email, request):
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.username = username
        user.email = email
        user.is_active = False
        user.is_staff = False
        user.save()
        current_site = get_current_site(request)
        email_token = str(secrets.token_hex(16))
        UserProfile.objects.create(user = user, email_token = email_token)
        email = user.email
        send_account_activation_email.delay(email , email_token, current_site.domain)
        messages.success(request,"An email has been sent for verification")
        return HttpResponseRedirect(request.path_info)


def verification(request, token):
    try:
        profile = UserProfile.objects.select_related('user').get(email_token=token)
        profile.is_email_verified = True
        profile.user.is_active = True #pyright:ignore
        profile.user.save() #pyright:ignore
        profile.save()
        messages.success(request,"Account verified, Please Login")
        return redirect("accounts:login")
    except UserProfile.DoesNotExist:
        messages.success(request,"Account verification failed, Please try again")
        return redirect("accounts:signup-user")

class ChangePasswordView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if not form.is_valid():
            return JsonResponse({"message": form.errors})
        user = form.save()
        update_session_auth_hash(request, user)  # Important!
        return JsonResponse({"message": "success"})

class PublicProfileView(LoginRequiredMixin, View):
    def get(self, request):
        template_name = "accounts/public_user_profile.html"
        context = {}
        return render(request, template_name, context) 
    
class PublicProfileUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        other_name = request.POST.get("other_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        try:
            profile = UserProfile.objects.get(uid = request.user.user_profile.uid)
            profile.first_name = first_name
            profile.last_name = last_name
            profile.address = address
            profile.phone = phone
            profile.address=address
            profile.other_name = other_name
            request.user.email = email
            profile.save()
            request.user.save()
        except UserProfile.DoesNotExist:
            return JsonResponse({"message": "Profile does not exist"})            
        return JsonResponse({"message": "success"})


def deactivate(request, user_id):
    if request.method != "POST":
        return
    try:
        return deactivate_user(user_id, request)
    except User.DoesNotExist:
        return redirect("accounts:login")


# TODO Rename this here and in `deactivate`
def deactivate_user(user_id, request):
    user = User.objects.get(id=user_id)
    password = request.POST.get("password")
    if not check_password(password, user.password):
        return JsonResponse({"data": "failed"})
    user.is_active = False
    user.save()
    logout(request)
    return redirect("accounts:login")

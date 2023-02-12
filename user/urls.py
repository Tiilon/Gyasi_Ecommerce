from django.urls import path, reverse_lazy
from user.views import *
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

app_name = 'accounts'

urlpatterns = [
    path('login', AdminLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    # path('signup', CreateUserView.as_view(), name='signup-user'),
    # path('signup-invite/<str:slug>/', CreateUserView.as_view(), name='signup-user-invite'),
    # path('verify/<str:token>/<int:user_id>/', verification, name='auth_userx'),
    # path('send-token', send_token, name='send_token'),
    # path('deactivate/<int:user_id>/', deactivate, name='deactivate'),
    # path('profile/<int:id>/change-profile',UploadProfilePictureView.as_view(), name="change-profile"),
]

from .views import register, verify_otp, login_view
from django.urls import path

urlpatterns = [
    path('register/', register),
    path('verify-otp/', verify_otp),
    path('login/', login_view),
]
import random
import re 
from django.contrib.auth import authenticate, login
import json
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import OTP
from django.views.decorators.csrf import csrf_exempt


User = get_user_model()
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
    except json.JSONDecodeError:

        email = request.POST.get("email")
        password = request.POST.get("password")

    errors = {}
    if not email:
        errors["email"] = "Email is required."
    elif not re.match(EMAIL_REGEX, email):
        errors["email"] = "Invalid email format."

    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 6:
        errors["password"] = "Password must be at least 6 characters."

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "User with this email already exists."}, status=400)

    username = email.split("@")[0] 
    user = User.objects.create_user(username=username, email=email, password=password)

    otp = random.randint(100000, 999999)

    return JsonResponse({
        "message": "User registered successfully.",
        "email": email,
        "otp": otp
    })

@csrf_exempt
def verify_otp(request):
    email = request.POST['email']
    otp_code = request.POST['otp']

    user = User.objects.get(email=email)
    otp = OTP.objects.filter(user=user, code=otp_code).first()

    if otp:
        user.is_verified = True
        user.save()
        otp.delete()
        return JsonResponse({'message': 'Account verified'})
    else:
        return JsonResponse({'error': 'Invalid OTP'}, status=400)
    

@csrf_exempt
def login_view(request):
    email = request.POST['email']
    password = request.POST['password']

    user = authenticate(request, email=email, password=password)

    if user:
        if not user.is_verified:
            return JsonResponse({'error': 'Account not verified'})
        login(request, user)
        return JsonResponse({'message': 'Login successful'})
    return JsonResponse({'error': 'Invalid credentials'}, status=400)

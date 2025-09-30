from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

# Create your views here.
def Login(request):
    username=request.POST.get("Username"),
    password=request.POST.get("Password"),
    if username and password:
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def Register(request):
    if request.method == 'POST':
        username = request.POST.get("Username")
        password = request.POST.get("Password")
        if username and password:
            # Create new user
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'register.html', {'error': 'Please provide both username and password'})
    return render(request, 'register.html')
def Home(request):
    return render(request, 'home.html','Style.css')
def UserProfile(request):
    return render(request, 'user_profile.html','Style.css')

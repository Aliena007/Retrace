from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

# Create your views here.
def Login(request):
    if request.method == 'POST':
        username = request.POST.get("Username")
        password = request.POST.get("Password")
        if username and password:
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'Login.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'Login.html', {'error': 'Please provide both username and password'})
    return render(request, 'Login.html')

def Register(request):
    if request.method == 'POST':
        username = request.POST.get("Username")
        password = request.POST.get("Password")
        if username and password:
            # Create new user
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return render('Register.html')
def Home(request):
    return render(request, 'Base.html')

def UserProfile(request):
    if request.user.is_authenticated:
        return render(request, 'Profile.html')
    return render(request, 'Base.html','Style.css')
def UserProfile(request):
    if request.user.is_authenticated:
        return render(request, 'Profile.html','Style.css')
    return render(request, 'Profile.html','Style.css')

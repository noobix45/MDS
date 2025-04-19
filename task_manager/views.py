from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User

# Create your views here.

#@login_required
def home(request):
    return render(request, 'home.html')
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) #logare automata dupa inregistrare
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request,'register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(f"Login încercat pentru: {username} cu parola: {password}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("Autentificare REUȘITĂ")
            login(request, user)
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            print("Autentificare EȘUATĂ")
            return redirect('login')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')
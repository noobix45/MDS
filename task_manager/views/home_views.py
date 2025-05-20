from django.db import connection
from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from task_manager.forms.user_forms import UserRegistrationForm
from django.contrib.auth import logout
from task_manager.models import Task,Utilizator

# Create your views here.

# @login_required
def home(request):
    tasks = []
    if request.user.is_authenticated:
        try:
            sort_criteria = request.GET.get('sort')
            utilizator = Utilizator.objects.get(user=request.user)
            tasks = Task.objects.filter(utilizatori_task__id_utilizator=utilizator,grup_task=False)

            if sort_criteria=='importanta':
                tasks = tasks.order_by('importanta')
            elif sort_criteria=='deadline':
                tasks = tasks.order_by('deadline')
            elif sort_criteria=='titlu':
                tasks = tasks.order_by('titlu')
            elif sort_criteria == 'prioritate':
                tasks = tasks.order_by('prioritate')
            else:
                if tasks.filter(prioritate__gt=0.0).exists():
                    tasks = tasks.order_by('prioritate')
        except Utilizator.DoesNotExist:
            tasks = []
    return render(request, 'home.html', {'tasks': tasks})
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) #logare automata dupa inregistrare
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form':form})

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

def delete_account(request):
    user_auth_id = request.user.id
    logout(request)

    try:
        utilizator = Utilizator.objects.get(user_id=user_auth_id)
        user_app_id = utilizator.id_utilizator  # dacă ai nevoie de el
    except Utilizator.DoesNotExist:
        user_app_id = None

    with connection.cursor() as cursor:
        if user_app_id is not None:
            cursor.execute("DELETE FROM utilizator WHERE id_user = %s", [user_auth_id])
        cursor.execute("DELETE FROM auth_user WHERE id = %s", [user_auth_id])

    return redirect('register')
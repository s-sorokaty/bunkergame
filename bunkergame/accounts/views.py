from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('/lobbys/lobbys_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/lobbys/lobbys_list')  # Redirect to a home page or dashboard
        else:
            return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль.'})
    return render(request, 'login.html')
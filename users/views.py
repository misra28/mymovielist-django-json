from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import RegisterUserForm
from movielist.models import User

# Create your views here.
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('display_home')
        else:
            messages.success(request, ("There was an error logging in. Try again."))
            return redirect('login_user')
    else:
        return render(request, 'authenticate/login_user.html')
    
def logout_user(request):
    logout(request)
    messages.success(request, ("Successfully logged out."))
    return redirect('display_home')

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            newuser = User(username=username, first_name=first_name, last_name=last_name)
            newuser.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return redirect('display_home')
        
    else:
        form = RegisterUserForm()
    
    return render(request, 'authenticate/register_user.html', {'form':form})
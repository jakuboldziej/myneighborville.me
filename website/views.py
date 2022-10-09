from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.contrib.auth.models import User


from .models import WebsiteUser

# 404 Handling
def view_page_not_found(request, exception):
    return render(request, '404.html')

# Views
def index(request):
    context = {
        
    }
    return render(request, 'index.html', context)

def map(request):
    context = {
        
    }
    return render(request, 'map.html', context)

# Auth
def logout(request):
    logout(request)
    return redirect('/')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        location = request.POST['location']
        phoneNumber = request.POST['phoneNumber']
        password = request.POST['password']

        new_user = User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            first_name=firstName,
            last_name=lastName
        )
        new_user.save()
        user = User.objects.get(username=username)
        new_websiteUser = WebsiteUser.objects.create(
            user=new_user,
            location=location, 
            phoneNumber=phoneNumber, 
        )
        new_websiteUser.save()

        return redirect("/login")
    return render(request, "registration/register.html")
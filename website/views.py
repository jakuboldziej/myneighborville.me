from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib import messages

from django.conf import settings

import datetime

from .models import WebsiteUser, Event, News, Marker

# 404 Handling
def view_page_not_found(request, exception):
    return render(request, '404.html')

# Views
def index(request):
    context = {
        
    }
    return render(request, 'index.html', context)

def map(request):
    markers = Marker.objects.all()
    api_key = settings.GOOGLE_API_KEY
    context = {
        'markers': markers,
        'api_key': api_key,
    }
    return render(request, 'map.html', context)

def events(request):
    events = Event.objects.all().order_by('-id')
    context = {
        'events': events,
    }
    return render(request, 'events.html', context)

def profile(request, id):
    currentUser = User.objects.get(id=id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    userEvents = Event.objects.filter(user=currentWebsiteUser).order_by('id')
    userNews = News.objects.filter(user=currentWebsiteUser)
    request.session["currentWebsiteUser"] = currentWebsiteUser.id

    context = {
        'currentUser': currentUser,
        'userEvents': userEvents,
        'userNews': userNews,
    }
    return render(request, 'profile.html', context)

def addMarkerView(request):
    if request.method == 'POST':
        location = request.POST['location']
        title = request.POST['title']
        content = request.POST['content']
        locSplit = location.split(', ')
        lat = locSplit[0]
        lng = locSplit[1]

        # return redirect('/addMarker/' + location + '/' + title + '/' + content)
        return redirect('/map')
    else:
        return render(request, 'addMarker.html')

def addNewsView(request):

    return render(request, 'addNews.html')

# Events
def addEvent(request):
    if request.method == "POST":
        currentUser = User.objects.get(id=request.user.id)
        currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
        users = [currentWebsiteUser]
        title = request.POST['title']
        description = request.POST['description']

        newEvent = Event.objects.create(
            title=title, 
            description=description,
            dateStart=datetime.datetime.today(),
            dateEnd=datetime.datetime.today(),
            timeStart=datetime.datetime.utcnow(),
            timeEnd=datetime.datetime.utcnow(),
            )
        newEvent.user.set(users)
        newEvent.save()

        currentWebsiteUser = request.session["currentWebsiteUser"]

        return redirect('/profile/' + str(currentWebsiteUser))
    else:
        context = {

        }
        return render(request, 'addEvent.html', context)

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
        password2 = request.POST['password2']
        
        if password != password2:
            messages.info(request, 'Passwords don\'t match!')
            return redirect("/register")
        else:
            new_user = User.objects.create(
                username=username,
                password=make_password(password),
                email=email,
                first_name=firstName,
                last_name=lastName
            )
            new_user.save()
            new_websiteUser = WebsiteUser.objects.create(
                user=new_user,
                location=location, 
                phoneNumber=phoneNumber, 
            )
            new_websiteUser.save()

            return redirect("/login")
    return render(request, "registration/register.html")
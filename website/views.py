from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings

import datetime

from .models import WebsiteUser, Event, News, Marker, Job

# 404 Handling
def view_page_not_found(request, exception):
    return render(request, '404.html')

# Views
@login_required
def index(request):
    events = Event.objects.all().order_by('-id')[:6]
    news = News.objects.all().order_by('-id')[:6]
    jobs = Job.objects.all().order_by('-id')[:6]
    context = {
        'events': events,
        'news': news,
        'jobs': jobs,
    }
    return render(request, 'index.html', context)

@login_required
def map(request):
    api_key = settings.GOOGLE_API_KEY
    userLocation = WebsiteUser.objects.get(id=request.user.id).location
    userLocation = userLocation.replace(" ", "_")
    markers = Marker.objects.all()
    # Tutaj narazie wyświetla tylko znacznik usera
    # markers = Marker.objects.filter(title=userLocation)

    context = {
        'markers': markers,
        'api_key': api_key,
        'userLocation': userLocation,
    }
    return render(request, 'map.html', context)

@login_required
def news(request):
    news = News.objects.all().order_by('-id')
    context = {
        'news': news,
    }
    return render(request, 'news.html', context)

@login_required
def events(request):
    events = Event.objects.all().order_by('-id')
    context = {
        'events': events,
    }
    return render(request, 'events.html', context)

@login_required
def jobs(request):
    jobs = Job.objects.all().order_by('-id')
    context = {
        'jobs': jobs,
    }
    return render(request, 'jobs.html', context)

# Views with params
@login_required
def profileSettings(request, id):
    currentUser = User.objects.get(id=id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)

    context = {
        'currentUser': currentWebsiteUser,
    }
    return render(request, 'settings.html', context)

@login_required
def profile(request, id):
    currentUser = User.objects.get(id=id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    userEvents = Event.objects.filter(user=currentWebsiteUser).order_by('id')
    userNews = News.objects.filter(user=currentWebsiteUser)
    userJobs = Job.objects.filter(userId=currentWebsiteUser.id)
    request.session["currentWebsiteUser"] = currentWebsiteUser.id

    context = {
        'currentUser': currentWebsiteUser,
        'userEvents': userEvents,
        'userNews': userNews,
        'userJobs': userJobs,
    }
    return render(request, 'profile.html', context)

@login_required
def oneNews(request, id):
    oneNews = News.objects.get(id=id)
    context = {
        'oneNews': oneNews,
    }
    return render(request, 'oneNews.html', context)

@login_required
def event(request, id):
    event = Event.objects.get(id=id)
    context = {
        'event': event,
    }
    return render(request, 'event.html', context)

@login_required
def job(request, id):
    job = Job.objects.get(id=id)
    userId = int(job.userId)
    createdBy = WebsiteUser.objects.get(id=userId)
    context = {
        'job': job,
        'createdBy': createdBy
    }
    return render(request, 'job.html', context)

# Events
@login_required
def addEvent(request):
    currentUser = User.objects.get(id=request.user.id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    if request.method == "POST":
        users = [currentWebsiteUser]
        title = request.POST['title']
        description = request.POST['description']
        address = request.POST['address']
        location = request.POST['location']

        newEvent = Event.objects.create(
            title=title, 
            description=description,
            dateStart=datetime.datetime.today(),
            dateEnd=datetime.datetime.today(),
            timeStart=datetime.datetime.utcnow(),
            timeEnd=datetime.datetime.utcnow(),
            location=address,
            )
        newEvent.user.set(users)
        newEvent.save()
        currentWebsiteUser = request.session["currentWebsiteUser"]

        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]
        address = address.replace(" ", "_")
        try:
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content=description,
                type="Event",
            )
            newMarker.users.add(currentWebsiteUser)
            newMarker.save()
        except:
            _ = 0

        return redirect('/profile/' + str(currentWebsiteUser))
    else:
        api_key = settings.GOOGLE_API_KEY
        markers = Marker.objects.all()
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_")

        context = {
            'api_key': api_key,
            'markers': markers,
            'userLocation': userLocation,
        }
        return render(request, 'addEvent.html', context)

@login_required
def addNews(request):
    currentUser = User.objects.get(id=request.user.id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    if request.method == "POST":
        users = [currentWebsiteUser]
        title = request.POST['title']
        description = request.POST['description']
        address = request.POST['address']
        location = request.POST['location']

        newNews = News.objects.create(
            title=title, 
            description=description,
            createdAtDate=datetime.datetime.today(),
            createdAtTime=datetime.datetime.utcnow(),
            location=address,
            )
        newNews.user.set(users)
        newNews.save()
        currentWebsiteUser = request.session["currentWebsiteUser"]

        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]
        address = address.replace(" ", "_")
        try:
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content=description,
                type="News",
            )
            newMarker.users.add(currentWebsiteUser)
            newMarker.save()
        except:
            _ = 0

        return redirect('/profile/' + str(currentWebsiteUser))
    else:
        api_key = settings.GOOGLE_API_KEY
        markers = Marker.objects.all()        
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_")

        context = {
            'api_key': api_key,
            'markers': markers,
            'userLocation': userLocation,
        }
        return render(request, 'addNews.html', context)

@login_required
def addJob(request):
    currentUser = User.objects.get(id=request.user.id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        address = request.POST['address']
        location = request.POST['location']

        newJob = Job.objects.create(
            userId=currentWebsiteUser.id,
            title=title, 
            description=description,
            location=address,
            )
        newJob.save()
        currentWebsiteUser = request.session["currentWebsiteUser"]

        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]
        address = address.replace(" ", "_")
        try:
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content=description,
                type="Job",
            )
            newMarker.users.add(currentWebsiteUser)
            newMarker.save()
        except:
            _ = 0

        return redirect('/profile/' + str(currentWebsiteUser))
    else:
        api_key = settings.GOOGLE_API_KEY
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_")
        markers = Marker.objects.all()

        context = {
            'api_key': api_key,
            'userLocation': userLocation,
            'markers': markers,
        }
        return render(request, 'addJob.html', context)

@login_required
def addMarker(request):
    currentUser = User.objects.get(id=request.user.id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    if request.method == 'POST':
        location = request.POST['location']
        title = request.POST['title']
        content = request.POST['content']
        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]

        title = title.replace(" ", "_")

        newMarker = Marker.objects.create(
            latitude=lat,
            longitude=lng,
            title=title,
            content=content,
        )
        newMarker.save()
        return redirect('/add_marker')
    else:
        api_key = settings.GOOGLE_API_KEY
        markers = Marker.objects.all()
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_")

        context = {
            'api_key': api_key,
            'markers': markers,
            'userLocation': userLocation,
        }
        return render(request, 'addMarker.html', context)

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
        address = request.POST['address']
        location = request.POST['location']
        phoneNumber = request.POST['phoneNumber']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.info(request, 'Passwords don\'t match!')
            return redirect("/register")
        # elif len(password) < 6:
            # messages.warning(request, "Password must be at least 6 characters long.")
            # return redirect('/register')
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
                location=address, 
                phoneNumber=phoneNumber, 
            )
            new_websiteUser.save()
            
            location = location[1:-1]
            locSplit = location.split(", ")
            lat = locSplit[0]
            lng = locSplit[1]

            address = address.replace(" ", "_")
            try:
                newMarker = Marker.objects.create(
                    latitude=lat,
                    longitude=lng,
                    title=address,
                    content="Home",
                    type="Home",
                )
                newMarker.users.add(new_websiteUser)
                newMarker.save()
            except:
                _ = 0
            return redirect("/login")
    else:
        api_key = settings.GOOGLE_API_KEY

        context = {
            'api_key': api_key,
        }
        return render(request, "registration/register.html", context)
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
    userCity = userLocation.split(', ')[0].replace(' ', '_')
    userLocation = userLocation.replace(" ", "_")
    userLocation = userLocation.replace(",", "")
    userHomeMarker = Marker.objects.get(title=userLocation)
    markers = Marker.objects.all()
    allMarkers = [marker for marker in markers if marker.type != "Home"]
    cityMarkers = [marker for marker in markers if userCity in marker.title and marker.type != "Home"]
    # Tutaj narazie wyświetla tylko znacznik usera
    # markers = Marker.objects.filter(title=userLocation)

    context = {
        'markers': markers,
        'allMarkers': allMarkers,
        'cityMarkers': cityMarkers,
        'api_key': api_key,
        'userLocation': userLocation,
        'userHomeMarker': userHomeMarker,
        'userCity': userCity,
    }
    return render(request, 'map.html', context)

@login_required
def news(request):
    news = News.objects.all().order_by('-id')
    context = {
        'news': news,
    }
    return render(request, 'displayServices/news.html', context)

@login_required
def events(request):
    events = Event.objects.all().order_by('-id')
    context = {
        'events': events,
    }
    return render(request, 'displayServices/events.html', context)

@login_required
def jobs(request):
    jobs = Job.objects.all().order_by('-id')
    users = WebsiteUser.objects.all()
    context = {
        'jobs': jobs,
        'users': users,
    }
    return render(request, 'displayServices/jobs.html', context)

# Views with params
@login_required
def profileSettings(request, nick):
    currentUser = User.objects.get(username=nick)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)

    context = {
        'currentUser': currentWebsiteUser,
    }
    if currentWebsiteUser.user == request.user:
        return render(request, 'settings.html', context)
    else:
        return redirect('/')
        
@login_required
def profile(request, nick):
    currentUser = User.objects.get(username=nick)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    userEvents = Event.objects.filter(user=currentWebsiteUser).order_by('id')
    userNews = News.objects.filter(user=currentWebsiteUser)
    userJobs = Job.objects.filter(userId=currentWebsiteUser.id)
    request.session["currentWebsiteUser"] = currentWebsiteUser.user.username

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
        dateStart = request.POST['dateStart']
        dateStart = dateStart.split("T")
        dateStart = dateStart[0] + ' ' + dateStart[1] + '+00:00'
        dateEnd = request.POST['dateEnd']
        dateEnd = dateEnd.split("T")
        dateEnd = dateEnd[0] + ' ' + dateEnd[1] + '+00:00'

        newEvent = Event.objects.create(
            title=title, 
            description=description,
            dateStart=dateStart,
            dateEnd=dateEnd,
            location=address,
            )
        newEvent.user.set(users)
        newEvent.save()
        currentWebsiteUser = request.session["currentWebsiteUser"]

        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]
        address = address.replace(" ", "_").replace(',', '')
        try:
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content=description,
                type="Event",
            )
            newMarker.events.add(newEvent)
            # newMarker.users.add(currentWebsiteUser)
            newMarker.save()
        except:
            _ = 0

        return redirect('/profile/' + str(currentWebsiteUser))
    else:
        api_key = settings.GOOGLE_API_KEY
        markers = Marker.objects.all()
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_").replace(",", "")

        context = {
            'api_key': api_key,
            'markers': markers,
            'userLocation': userLocation,
        }
        return render(request, 'addServices/addEvent.html', context)

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
            location=address,
            markerId=0
            )
        newNews.user.set(users)
        
        currentWebsiteUser = request.session["currentWebsiteUser"]

        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]
        try:
            address = address.replace(" ", "_").replace(',', '')
            checkMarker = Marker.objects.get(title=address)
        except:
            checkMarker = None
        if checkMarker:
            checkMarker.content += '<a href="/news/' + str(newNews.id) + '">' + newNews.title + '</a>\n</br>'
            checkMarker.news.add(newNews)
            checkMarker.save()

            newNews.markerId = checkMarker.id
            newNews.save()
        else:
            address = address.replace(" ", "_").replace(',', '')
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content='<a href="/news/' + str(newNews.id) + '">' + newNews.title + '</a>\n</br>',
                type="News",
            )
            newMarker.news.add(newNews)
            # newMarker.users.add(currentWebsiteUser)
            newMarker.save()

            newNews.markerId = newMarker.id
            newNews.save()

        return redirect('/profile/' + str(currentWebsiteUser))
    else:
        api_key = settings.GOOGLE_API_KEY
        markers = Marker.objects.all()        
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_").replace(",", "")

        context = {
            'api_key': api_key,
            'markers': markers,
            'userLocation': userLocation,
        }
        return render(request, 'addServices/addNews.html', context)

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
        address = address.replace(" ", "_").replace(',', '')
        try:
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content=description,
                type="Job",
            )
            newMarker.jobs.add(newJob)
            # newMarker.users.add(currentWebsiteUser)
            newMarker.save()
        except:
            _ = 0

        return redirect('/profile/' + str(currentWebsiteUser))
    else:
        api_key = settings.GOOGLE_API_KEY
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_").replace(",", "")
        markers = Marker.objects.all()

        context = {
            'api_key': api_key,
            'userLocation': userLocation,
            'markers': markers,
        }
        return render(request, 'addServices/addJob.html', context)

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

        title = title.replace(" ", "_").replace(',', '')

        newMarker = Marker.objects.create(
            latitude=lat,
            longitude=lng,
            title=title,
            content=content,
            type="add_marker",
            typeId=9999
        )
        newMarker.save()
        return redirect('/add_marker')
    else:
        api_key = settings.GOOGLE_API_KEY
        markers = Marker.objects.all()
        userLocation = currentWebsiteUser.location
        userLocation = userLocation.replace(" ", "_").replace(",", "")

        context = {
            'api_key': api_key,
            'markers': markers,
            'userLocation': userLocation,
        }
        return render(request, 'addServices/addMarker.html', context)

@login_required
def editEvent(request, id):
    event = Event.objects.get(id=id)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        dateStart = request.POST['dateStart']
        dateEnd = request.POST['dateEnd']
        
        dateStart = dateStart.split("T")
        dateStart = dateStart[0] + ' ' + dateStart[1] + '+00:00'
        dateEnd = dateEnd.split("T")
        dateEnd = dateEnd[0] + ' ' + dateEnd[1] + '+00:00'

        event.title = title
        event.description = description
        event.dateStart = dateStart
        event.dateEnd = dateEnd
        event.save()

        return redirect('/profile/' + request.user.username)
    else:
        context = {
            'event': event,
        }
        return render(request, 'editServices/editEvent.html', context)

@login_required
def editJob(request, id):
    job = Job.objects.get(id=id)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']

        job.title = title
        job.description = description
        job.save()

        return redirect('/profile/' + request.user.username)
    else:
        context = {
            'job': job,
        }
        return render(request, 'editServices/editJob.html', context)

@login_required
def editNews(request, id):
    news = News.objects.get(id=id)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']

        news.title = title
        news.description = description
        news.save()

        return redirect('/profile/' + request.user.username)
    else:
        context = {
            'news': news,
        }
        return render(request, 'editServices/editNews.html', context)
    
@login_required
def deleteEvent(request, id):
    event = Event.objects.get(id=id)
    marker = Marker.objects.get(id=event.markerId, type="Event")
    event.delete()
    marker.delete()
    return redirect('/profile/' + request.user.username)

@login_required
def deleteJob(request, id):
    job = Job.objects.get(id=id)
    marker = Marker.objects.get(typeId=job.id, type="Job")
    job.delete()
    marker.delete()
    return redirect('/profile/' + request.user.username)

@login_required
def deleteNews(request, id):
    news = News.objects.get(id=id)
    marker = Marker.objects.get(id=news.markerId, type="News")

    newsLinia = '/news/' + str(news.id)
    # jeżel linie jest None usuń też markera
    linie = marker.content.split("</br>")
    print(linie)
    for i, linia in enumerate(linie):
        if newsLinia in linia:
            linie.pop(i)
    print(linie)
    result = ''
    for i, linia in enumerate(linie):
        if i == len(linie) - 1:
            result += linia
        else:
            result += linia + '</br>'
    print(result)
    marker.content = result
    marker.save()
    news.delete()
    return redirect('/profile/' + request.user.username)

@login_required
def deleteUserFromJob(request, jobId, userId):
    user = WebsiteUser.objects.get(id=userId)
    job = Job.objects.get(id=jobId)

    job.people.remove(user)
    job.save()
    return redirect('/jobs/edit_job/' + jobId)

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
            users = [username.username for username in User.objects.all()]
            if username in users:
                messages.info(request, 'User already exists')
                return redirect("/register")
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

            address = address.replace(" ", "_").replace(',', '')
            try:
                newMarker = Marker.objects.create(
                    latitude=lat,
                    longitude=lng,
                    title=address,
                    content="Home",
                    type="Home",
                    typeId=0
                )
                # newMarker.users.add(new_websiteUser)
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
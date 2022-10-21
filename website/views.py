from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings

import datetime

from .models import WebsiteUser, Event, News, Marker, Job

# 404 Handling
def view_page_not_found(request):
    return render(request, '404.html')

# Views
@login_required
def index(request):
    displayedElements = 12
    events = Event.objects.all().order_by('-id')
    news = News.objects.all().order_by('-id')
    jobs = Job.objects.all().order_by('-id')

    eventsCount = events.count()
    newsCount = news.count()
    jobsCount = jobs.count()

    context = {
        'events': events[:displayedElements],
        'news': news[:displayedElements],
        'jobs': jobs[:displayedElements],
        'eventsCount': eventsCount,
        'newsCount': newsCount,
        'jobsCount': jobsCount,
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

    context = {
        'allMarkers': allMarkers,
        'cityMarkers': cityMarkers,
        'api_key': api_key,
        'userLocation': userLocation,
        'userHomeMarker': userHomeMarker,
    }
    return render(request, 'map.html', context)

@login_required
def home_list(request):
    user = WebsiteUser.objects.get(id=request.user.id)
    marker = Marker.objects.get(title=user.location)
    jobs = marker.jobs.all()
    events = marker.events.all()
    news = marker.news.all()

    context = {
        'jobs': jobs,
        'events': events,
        'news': news,
    }
    return render(request, 'home_list.html', context)

# Profile
@login_required
def profile(request, nick):
    currentUser = User.objects.get(username=nick)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    userEvents = Event.objects.filter(userId=currentWebsiteUser.id).order_by('id')
    userNews = News.objects.filter(userId=currentWebsiteUser.id)
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
def profileSettings(request, nick):
    if request.method == "POST":
        username = request.POST["username"]
        location = request.POST["location"]
        email = request.POST["email"]
        
        user = User.objects.get(username=nick)
        websiteUser = WebsiteUser.objects.get(user=user)

        user.username = username
        user.email = email
        websiteUser.location = location
        user.save()
        websiteUser.save()

        return redirect('/profile/settings/' + user.username)
    else:
        owner = User.objects.get(username=nick)
        owner = WebsiteUser.objects.get(user=owner)

        context = {
            'currentUser': owner,
        }
        if owner.user == request.user:
            return render(request, 'settings.html', context)
        else:
            return redirect('/')

# Events
@login_required
def events(request):
    users = WebsiteUser.objects.all()
    user = WebsiteUser.objects.get(id=request.user.id)
    if request.method == "POST":
        result = request.POST["result"]

        if result == "all":
            request.session["filter"] = "all"
        else:
            request.session["filter"] = "city"
        return redirect('events')
    else:
        users = WebsiteUser.objects.all()
        try:
            filter = request.session["filter"]
        except:
            filter = "none"
        
        if filter == "all":
            events = Event.objects.all().order_by('-id')

        elif filter == "city":
            events = Event.objects.filter(location__contains=user.location).order_by('-id')
        else:
            events = Event.objects.all().order_by('-id')
            try:
                filter = request.session["filter"]
            except:
                filter = "none"

            context = {
                'events': events,
                'users': users,
                'filter': filter,
            }
            return render(request, 'displayServices/events.html', context)
    context = {
        'events': events,
        'users': users,
        'filter': filter,
    }
    return render(request, 'displayServices/events.html', context)

@login_required
def event(request, id):
    user = WebsiteUser.objects.get(id=request.user.id)
    event = Event.objects.get(id=id)
    owner = WebsiteUser.objects.get(id=event.userId)

    if user in event.participants.all():
        participating = True
    else:
        participating = False
        
    context = {
        'event': event,
        'owner': owner,
        'participating': participating,
    }
    return render(request, 'event.html', context)

@login_required
def addEvent(request):
    currentUser = User.objects.get(id=request.user.id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        address = request.POST['address']
        location = request.POST['location']
        dateStart = request.POST['dateStart']
        dateStart = dateStart.split("T")
        dateStart = dateStart[0] + ' ' + dateStart[1]
        dateEnd = request.POST['dateEnd']
        dateEnd = dateEnd.split("T")
        dateEnd = dateEnd[0] + ' ' + dateEnd[1]

        newEvent = Event.objects.create(
            userId=currentWebsiteUser.id,
            title=title, 
            description=description,
            dateStart=dateStart,
            dateEnd=dateEnd,
            location=address,
        )
        newEvent.save()
        currentWebsiteUser = request.session["currentWebsiteUser"]

        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]
        address = address.replace(" ", "_").replace(',', '')
        try:
            checkMarker = Marker.objects.get(title=address)
        except:
            checkMarker = None
        if checkMarker:
            markerType = checkMarker.type
            object = None
            objectType = None
            if checkMarker.jobs.count() != 0:
                object = checkMarker.jobs.first()
                objectType = "jobs"
            elif checkMarker.events.count() != 0:
                object = checkMarker.events.first()
                objectType = "events"
            elif checkMarker.news.count() != 0:
                object = checkMarker.news.first()
                objectType = "news"

            if checkMarker.elements() > 1:
                if markerType != "Home":
                    checkMarker.content += '<a class="object_link" href="/events/' + str(newEvent.id) + '">' + newEvent.title + '</a>\n</br>'
            else:
                checkMarker.content = ''

                if markerType == "Home":
                    checkMarker.content += "<h2>Home</h2>"
                    checkMarker.content += '<a class="object_link" href="/home_list"><h3>Info</h2></a>'
                else:
                    checkMarker.content += f'<a class="object_link" href="/{objectType}/' + str(object.id) + '">' + object.title + '</a>\n</br>'
                    checkMarker.content += '<a class="object_link" href="/events/' + str(newEvent.id) + '">' + newEvent.title + '</a>\n</br>'
                    checkMarker.type = "Multiple"

            checkMarker.events.add(newEvent)
            checkMarker.save()
            newEvent.markerId = checkMarker.id
            newEvent.save()
        else:
            address = address.replace(" ", "_").replace(',', '')
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content=f"""
                <div class="text-center">
                <a class="object_title" href='/events/{newEvent.id}'><h2>{newEvent.title}</h2></a></br>
                <h3 class="object_description">{newEvent.description}</h3>
                </div>
                """,
                type="Event",
            )
            newMarker.events.add(newEvent)
            newMarker.save()

            newEvent.markerId = newMarker.id
            newEvent.save()

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
def deleteEvent(request, id):
    event = Event.objects.get(id=id)
    marker = Marker.objects.get(id=event.markerId)
    markerType = marker.type
    markerElements = marker.elements()
    markerElements -= 1
    marker.save()

    if event.userId == request.user.id:
        newsLinia = '/events/' + str(event.id)
        linie = marker.content.split("</br>")
        for i, linia in enumerate(linie):
            if newsLinia in linia:
                linie.pop(i)
        event.delete()
        
        result = ''
        if markerElements == 1:
            object = None
            objectType = None
            if marker.jobs.count() == 1:
                object = marker.jobs.first()
                objectType = "jobs"
            elif marker.events.count() == 1:
                object = marker.events.first()
                objectType = "events"
            elif marker.news.count() == 1:
                object = marker.news.first()
                objectType = "news"
            
            if markerType == "Home":
                    result += "<h2>Home</h2>"
            else:
                result = f"""
                    <div class="text-center">
                    <a class="object_title" href='/{objectType}/{object.id}'><h2>{object.title}</h2></a></br>
                    <h3 class="object_description">{object.description}</h3>
                    </div>
                    """
                marker.type = objectType.capitalize()
        else:
            if markerType != "Home":
                for i, linia in enumerate(linie):
                    if i == len(linie) - 1:
                        result += linia
                    else:
                        result += linia + '</br>'
            else:
                result = "<h2>Home</h2>"

        if markerElements == 0 and markerType != "Home":
            marker.delete()
        else:
            marker.content = result
            marker.save()

        return redirect('/profile/' + request.user.username)
    else:
        return redirect('/')

@login_required
def editEvent(request, id):
    event = Event.objects.get(id=id)
    marker = Marker.objects.get(id=event.markerId)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        dateStart = request.POST['dateStart']
        dateStart = dateStart.split("T")
        dateStart = dateStart[0] + ' ' + dateStart[1]
        dateEnd = request.POST['dateEnd']
        dateEnd = dateEnd.split("T")
        dateEnd = dateEnd[0] + ' ' + dateEnd[1]

        event.title = title
        event.description = description
        event.dateStart = dateStart
        event.dateEnd = dateEnd
        event.save()

        markerType = marker.type
        result = ''
        if marker.elements() == 1:
            if markerType != "Home":
                result = f"""
                    <div class="text-center">
                    <a class="object_title" href='/events/{event.id}'><h2>{event.title}</h2></a></br>
                    <h3 class="object_description">{event.description}</h3>
                    </div>
                    """
        else:
            if markerType != "Home":
                newsLinia = '/events/' + str(event.id)
                linie = marker.content.split("</br>")
                for i, linia in enumerate(linie):
                    if newsLinia in linia:
                        linie[i] = '<a class="object_link" href="/events/' + str(event.id) + '">' + event.title + '</a>\n'

                for i, linia in enumerate(linie):
                    if i == len(linie) - 1:
                        result += linia
                    else:
                        result += linia + '</br>'

        marker.content = result
        marker.save()
        return redirect('/profile/' + request.user.username)
    else:
        # dodać do start i end time +02:00
        print(event.dateStart.timetz())
        context = {
            'event': event,
        }
        if event.userId == request.user.id:
            return render(request, 'editServices/editEvent.html', context)
        else:
            return redirect('/')

@login_required
def deleteUserFromEvent(request, eventId, userId):
    user = WebsiteUser.objects.get(id=userId)
    event = Event.objects.get(id=eventId)

    event.participants.remove(user)
    event.save()
    return redirect('/jobs/edit_job/' + str(eventId))

@login_required
def participate(request, eventId):
    user = WebsiteUser.objects.get(id=request.user.id)
    event = Event.objects.get(id=eventId)
    
    event.participants.add(user)
    event.save()

    return redirect('/events/' + str(eventId))

@login_required
def unparticipate(request, eventId):
    user = WebsiteUser.objects.get(id=request.user.id)
    event = Event.objects.get(id=eventId)
    
    event.participants.remove(user)
    event.save()

    return redirect('/events/' + str(eventId))

# Jobs
@login_required
def jobs(request):
    users = WebsiteUser.objects.all()
    user = WebsiteUser.objects.get(id=request.user.id)

    if request.method == "POST":
        result = request.POST["result"]

        if result == "all":
            request.session["filter"] = "all"
        else:
            request.session["filter"] = "city"
        return redirect('jobs')
    else:
        users = WebsiteUser.objects.all()
        try:
            filter = request.session["filter"]
        except:
            filter = "none"
        
        if filter == "all":
            jobs = Job.objects.all().order_by('-id')
        elif filter == "city":
            jobs = Job.objects.filter(location__contains=user.location).order_by('-id')
        else:
            jobs = Job.objects.all().order_by('-id')
            try:
                filter = request.session["filter"]
            except:
                filter = "none"

        context = {
            'jobs': jobs,
            'users': users,
            'filter': filter,
        }
        return render(request, 'displayServices/jobs.html', context)

@login_required
def job(request, id):
    user = WebsiteUser.objects.get(id=request.user.id)
    job = Job.objects.get(id=id)
    owner = WebsiteUser.objects.get(id=job.userId)

    if user in job.people.all():
        applied = True
    else:
        applied = False
    print(applied)
    context = {
        'job': job,
        'owner': owner,
        'applied': applied,
    }
    return render(request, 'job.html', context)

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
            checkMarker = Marker.objects.get(title=address)
        except:
            checkMarker = None
        if checkMarker:
            markerType = checkMarker.type
            object = None
            objectType = None
            if checkMarker.jobs.count() != 0:
                object = checkMarker.jobs.first()
                objectType = "jobs"
            elif checkMarker.events.count() != 0:
                object = checkMarker.events.first()
                objectType = "events"
            elif checkMarker.news.count() != 0:
                object = checkMarker.news.first()
                objectType = "news"

            if checkMarker.elements() > 1:
                if markerType != "Home":
                    checkMarker.content += '<a class="object_link" href="/jobs/' + str(newJob.id) + '">' + newJob.title + '</a>\n</br>'
            else:
                checkMarker.content = ''

                if markerType == "Home":
                    checkMarker.content += "<h2>Home</h2>"
                    checkMarker.content += '<a class="object_link" href="/home_list"><h3>Info</h2></a>'
                else:
                    checkMarker.content += f'<a class="object_link" href="/{objectType}/' + str(object.id) + '">' + object.title + '</a>\n</br>'
                    checkMarker.content += '<a class="object_link" href="/jobs/' + str(newJob.id) + '">' + newJob.title + '</a>\n</br>'
                    checkMarker.type = "Multiple"

            checkMarker.jobs.add(newJob)
            checkMarker.save()

            newJob.markerId = checkMarker.id
            newJob.save()
        else:
            address = address.replace(" ", "_").replace(',', '')
            newMarker = Marker.objects.create(
                latitude=lat,
                longitude=lng,
                title=address,
                content=f"""
                <div class="text-center">
                <a class="object_title" href='/jobs/{newJob.id}'><h2>{newJob.title}</h2></a></br>
                <h3 class="object_description">{newJob.description}</h3>
                </div>
                """,
                type="Job",
                icon="/static/images/Praca_30x40.png",
            )
            newMarker.jobs.add(newJob)
            newMarker.save()

            newJob.markerId = newMarker.id
            newJob.save()

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
def deleteJob(request, id):
    job = Job.objects.get(id=id)
    marker = Marker.objects.get(id=job.markerId)
    markerType = marker.type
    markerElements = marker.elements()
    markerElements -= 1
    marker.save()
    objectType = None

    if job.userId == request.user.id:
        newsLinia = '/jobs/' + str(job.id)
        # jeżel linie jest None usuń też markera
        linie = marker.content.split("</br>")
        for i, linia in enumerate(linie):
            if newsLinia in linia:
                linie.pop(i)
        job.delete()
        
        result = ''
        if markerElements == 1:
            result = ''
            object = None
            if marker.jobs.count() == 1:
                object = marker.jobs.first()
                objectType = "jobs"
            elif marker.events.count() == 1:
                object = marker.events.first()
                objectType = "events"
            elif marker.news.count() == 1:
                object = marker.news.first()
                objectType = "news"
                
            if markerType == "Home":
                    result += "<h2>Home</h2>"
            else:
                result = f"""
                    <div class="text-center">
                    <a class="object_title" href='/{objectType}/{object.id}'><h2>{object.title}</h2></a></br>
                    <h3 class="object_description">{object.description}</h3>
                    </div>
                    """
                marker.type = objectType.capitalize()
                
        else:
            if markerType != "Home":
                for i, linia in enumerate(linie):
                    if i == len(linie) - 1:
                        result += linia
                    else:
                        result += linia + '</br>'
            else:
                result = "<h2>Home</h2>"

        if markerElements == 0 and markerType != "Home":
            marker.delete()
        else:
            marker.content = result
            marker.save()
        return redirect('/profile/' + request.user.username)
    else:
        return redirect('/')

@login_required
def editJob(request, id):
    job = Job.objects.get(id=id)
    marker = Marker.objects.get(id=job.markerId)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']

        job.title = title
        job.description = description
        job.save()

        markerType = marker.type
        result = ''
        if marker.elements() == 1:
            if markerType != "Home":
                result = f"""
                    <div class="text-center">
                    <a class="object_title" href='/jobs/{job.id}'><h2>{job.title}</h2></a></br>
                    <h3 class="object_description">{job.description}</h3>
                    </div>
                    """
        else:
            if markerType != "Home":
                newsLinia = '/jobs/' + str(job.id)
                linie = marker.content.split("</br>")
                for i, linia in enumerate(linie):
                    if newsLinia in linia:
                        linie[i] = '<a class="object_link" href="/jobs/' + str(job.id) + '">' + job.title + '</a>\n'

                for i, linia in enumerate(linie):
                    if i == len(linie) - 1:
                        result += linia
                    else:
                        result += linia + '</br>'
                        
        marker.content = result
        marker.save()

        return redirect('/profile/' + request.user.username)
    else:
        context = {
            'job': job,
        }
        if job.userId == request.user.id:
            return render(request, 'editServices/editJob.html', context)
        else:
            return redirect('/')

@login_required
def deleteUserFromJob(request, jobId, userId):
    user = WebsiteUser.objects.get(id=userId)
    job = Job.objects.get(id=jobId)

    job.people.remove(user)
    job.save()
    return redirect('/jobs/edit_job/' + str(jobId))

@login_required
def apply(request, jobId):
    user = WebsiteUser.objects.get(id=request.user.id)
    job = Job.objects.get(id=jobId)
    
    job.people.add(user)
    job.save()
    applied = job.people.count()

    data = {
        'applied': applied,
    }
    # return JsonResponse(data)
    return redirect('/jobs/' + str(jobId))
        
@login_required
def unapply(request, jobId):
    user = WebsiteUser.objects.get(id=request.user.id)
    job = Job.objects.get(id=jobId)
    
    job.people.remove(user)
    job.save()

    applied = job.people.count()
    data = {
        'applied': applied,
    }
    # return JsonResponse(data)
    return redirect('/jobs/' + str(jobId))

# News
@login_required
def news(request):
    user = WebsiteUser.objects.get(id=request.user.id)
    if request.method == "POST":
        result = request.POST["result"]

        if result == "all":
            request.session["filter"] = "all"
        else:
            request.session["filter"] = "city"
        return redirect('news')
    else:
        users = WebsiteUser.objects.all()
        try:
            filter = request.session["filter"]
        except:
            filter = "none"
        
        if filter == "all":
            news = News.objects.all().order_by('-id')
        elif filter == "city":
            news = News.objects.filter(location__contains=user.location).order_by('-id')
        else:
            news = News.objects.all().order_by('-id')
            try:
                filter = request.session["filter"]
            except:
                filter = "none"

        context = {
            'news': news,
            'users': users,
            'filter': filter,
        }
        return render(request, 'displayServices/news.html', context)

@login_required
def oneNews(request, id):
    oneNews = News.objects.get(id=id)
    owner = WebsiteUser.objects.get(id=oneNews.userId)
    context = {
        'oneNews': oneNews,
        'owner': owner,
    }
    return render(request, 'oneNews.html', context)

@login_required
def addNews(request):
    currentUser = User.objects.get(id=request.user.id)
    currentWebsiteUser = WebsiteUser.objects.get(user=currentUser)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        address = request.POST['address']
        location = request.POST['location']

        newNews = News.objects.create(
            userId=currentWebsiteUser.id,
            title=title, 
            description=description,
            createdAtDate=datetime.datetime.today(),
            location=address,
            )
        
        currentWebsiteUser = request.session["currentWebsiteUser"]

        location = location[1:-1]
        locSplit = location.split(", ")
        lat = locSplit[0]
        lng = locSplit[1]
        address = address.replace(" ", "_").replace(',', '')
        try:
            checkMarker = Marker.objects.get(title=address)
        except:
            checkMarker = None
        if checkMarker:
            markerType = checkMarker.type
            object = None
            objectType = None
            if checkMarker.jobs.count() != 0:
                object = checkMarker.jobs.first()
                objectType = "jobs"
            elif checkMarker.events.count() != 0:
                object = checkMarker.events.first()
                objectType = "events"
            elif checkMarker.news.count() != 0:
                object = checkMarker.news.first()
                objectType = "news"

            if checkMarker.elements() > 1:
                if markerType != "Home":
                    checkMarker.content += '<a class="object_link" href="/news/' + str(newNews.id) + '">' + newNews.title + '</a>\n</br>'
            else:
                checkMarker.content = ''

                if markerType == "Home":
                    checkMarker.content += "<h2>Home</h2>"
                    checkMarker.content += '<a class="object_link" href="/home_list"><h3>Info</h2></a>'
                else:
                    checkMarker.content += f'<a class="object_link" href="/{objectType}/' + str(object.id) + '">' + object.title + '</a>\n</br>'
                    checkMarker.content += '<a class="object_link" href="/news/' + str(newNews.id) + '">' + newNews.title + '</a>\n</br>'
                    checkMarker.type = "Multiple"

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
                content=f"""
                <div class="text-center">
                <a class="object_title" href='/news/{newNews.id}'><h2>{newNews.title}</h2></a></br>
                <h3 class="object_description" >{newNews.description}</h3>
                </div>
                """,
                type="News",
            )
            newMarker.news.add(newNews)
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
def deleteNews(request, id):
    news = News.objects.get(id=id)
    marker = Marker.objects.get(id=news.markerId)
    markerType = marker.type
    markerElements = marker.elements()
    markerElements -= 1
    marker.save()
    objectType = None

    if news.userId == request.user.id:
        newsLinia = '/news/' + str(news.id)
        linie = marker.content.split("</br>")
        for i, linia in enumerate(linie):
            if newsLinia in linia:
                linie.pop(i)
        news.delete()
        
        result = ''
        if markerElements == 1:
            result = ''
            object = None
            if marker.jobs.count() == 1:
                object = marker.jobs.first()
                objectType = "jobs"
            elif marker.events.count() == 1:
                object = marker.events.first()
                objectType = "events"
            elif marker.news.count() == 1:
                object = marker.news.first()
                objectType = "news"

            if markerType == "Home":
                    result += "<h2>Home</h2>"
            else:
                result = f"""
                    <div class="text-center">
                    <a class="object_title" href='/{objectType}/{object.id}'><h2>{object.title}</h2></a></br>
                    <h3 class="object_description">{object.description}</h3>
                    </div>
                    """
                marker.type = objectType.capitalize()
        else:
            if markerType != "Home":
                for i, linia in enumerate(linie):
                    if i == len(linie) - 1:
                        result += linia
                    else:
                        result += linia + '</br>'
            else:
                result = "<h2>Home</h2>"
        if markerElements == 0 and markerType != "Home":
            pass
            marker.delete()
        else:
            marker.content = result
            marker.save()
        return redirect('/profile/' + request.user.username)
    else:
        return redirect('/')

@login_required
def editNews(request, id):
    news = News.objects.get(id=id)
    marker = Marker.objects.get(id=news.markerId)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']

        news.title = title
        news.description = description
        news.save()

        markerType = marker.type
        result = ''
        if marker.elements() == 1:
            if markerType != "Home":
                result = f"""
                    <div class="text-center">
                    <a class="object_title" href='/news/{news.id}'><h2>{news.title}</h2></a></br>
                    <h3 class="object_description">{news.description}</h3>
                    </div>
                    """
        else:
            if markerType != "Home":
                newsLinia = '/news/' + str(news.id)
                linie = marker.content.split("</br>")
                for i, linia in enumerate(linie):
                    if newsLinia in linia:
                        linie[i] = '<a class="object_link" href="/news/' + str(news.id) + '">' + news.title + '</a>\n'

                for i, linia in enumerate(linie):
                    if i == len(linie) - 1:
                        result += linia
                    else:
                        result += linia + '</br>'

        marker.content = result
        marker.save()

        return redirect('/profile/' + request.user.username)
    else:
        context = {
            'news': news,
        }
        if news.userId == request.user.id:
            return render(request, 'editServices/editNews.html', context)
        else:
            return redirect('/')
    
# Auth
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        address = request.POST['address']
        location = request.POST['location']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.info(request, 'Passwords don\'t match!')
            return redirect("/register")
        elif len(password) < 6:
            messages.warning(request, "Password must be at least 6 characters long.")
            return redirect('/register')
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
                    content="<h2>Home</h2>",
                    type="Home",
                    icon="/static/images/Home_Icon_47x40.png"
                )
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

def logout(request):
    logout(request)
    return redirect('/')

def changePassword(request):
    if request.method == "POST":
        user = request.user
        oldPassword = request.POST["oldPassword"]
        newPassword1 = request.POST["newPassword1"]
        newPassword2 = request.POST["newPassword2"]
        
        check_password = user.check_password(str(oldPassword))
        
        if check_password:
            if newPassword1 == newPassword2:
                user.set_password(newPassword1)
                user.save()
                return redirect('/profile/settings/' + request.user.username)
            else:
                messages.info(request, 'Password doesn\'t match')
                return redirect('/changePassword/')
        else:
            messages.info(request, 'Your password is wrong!')
            return redirect('/changePassword/')
    else:
        return render(request, 'registration/changePassword.html')
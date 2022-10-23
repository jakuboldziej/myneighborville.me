from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse
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
    userLocation = user.location.replace(" ", "_").replace(',', '')
    marker = Marker.objects.get(title=userLocation)
    jobs = marker.jobs.all()
    events = marker.events.all()
    news = marker.news.all()

    context = {
        'jobs': jobs,
        'events': events,
        'news': news,
    }
    return render(request, 'home_list.html', context)

@login_required
def filter(request):
    if request.POST['action']:
        filter = request.POST['filter']
        result = ''
        if filter == "Wszystko":
            result = "Miasto"
        else:
            result = "Wszystko"
        data = {
            'result': result,
        }
        return JsonResponse(data)

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
        address = request.POST["address"]
        email = request.POST["email"]
        
        news = News.objects.filter(location=address).count()
        jobs = Job.objects.filter(location=address).count()
        events = Event.objects.filter(location=address).count()

        user = User.objects.get(username=nick)
        websiteUser = WebsiteUser.objects.get(user=user)

        if request.POST["changingLocation"]:
            newAddress = address.replace(" ", "_").replace(',', '')
            userLocation = websiteUser.location
            userLocation = userLocation.replace(" ", "_").replace(',', '')
            oldMarker = Marker.objects.get(title=userLocation)
            try:
                if oldMarker.news.all().count() != 0 or oldMarker.jobs.all().count() != 0 or oldMarker.events.all().count() != 0:
                    oldMarker.content = ''

                    if oldMarker.elements() > 1:
                        oldMarker.type = "Multiple"
                        if oldMarker.news.all().count() != 0:
                            for n in oldMarker.news.all():
                                oldMarker.content += '<a class="object_link" href="/events/' + str(n.id) + '">' + n.title + '</a>\n</br>'

                        if oldMarker.jobs.all().count() != 0:
                            for job in oldMarker.jobs.all():
                                oldMarker.content += '<a class="object_link" href="/events/' + str(job.id) + '">' + job.title + '</a>\n</br>'

                        if oldMarker.events.all().count() != 0:
                            for event in oldMarker.events.all():
                                oldMarker.content += '<a class="object_link" href="/events/' + str(event.id) + '">' + event.title + '</a>\n</br>'
                    else:
                        object = None
                        objectType = None
                        if oldMarker.jobs.count() == 1:
                            object = oldMarker.jobs.first()
                            objectType = "jobs"
                        elif oldMarker.events.count() == 1:
                            object = oldMarker.events.first()
                            objectType = "events"
                        elif oldMarker.news.count() == 1:
                            object = oldMarker.news.first()
                            objectType = "news"
                        oldMarker.content = f"""
                            <div class="text-center">
                            <a class="object_title" href='/{objectType}/{object.id}'><h2>{object.title}</h2></a></br>
                            <h3 class="object_description">{object.description}</h3>
                            </div>
                            """
                        oldMarker.type = objectType.capitalize()

                    oldMarker.save()
                    
                else:
                    oldMarker.delete()

                content = ''
                if news != 0 or jobs != 0 or events != 0:
                    content = '<h2>Home</h2><a class="object_link" href="/home_list"><h3>Info</h2></a>'
                else:
                    content = '<h2>Home</h2>'

                location = location[1:-1]
                locSplit = location.split(", ")
                lat = locSplit[0]
                lng = locSplit[1]
                newMarker = Marker.objects.create(
                    latitude=lat,
                    longitude=lng,
                    title=newAddress,
                    content=content,
                    type="Home",
                )
                newMarker.save()
            except:
                content = ''
                if news != 0 or jobs != 0 or events != 0:
                    content = '<h2>Home</h2><a class="object_link" href="/home_list"><h3>Info</h2></a>'
                else:
                    content = '<h2>Home</h2>'

                existingMarker = Marker.objects.get(title=newAddress)
                existingMarker.type = "Home"
                existingMarker.content = content
                existingMarker.save()

            websiteUser.location = address

        user.username = username
        user.email = email
        user.save()
        websiteUser.save()

        return redirect('/profile/settings/' + user.username)
    else:
        owner = User.objects.get(username=nick)
        owner = WebsiteUser.objects.get(user=owner)

        api_key = settings.GOOGLE_API_KEY
        context = {
            'currentUser': owner,
            'api_key': api_key,
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
    events = Event.objects.all()
    
    userLocation = user.location.split(', ')[0]

    context = {
        'events': events,
        'users': users,
        'userLocation': userLocation,
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
                    checkMarker.icon = ""

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
                    if marker.elements() != 0:
                        result = '<h2>Home</h2><a class="object_link" href="/home_list"><h3>Info</h2></a>'
                    else:
                        result = "<h2>Home</h2>"
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
                if marker.elements() != 0:
                    result = '<h2>Home</h2><a class="object_link" href="/home_list"><h3>Info</h2></a>'
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
def participate(request):
    user = WebsiteUser.objects.get(id=request.user.id)
    if request.POST['action'] == 'post':
        result = ''
        id = int(request.POST['eventId'])
        event = Event.objects.get(id=id)
        if event.participants.filter(id=user.id).exists():
            event.participants.remove(user)
            result = event.participants.count()
            event.save()
            participating = False
        else:
            
            event.participants.add(user)
            result = event.participants.count()
            event.save()
            participating = True

        data = {
            'result': result,
            'participating': participating,
        }
        return JsonResponse(data)

# Jobs
@login_required
def jobs(request):
    users = WebsiteUser.objects.all()
    user = WebsiteUser.objects.get(id=request.user.id)
    jobs = Job.objects.all()

    userLocation = user.location.split(', ')[0]

    context = {
        'jobs': jobs,
        'users': users,
        'userLocation': userLocation,
    }
    return render(request, 'displayServices/jobs.html', context)

@login_required
def job(request, id):
    job = Job.objects.get(id=id)
    user = WebsiteUser.objects.get(id=request.user.id)
    owner = WebsiteUser.objects.get(id=job.userId)

    if user in job.people.all():
        applied = True
    else:
        applied = False
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
                    checkMarker.icon = ""

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
                icon="/static/images/Praca_marker.png",
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
                    if marker.elements() != 0:
                        result = '<h2>Home</h2><a class="object_link" href="/home_list"><h3>Info</h2></a>'
                    else:
                        result = "<h2>Home</h2>"
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
                if marker.elements() != 0:
                    result = '<h2>Home</h2><a class="object_link" href="/home_list"><h3>Info</h2></a>'
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
def apply(request):
    user = WebsiteUser.objects.get(id=request.user.id)
    if request.POST['action'] == 'post':
        result = ''
        id = int(request.POST['jobId'])
        job = Job.objects.get(id=id)
        if job.people.filter(id=user.id).exists():
            job.people.remove(user)
            result = job.people.count()
            job.save()
            applied = False
        else:
            
            job.people.add(user)
            result = job.people.count()
            job.save()
            applied = True

        data = {
            'result': result,
            'applied': applied,
        }
        return JsonResponse(data)
        
# News
@login_required
def news(request):
    users = WebsiteUser.objects.all()
    user = WebsiteUser.objects.get(id=request.user.id)
    news = News.objects.all()

    userLocation = user.location.split(', ')[0]

    context = {
        'news': news,
        'users': users,
        'userLocation': userLocation,
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
        newNews.save()
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
                    checkMarker.icon = ""

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
                if marker.elements() != 0:
                    result = '<h2>Home</h2><a class="object_link" href="/home_list"><h3>Info</h2></a>'
                else:
                    result = "<h2>Home</h2>"
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
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            firstName = request.POST['firstName']
            lastName = request.POST['lastName']
            email = request.POST['email']
            address = request.POST['address']
            location = request.POST['location']
            password = request.POST['password']
            
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
                    icon="/static/images/Home_marker.png"
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

def logoutView(request):
    logout(request)
    return redirect('/')

def changePassword(request):
    if request.method == "POST":
        user = request.user
        oldPassword = request.POST["oldPassword"]
        newPassword1 = request.POST["newPassword1"]
        
        check_password = user.check_password(str(oldPassword))
        
        if check_password:
            user.set_password(newPassword1)
            user.save()
            return redirect('/profile/settings/' + request.user.username)
        else:
            messages.info(request, 'Your old password is wrong!')
            return redirect('/changePassword/')
    else:
        return render(request, 'registration/changePassword.html')
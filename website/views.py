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
def news(request):
    users = WebsiteUser.objects.all()
    news = News.objects.all().order_by('-id')

    context = {
        'news': news,
        'users': users,
    }
    return render(request, 'displayServices/news.html', context)

@login_required
def events(request):
    users = WebsiteUser.objects.all()
    events = Event.objects.all().order_by('-id')

    context = {
        'events': events,
        'users': users,
    }
    return render(request, 'displayServices/events.html', context)

@login_required
def jobs(request):
    users = WebsiteUser.objects.all()
    jobs = Job.objects.all().order_by('-id')

    context = {
        'jobs': jobs,
        'users': users,
    }
    return render(request, 'displayServices/jobs.html', context)

# Views with params
@login_required
def profileSettings(request, nick):
    owner = User.objects.get(username=nick)
    owner = WebsiteUser.objects.get(user=owner)

    context = {
        'currentUser': owner,
    }
    if owner.user == request.user:
        return render(request, 'settings.html', context)
    else:
        return redirect('/')
        
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
            if checkMarker.elements() > 1:
                checkMarker.content += '<a class="object_link" href="/events/' + str(newEvent.id) + '">' + newEvent.title + '</a>\n</br>'
            else:
                checkMarker.content = ''
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
                checkMarker.content += f'<a class="object_link" href="/{objectType}/' + str(object.id) + '">' + object.title + '</a>\n</br>'
                checkMarker.content += '<a class="object_link" href="/events/' + str(newEvent.id) + '">' + newEvent.title + '</a>\n</br>'

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
            if checkMarker.elements() > 1:
                checkMarker.content += '<a class="object_link" href="/news/' + str(newNews.id) + '">' + newNews.title + '</a>\n</br>'
            else:
                checkMarker.content = ''
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
                checkMarker.content += f'<a class="object_link" href="/{objectType}/' + str(object.id) + '">' + object.title + '</a>\n</br>'
                checkMarker.content += '<a class="object_link" href="/news/' + str(newNews.id) + '">' + newNews.title + '</a>\n</br>'

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
            if checkMarker.elements() > 1:
                checkMarker.content += '<a class="object_link" href="/jobs/' + str(newJob.id) + '">' + newJob.title + '</a>\n</br>'
            else:
                checkMarker.content = ''
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
                checkMarker.content += f'<a class="object_link" href="/{objectType}/' + str(object.id) + '">' + object.title + '</a>\n</br>'
                checkMarker.content += '<a class="object_link" href="/jobs/' + str(newJob.id) + '">' + newJob.title + '</a>\n</br>'

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
        if event.userId == request.user.id:
            return render(request, 'editServices/editEvent.html', context)
        else:
            return redirect('/')

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
        if job.userId == request.user.id:
            return render(request, 'editServices/editJob.html', context)
        else:
            return redirect('/')

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
        if news.userId == request.user.id:
            return render(request, 'editServices/editNews.html', context)
        else:
            return redirect('/')
    
@login_required
def deleteEvent(request, id):
    event = Event.objects.get(id=id)
    marker = Marker.objects.get(id=event.markerId)
    markerElements = marker.elements()
    markerElements -= 1
    marker.save()

    if event.userId == request.user.id:
        newsLinia = '/events/' + str(event.id)
        # jeżel linie jest None usuń też markera
        linie = marker.content.split("</br>")
        for i, linia in enumerate(linie):
            if newsLinia in linia:
                linie.pop(i)
        event.delete()
        
        result = ''
        if markerElements == 1:
            result = ''
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
            result = f"""
                <div class="text-center">
                <a class="object_title" href='/{objectType}/{object.id}'><h2>{object.title}</h2></a></br>
                <h3 class="object_description">{object.description}</h3>
                </div>
                """
        else:
            for i, linia in enumerate(linie):
                if i == len(linie) - 1:
                    result += linia
                else:
                    result += linia + '</br>'

        if markerElements == 0:
            marker.delete()
        else:
            marker.content = result
            marker.save()

        return redirect('/profile/' + request.user.username)
    else:
        return redirect('/')

@login_required
def deleteJob(request, id):
    job = Job.objects.get(id=id)
    marker = Marker.objects.get(id=job.markerId)
    markerElements = marker.elements()
    markerElements -= 1
    marker.save()

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
            result = f"""
                <div class="text-center">
                <a class="object_title" href='/{objectType}/{object.id}'><h2>{object.title}</h2></a></br>
                <h3 class="object_description">{object.description}</h3>
                </div>
                """
        else:
            for i, linia in enumerate(linie):
                if i == len(linie) - 1:
                    result += linia
                else:
                    result += linia + '</br>'

        if markerElements == 0:
            marker.delete()
        else:
            marker.content = result
            marker.save()
        return redirect('/profile/' + request.user.username)
    else:
        return redirect('/')

@login_required
def deleteNews(request, id):
    news = News.objects.get(id=id)
    marker = Marker.objects.get(id=news.markerId)
    markerElements = marker.elements()
    markerElements -= 1
    marker.save()

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
            result = f"""
                <div class="text-center">
                <a class="object_title" href='/{objectType}/{object.id}'><h2>{object.title}</h2></a></br>
                <h3 class="object_description">{object.description}</h3>
                </div>
                """
        else:
            for i, linia in enumerate(linie):
                if i == len(linie) - 1:
                    result += linia
                else:
                    result += linia + '</br>'

        if markerElements == 0:
            marker.delete()
        else:
            marker.content = result
            marker.save()
        return redirect('/profile/' + request.user.username)
    else:
        return redirect('/')

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
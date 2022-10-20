from django.db import models
from django.contrib.auth.models import User

class WebsiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class News(models.Model):
    userId = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    createdAtDate = models.DateTimeField()
    location = models.CharField(max_length=100) 
    markerId = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    userId = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    dateStart = models.DateTimeField()
    dateEnd= models.DateTimeField()
    location = models.CharField(max_length=100)
    markerId = models.IntegerField(null=True, blank=True)
    participants = models.ManyToManyField(WebsiteUser)

    def __str__(self):
        return self.title

class Job(models.Model):
    userId = models.IntegerField()
    people = models.ManyToManyField(WebsiteUser)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    location = models.CharField(max_length=100)
    markerId = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

class Marker(models.Model):
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    title = models.CharField(max_length=100, unique=True)
    content = models.TextField(max_length=10000)
    type = models.CharField(max_length=100)
    news = models.ManyToManyField(News, blank=True)
    jobs = models.ManyToManyField(Job, blank=True)
    events = models.ManyToManyField(Event, blank=True)

    def __str__(self):
        return self.title

    def elements(self):
        return self.news.count() + self.jobs.count() + self.events.count()
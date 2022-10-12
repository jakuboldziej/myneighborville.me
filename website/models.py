from django.db import models
from django.contrib.auth.models import User

class WebsiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class News(models.Model):
    user = models.ManyToManyField(WebsiteUser)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    createdAtDate = models.DateField()
    createdAtTime = models.TimeField(auto_now=False, auto_now_add=False)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Event(models.Model):
    user = models.ManyToManyField(WebsiteUser)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    dateStart = models.DateField()
    dateEnd = models.DateField()
    timeStart = models.TimeField(auto_now=False, auto_now_add=False)
    timeEnd = models.TimeField(auto_now=False, auto_now_add=False)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Marker(models.Model):
    users = models.ManyToManyField(WebsiteUser)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    title = models.CharField(max_length=100, unique=True)
    content = models.TextField(max_length=10000)
    type = models.TextField(max_length=100)

    def __str__(self):
        return self.title

class Job(models.Model):
    userId = models.IntegerField()
    people = models.ManyToManyField(WebsiteUser)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.title
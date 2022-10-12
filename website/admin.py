from django.contrib import admin

from .models import WebsiteUser, News, Event, Marker, Job

class WebsiteUserAdmin(admin.ModelAdmin):
    fields = ('user', 'location', 'phoneNumber')
    list_display = ['user', 'location', 'phoneNumber']
admin.site.register(WebsiteUser, WebsiteUserAdmin)

class NewsAdmin(admin.ModelAdmin):
    fields = ('user', 'title', 'description', 'location', 'createdAtDate', 'createdAtTime')
    list_display = ['title', 'description', 'location', 'createdAtDate', 'createdAtTime']
admin.site.register(News, NewsAdmin)

class EventAdmin(admin.ModelAdmin):
    fields = ('user', 'title', 'description', 'dateStart', 'dateEnd', 'timeStart', 'timeEnd', 'location')
    list_display = ['title', 'description', 'dateStart', 'dateEnd', 'timeStart', 'timeEnd', 'location']
admin.site.register(Event, EventAdmin)

class MarkerAdmin(admin.ModelAdmin):
    fields = ('title', 'latitude', 'longitude', 'content', 'users')
    list_display = ['title', 'latitude', 'longitude', 'content']
admin.site.register(Marker, MarkerAdmin)

class JobAdmin(admin.ModelAdmin):
    fields = ('userId', 'title', 'description', 'location')
    list_display = ['userId', 'title', 'description', 'location']
admin.site.register(Job, JobAdmin)
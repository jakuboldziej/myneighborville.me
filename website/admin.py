from django.contrib import admin

from .models import WebsiteUser, News, Event, Marker, Job

class WebsiteUserAdmin(admin.ModelAdmin):
    fields = ('user', 'location', 'phoneNumber')
    list_display = ['user', 'id', 'location', 'phoneNumber']
admin.site.register(WebsiteUser, WebsiteUserAdmin)

class NewsAdmin(admin.ModelAdmin):
    fields = ('user', 'title', 'description', 'location', 'createdAtDate', 'markerId')
    list_display = ['title', 'id', 'description', 'location', 'createdAtDate', 'markerId']
admin.site.register(News, NewsAdmin)

class EventAdmin(admin.ModelAdmin):
    fields = ('user', 'title', 'description', 'location', 'dateStart', 'dateEnd', 'markerId')
    list_display = ['title', 'id', 'description', 'location', 'dateStart', 'dateEnd', 'markerId']
admin.site.register(Event, EventAdmin)

class MarkerAdmin(admin.ModelAdmin):
    fields = ('title', 'type', 'typeId', 'latitude', 'longitude', 'content', 'news', 'jobs', 'events')
    list_display = ['title', 'id', 'type', 'typeId', 'latitude', 'longitude', 'content']
admin.site.register(Marker, MarkerAdmin)

class JobAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'userId', 'location', 'people', 'markerId')
    list_display = ['title', 'description', 'id', 'userId', 'location', 'markerId']
admin.site.register(Job, JobAdmin)
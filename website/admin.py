from django.contrib import admin

from .models import WebsiteUser, News, Event, Marker, Job

class WebsiteUserAdmin(admin.ModelAdmin):
    fields = ('user', 'location', 'phoneNumber')
    list_display = ['user', 'id', 'location', 'phoneNumber']
admin.site.register(WebsiteUser, WebsiteUserAdmin)

class NewsAdmin(admin.ModelAdmin):
    fields = ('userId', 'title','description', 'location', 'createdAtDate', 'markerId')
    list_display = ['title', 'id', 'userId', 'description', 'location', 'createdAtDate', 'markerId']
admin.site.register(News, NewsAdmin)

class EventAdmin(admin.ModelAdmin):
    fields = ('userId', 'title', 'description', 'location', 'dateStart', 'dateEnd', 'markerId', 'participants')
    list_display = ['title', 'id', 'userId', 'description', 'location', 'dateStart', 'dateEnd', 'markerId']
admin.site.register(Event, EventAdmin)

class MarkerAdmin(admin.ModelAdmin):
    fields = ('title', 'type', 'latitude', 'longitude', 'content', 'news', 'jobs', 'events', 'icon')
    list_display = ['title', 'id', 'type','latitude', 'longitude', 'content', 'elements']
admin.site.register(Marker, MarkerAdmin)

class JobAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'userId', 'location', 'people', 'markerId')
    list_display = ['title', 'description', 'id', 'userId', 'location', 'markerId']
admin.site.register(Job, JobAdmin)
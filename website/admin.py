from django.contrib import admin

from .models import WebsiteUser, News, Event, Marker

class WebsiteUserAdmin(admin.ModelAdmin):
    fields = ('user', 'location', 'phoneNumber')
    list_display = ['location', 'phoneNumber']
admin.site.register(WebsiteUser, WebsiteUserAdmin)

class NewsAdmin(admin.ModelAdmin):
    fields = ('user', 'title', 'description')
    list_display = ['title', 'description']
admin.site.register(News, NewsAdmin)

class MarkerAdmin(admin.ModelAdmin):
    fields = ('title', 'latitude', 'longitude', 'content')
    list_display = ['title', 'latitude', 'longitude', 'content']
admin.site.register(Marker, MarkerAdmin)

class EventAdmin(admin.ModelAdmin):
    fields = ('user', 'title', 'description', 'dateStart', 'dateEnd', 'timeStart', 'timeEnd')
    list_display = ['title', 'description', 'dateStart', 'dateEnd', 'timeStart', 'timeEnd']
admin.site.register(Event, EventAdmin)
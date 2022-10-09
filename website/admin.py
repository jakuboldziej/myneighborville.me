from django.contrib import admin

from .models import WebsiteUser

class WebsiteUserAdmin(admin.ModelAdmin):
    fields = ('user', 'location', 'phoneNumber')
    list_display = ['user', 'location', 'phoneNumber']
    
admin.site.register(WebsiteUser, WebsiteUserAdmin)
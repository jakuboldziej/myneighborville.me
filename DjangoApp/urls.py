from django.contrib import admin
from django.urls import path, include
from website import views as wviews


urlpatterns = [
    path('', include('website.urls')),
    path('admin/', admin.site.urls),
]
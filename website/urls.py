from django.urls import path, include

from . import views

urlpatterns = [
    # Views
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('events/', views.events, name='events'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('add_marker/', views.addMarkerView, name="addMarkerView"),
    path('add_news/', views.addNewsView, name="addNewsView"),

    # Events
    path('add_event/', views.addEvent, name="addEvent"),

    # Auth
    path('', include("django.contrib.auth.urls")),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
] 
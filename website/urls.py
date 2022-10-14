from django.urls import path, include

from . import views

urlpatterns = [
    # Views
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('news/', views.news, name='news'),
    path('jobs/', views.jobs, name='jobs'),
    path('events/', views.events, name='events'),
    
    path('profile/settings/<int:id>', views.profileSettings, name='profileSettings'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('news/<int:id>', views.oneNews, name='oneNews'),
    path('events/<int:id>', views.event, name='event'),
    path('jobs/<int:id>', views.job, name='job'),

    # Events
    path('add_event/', views.addEvent, name='addEvent'),
    path('add_news/', views.addNews, name='addNews'),
    path('add_job/', views.addJob, name='addJob'),
    path('add_marker/', views.addMarker, name='addMarker'),


    # Auth
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
] 
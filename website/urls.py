from django.urls import path, include

from . import views

urlpatterns = [
    # Views
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('home_list/', views.home_list, name='home_list'),
    
    # Profile 
    path('profile/settings/<str:nick>', views.profileSettings, name='profileSettings'),
    path('profile/<str:nick>', views.profile, name='profile'),

    # Events
    path('events/', views.events, name='events'),
    path('events/<int:id>', views.event, name='event'),
    path('events/edit_event/<int:id>', views.editEvent, name='editEvent'),
    path('add_event/', views.addEvent, name='addEvent'),
    path('delete_event/<int:id>', views.deleteEvent, name='deleteEvent'),

    # Jobs
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<int:id>', views.job, name='job'),
    path('jobs/edit_job/<int:id>', views.editJob, name='editJob'),
    path('add_job/', views.addJob, name='addJob'),
    path('delete_job/<int:id>', views.deleteJob, name='deleteJob'),
    path('delete_user_from_job/<int:jobId>/<int:userId>', views.deleteUserFromJob, name='deleteUserFromJob'),

    # News  
    path('news/', views.news, name='news'),
    path('news/<int:id>', views.oneNews, name='oneNews'),
    path('news/edit_news/<int:id>', views.editNews, name='editNews'),
    path('add_news/', views.addNews, name='addNews'),
    path('delete_news/<int:id>', views.deleteNews, name='deleteNews'),

    # Auth
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
] 
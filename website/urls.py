from django.urls import path, include

from . import views

urlpatterns = [
    # Views
    path('', views.index, name='index'),
    path('map/', views.map, name='map'),
    path('home_list/', views.home_list, name='home_list'),
    path('filter/', views.filter, name='filter'),

    # Profile 
    path('profile/<str:nick>', views.profile, name='profile'),
    path('profile/settings/<str:nick>', views.profileSettings, name='profileSettings'),

    # Events
    path('events/', views.events, name='events'),
    path('events/<int:id>', views.event, name='event'),
    path('add_event/', views.addEvent, name='addEvent'),
    path('delete_event/<int:id>', views.deleteEvent, name='deleteEvent'),
    path('events/edit_event/<int:id>', views.editEvent, name='editEvent'),
    path('delete_user_from_event/<int:eventId>/<int:userId>', views.deleteUserFromEvent, name='deleteUserFromEvent'),
    path('events/participate/', views.participate, name="participate"),

    # Jobs
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<int:id>', views.job, name='job'),
    path('add_job/', views.addJob, name='addJob'),
    path('delete_job/<int:id>', views.deleteJob, name='deleteJob'),
    path('jobs/edit_job/<int:id>', views.editJob, name='editJob'),
    path('delete_user_from_job/<int:jobId>/<int:userId>', views.deleteUserFromJob, name='deleteUserFromJob'),
    path('jobs/apply/', views.apply, name="apply"),

    # News  
    path('news/', views.news, name='news'),
    path('news/<int:id>', views.oneNews, name='oneNews'),
    path('add_news/', views.addNews, name='addNews'),
    path('delete_news/<int:id>', views.deleteNews, name='deleteNews'),
    path('news/edit_news/<int:id>', views.editNews, name='editNews'),

    # Auth
    path('register/', views.register, name='register'),
    path('logout/', views.logoutView, name='logoutView'),
    path('changePassword/', views.changePassword, name='changePassword'),
    path('', include('django.contrib.auth.urls')),
] 
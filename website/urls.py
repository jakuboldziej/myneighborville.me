from django.urls import path, include

from . import views

urlpatterns = [
    # Views
    path('', views.index, name="index"),
    path('map/', views.map, name='map'),

    # Auth
    path('', include("django.contrib.auth.urls")),
    path('register/', views.register, name="register"),
    path('logout/', views.logout, name='logout'),
] 
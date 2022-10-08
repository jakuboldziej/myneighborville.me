from django.urls import path, include

from . import views

urlpatterns = [
    # Pages
    path('', views.index, name="index"),
    path('logout/', views.logout_view, name='logout')
] 

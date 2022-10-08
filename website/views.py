from django.shortcuts import render, redirect
from django.contrib.auth import logout

# 404 Handling
def view_page_not_found(request, exception):
    return render(request, '404.html')

def index(request):
    context = {
        
    }
    return render(request, 'index.html', context)

# Auth
def logout_view(request):
    logout(request)
    return redirect('/')
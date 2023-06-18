

from django.urls import path
from . import views
from .views import CustomLoginView, search
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('search/', search, name='search'), # Add this line
    path('upload/', views.upload_files, name='upload_files'),
    path('upload_files_page/', views.upload_files_page, name='upload_files_page'),  # Add this line
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

]



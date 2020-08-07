from django.urls import path
from . import views

urlpatterns = [
    path('', views.process_home, name='process_home'),
    path('about/', views.process_about, name='process_about'),
]

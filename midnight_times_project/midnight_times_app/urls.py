from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/<str:keyword>/', views.search_results, name='search_results'),
    path('history/', views.history, name='history'),
]

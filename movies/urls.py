from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_page_view, name='search'),
    
    path('api/search/', views.search_api_view, name='search_api'),
    
    path('movie/<int:pk>/', views.movie_detail_view, name='movie_detail'),
    path('actor/<int:pk>/', views.actor_detail_view, name='actor_detail'),
]
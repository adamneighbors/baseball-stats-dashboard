from django.urls import path
from . import views

app_name = 'playerstats'
urlpatterns = [
    path('', views.home, name='home'),
    path('player/<int:player_id>/<int:year>', views.player_by_year, name='player_by_year'),
    path('search/', views.search_players, name='search_players'),
]

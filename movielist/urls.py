from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.display_home, name = 'display_home'),
    path('add_movie/<id>/<poster_extension>/<title>', views.add_movie, name = 'add_movie'),
    path('query_movie', views.query_movie, name = 'query_movie'),
    path('list_summary/', views.list_summary, name="list_summary"),
    path('filter_movies/', views.filter_movies, name="filter_movies"),
    path('view_movie_info/<movie_id>', views.view_movie_info, name="view_movie_info"),
    path('update_movie/<movie_id>', views.update_movie, name="update_movie"),
    path('delete_movie/<movie_id>', views.delete_movie, name="delete_movie"),
    path('update_poster_path/<movie_id>/<poster_extension>', views.update_poster_path, name="update_poster_path"),
]

"""path('filter_summary/<filtered>/<filtered2>/', views.filter_summary, name="filter-summary"),
path('filter_summary/<filtered>/', views.filter_summary, name="filter-summary"),
path('filter_summary/None/<filtered2>/', views.filter_summary, name="filter-summary-none"),"""
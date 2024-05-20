from django.urls import path

from . import views
from movies.views import CustomLoginView

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path('movie/<int:movie_id>/add_review/', views.add_movie_review, name='add_movie_review'),
    path("your_name/", views.get_name, name="get_name"),
    #path("/logout", views.logout_view(), name="logout"),
    #path('accounts/login/', auth_views.LoginView.as_view(template_name='movies/login.html'), name='login'),
    #path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
]
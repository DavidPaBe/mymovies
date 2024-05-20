from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from movies.models import Movie
from .forms import NameForm
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.contrib.auth import authenticate, login, logout



# Create your views here.
def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return render(request, "name_ok.html", {"form": form})
        else:
            return render(request, "name_ok.html", {"form": form})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, "name.html", {"form": form})

def index(request):
    movies = Movie.objects.all()
    context = {'movie_list': movies}
    return render(request, "index.html", context=context)


def movie_detail(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    context = {'movie': movie}
    return render(request, "movie_detail.html", context=context)
    
def custom_logout_view(request):
    logout(request)
    return redirect('logged_out')
    
class LoggedOutView(TemplateView):
    template_name = 'movies/logged_out.html'
    
class CustomLoginView(LoginView):
    template_name = 'movies/login.html'
    success_url = reverse_lazy('index')

    def get_success_url(self):
        return self.success_url
        
from django.shortcuts import render, redirect
from .models import Movie, MovieReview
from .forms import MovieReviewForm

def add_movie_review(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            review = form.cleaned_data['review']
            movie_review = MovieReview.objects.create(user=request.user, movie=movie, rating=rating, review=review)
            return redirect('movie_detail', movie_id=movie_id)
    else:
        form = MovieReviewForm()
    return render(request, 'add_movie_review.html', {'form': form, 'movie': movie})

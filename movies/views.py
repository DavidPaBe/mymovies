from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from movies.models import Movie, MovieReview, ReviewVote
from .forms import NameForm
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



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
    movie = get_object_or_404(Movie, pk=movie_id)
    context = {'movie': movie}
    return render(request, 'movie_detail.html', {'movie': movie})
    
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


@login_required
def vote_review(request, review_id, vote_type):
    review = get_object_or_404(MovieReview, id=review_id)
    vote_value = 1 if vote_type == 'useful' else -1

    # Check if the user has already voted
    existing_vote = ReviewVote.objects.filter(user=request.user, review=review).first()
    if existing_vote:
        if existing_vote.vote == vote_value:
            return HttpResponseForbidden("You have already voted this way.")
        else:
            # Update the existing vote
            existing_vote.vote = vote_value
            existing_vote.save()
    else:
        # Create a new vote
        ReviewVote.objects.create(user=request.user, review=review, vote=vote_value)

    # Update the counts on the review
    if vote_value == 1:
        review.useful_count += 1
        if existing_vote:
            review.not_useful_count -= 1
    else:
        review.not_useful_count += 1
        if existing_vote:
            review.useful_count -= 1

    review.save()
    return redirect('movie_detail', movie_id=review.movie.pk)
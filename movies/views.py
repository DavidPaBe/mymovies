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
from django.db.models import Avg, Count


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
    
@login_required
def recommended_movies(request):
    user_reviews = MovieReview.objects.filter(user=request.user)
    if user_reviews.exists():
        # Get the genres of movies the user has reviewed positively (rating >= 50)
        liked_genres = Movie.objects.filter(reviews__in=user_reviews, reviews__rating__gte=50).values_list('genres', flat=True)
        # Get movies in the liked genres and exclude movies the user has already reviewed
        recommended_movies = Movie.objects.filter(genres__in=liked_genres).exclude(reviews__user=request.user).annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:10]
    else:
        # If the user has no reviews, recommend top rated movies
        recommended_movies = Movie.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:10]
    
    return render(request, 'recommended_movies.html', {'recommended_movies': recommended_movies})
    
@login_required
def movie_list(request):
    movies = Movie.objects.all()
    
    user_reviews = MovieReview.objects.filter(user=request.user)
    if user_reviews.exists():
        # Obtener los géneros de las películas que el usuario ha calificado positivamente (rating >= 50)
        liked_genres = Movie.objects.filter(reviews__in=user_reviews, reviews__rating__gte=50).values_list('genres', flat=True)
        # Obtener películas en los géneros que le gustaron al usuario y excluir películas ya calificadas por el usuario
        recommended_movies = Movie.objects.filter(Q(genres__in=liked_genres)).exclude(reviews__user=request.user).annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:10]
    else:
        # Si el usuario no tiene reseñas, recomendar las películas mejor calificadas
        recommended_movies = Movie.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:10]
    
    return render(request, 'movie_list.html', {'movie_list': movies, 'recommended_movies': recommended_movies})
    
def get_recommendations(user):
    user_reviews = MovieReview.objects.filter(user=user)
    
    if user_reviews.exists():
        # Si el usuario tiene reseñas, usa la lógica de recomendación personalizada
        # Aquí deberías implementar tu algoritmo de recomendación personalizado
        # Este es solo un ejemplo básico
        movie_scores = Movie.objects.annotate(avg_rating=Avg('moviereview__rating')).order_by('-avg_rating')
        recommendations = movie_scores[:5]
    else:
        # Si el usuario no tiene reseñas, muestra algunas películas populares
        # por ejemplo, las películas con más reseñas
        popular_movies = Movie.objects.annotate(num_reviews=Count('moviereview')).order_by('-num_reviews')
        recommendations = popular_movies[:5]

    return recommendations

@login_required
def recommended_movies(request):
    recommended_movies = Movie.objects.annotate(avg_rating=Avg('moviereview__rating')).order_by('-avg_rating')[:5]
    
    if not recommended_movies.exists():
        recommended_movies = Movie.objects.annotate(num_reviews=Count('moviereview')).order_by('-num_reviews')[:5]

    return render(request, 'movies/recommended_movies.html', {'recommended_movies': recommended_movies})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    reviews = MovieReview.objects.filter(movie=movie)
    
    # Filtrar para excluir la película actual
    recommendations = Movie.objects.annotate(avg_rating=Avg('moviereview__rating')).exclude(pk=movie_id).order_by('-avg_rating')[:5]

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'recommendations': recommendations
    })
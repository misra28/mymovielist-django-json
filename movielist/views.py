from datetime import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection, transaction
from django.db.models import Avg, Max, Min
from movielist.models import ListEntry
from .forms import *
from .models import *
import requests
import pymongo
import urllib.parse


def update_movie(request, movie_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/movielist/home')

    movie = ListEntry.objects.get(movie_id=movie_id, user_id=get_user_id(request))

    form = UpdateEntryForm(request.POST or None, instance=movie)
    if form.is_valid():
        form.save()
        return redirect('display_home')

    return render(request, 'update_movie.html', {'movie': movie, 'form': form})


def delete_movie(request, movie_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/movielist/home')

    movie = ListEntry.objects.get(movie_id=movie_id, user_id=get_user_id(request))
    movie.delete()
    return redirect('display_home')


def display_home(request):
    if not request.user.is_authenticated:
        return render(request, 'home.html', {})
    
    empty_list = False
    movielist = list(ListEntry.objects.filter(user_id=get_user_id(request)))

    if (len(movielist) <= 0):
        empty_list = True
        return render(request, 'home.html', {'empty_list': empty_list})

    for entry in movielist:
        if entry.poster_url == None:
            entry.poster_url = build_movie_dict(request, entry.movie_id)['poster_url']
            entry.save()
        if entry.movie_title == None:
            entry.movie_title = build_movie_dict(request, entry.movie_id)['title']
            entry.save()

    get_movies = sorted(list(movielist), key=lambda d: d.rating, reverse=True)
    returndict = {
        'movielist': get_movies
    }
    return render(request, 'home.html', returndict)


def update_poster_path(request, movie_id, poster_extension):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/movielist/home')
    
    path = 'https://image.tmdb.org/t/p/w500' + poster_extension

    with transaction.atomic(), connection.cursor() as cursor:
        #cursor.execute("""UPDATE movielist_listentry SET poster_url = %s WHERE user_id = %s AND movie_id = %s""", [path, get_user_id(request), movie_id])
        entry = ListEntry.objects.get(user_id=get_user_id(request), movie_id=movie_id)
        entry.poster_url = path


    return HttpResponseRedirect('/movielist/home')


def filter_movies(request):
    if request.method == "POST":
        filtered = request.POST['filtered']
        filtered2 = request.POST['filtered2']
        try:
            startdate = datetime.strptime(filtered, "%m-%d-%Y").date()
        except ValueError:
            startdate = ""
            filtered = ""
        try:
            enddate = datetime.strptime(filtered2, "%m-%d-%Y").date()
        except ValueError:
            enddate = ""
            filtered2 = ""

        if startdate != "" and enddate != "":
            le = ListEntry.objects.filter(date_watched__gte=startdate, date_watched__lte=enddate, user_id=get_user_id(request)).order_by('date_watched')
        elif startdate != "":
            le = ListEntry.objects.filter(date_watched__gte=startdate, user_id=get_user_id(request)).order_by('date_watched')
        elif enddate != "":
            le = ListEntry.objects.filter(date_watched__lte=enddate, user_id=get_user_id(request)).order_by('date_watched')
        else:
            return HttpResponseRedirect('/movielist/home')

        no_result = False

        if le.count() == 0:
            no_result = True

        get_movies = []
        for entry in le:
            if entry.poster_url == None:
                entry.poster_url = build_movie_dict(request, entry.movie_id)['poster_url']
                entry.save()
            if entry.movie_title == None:
                entry.movie_title = build_movie_dict(request, entry.movie_id)['title']
                entry.save()
        get_movies = le

        return render(request, 'home.html', {'filtered': filtered, 'filtered2': filtered2, 'no_result': no_result, 'movielist': get_movies})
    else:
        return HttpResponseRedirect('/movielist/home')


def list_summary(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/movielist/home')
    
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SELECT MIN(rating) FROM movielist_listentry le WHERE user_id = %s", [get_user_id(request)])
        min_rating = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(rating) FROM movielist_listentry le WHERE user_id = %s", [get_user_id(request)])
        max_rating = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(rating) FROM movielist_listentry le WHERE user_id = %s", [get_user_id(request)])
        avg_rating = cursor.fetchone()[0]
    
        min_rating_movies = ListEntry.objects.filter(rating=min_rating, user_id=get_user_id(request))
        max_rating_movies = ListEntry.objects.filter(rating=max_rating, user_id=get_user_id(request))

        min_rating_list = []
        for movie in min_rating_movies:
            title = build_movie_dict(request, movie.movie_id)['title']
            min_rating_list.append(title)

        max_rating_list = []
        for movie in max_rating_movies:
            title = build_movie_dict(request, movie.movie_id)['title']
            max_rating_list.append(title)

    returndict = {
        'searched': "",
        'searched2': "",
        'min_rating': min_rating,
        'max_rating': max_rating,
        'min_rating_movies': min_rating_list,
        'max_rating_movies': max_rating_list,
        'avg_rating': avg_rating,
    }
    return render(request, 'list_summary.html', returndict)


def view_movie_info(request, movie_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/movielist/home')
    
    with transaction.atomic(), connection.cursor() as cursor:
        movie_dict = build_movie_dict(request, movie_id)
        actors = get_movie_actors(movie_id)
        posters = get_movie_posters(movie_id)
        
    returndict = {
        'entry': movie_dict,
        'posters': posters,
        'actors': actors,
    }
    return render(request, 'view_movie_info.html', returndict)


def query_movie(request):
    if not request.user.is_authenticated or request.method == "GET" or request.POST['movie_query'] == '':
        return HttpResponseRedirect('/movielist/home')
    
    q = request.POST['movie_query']
    movie_query = urllib.parse.quote_plus(q)
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_query}&include_adult=false&language=en-US&page=1"

    movie_data = requests.get(url, headers=get_tmdb_headers()).json()
    movie_results = []

    skipped = False

    for movie in movie_data['results']:
        check = ListEntry.objects.filter(movie_id=movie['id'], user_id=get_user_id(request))
        if check.count() > 0 or '/' in movie['title']:
            skipped = True
            continue

        if movie['poster_path'] == None:
            no_poster = True 
        else:
            no_poster = False
        
        try:
            date = movie['release_date']
        except:
            date = None

        movie_dict = {
            'id': movie['id'],
            'title': movie['title'],
            'original_title': movie['original_title'],
            'overview': movie['overview'],
            'poster_path': "https://image.tmdb.org/t/p/w500" + str(movie['poster_path']),
            'poster_extension': str(movie['poster_path'])[1:],
            'release_date': date,
            'no_poster': no_poster,
        }
        movie_results.append(movie_dict)
    
    returndict = {
        'query': q,
        'movie_results': movie_results,
        'skipped': skipped
    }
    return render(request, 'query_movie.html', returndict)
    

def add_movie(request, id, poster_extension, title):
    submitted = False
    if request.method == "POST":
        form = ListEntryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                entry = form.save(commit=False)
                entry.user_id = get_user_id(request)[0]
                entry.movie_id = id
                entry.movie_title = title
                entry.poster_url = "https://image.tmdb.org/t/p/w500/" + poster_extension

            entry.save()
            return redirect('display_home')
    else:
        form = ListEntryForm
        if 'submitted' in request.GET:
            submitted = True
    
    returndict = {
        'form': form,
        'submitted': submitted,
        'poster': "https://image.tmdb.org/t/p/w500/" + poster_extension,
    }
    return render(request, 'add_movie.html', returndict)


def get_movie_actors(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
    actors = requests.get(url, headers=get_tmdb_headers()).json()

    get_actors = []
    for i in range(0, 5):
        path = actors['cast'][i]['profile_path']

        if path == None:
            path = "https://www.theyta.com/profiles/profile_placeholder.png"
        else:
            path = "https://image.tmdb.org/t/p/w500" + str(path)

        actor_info = {
            'name': actors['cast'][i]['name'],
            'profile_path': path
        }
        get_actors.append(actor_info)
    
    return get_actors


def build_movie_dict(request, movie_id):
    try: 
        entry = ListEntry.objects.get(movie_id=movie_id, user_id=get_user_id(request))
    except:
        entry = ListEntry.objects.filter(movie_id=movie_id, user_id=get_user_id(request))
        while entry.count() > 1:
            entry[-1].delete()

    movie = get_movie_json(movie_id)

    genre_list = []
    for genre in movie['genres']:
        genre_list.append(genre['name'])

    return {
        'title': movie['title'],
        'movie_id': movie['id'],
        'original_title': movie['original_title'],
        'overview': movie['overview'],
        'runtime': movie['runtime'],
        'release_date': str(movie['release_date']),
        'poster_url': "https://image.tmdb.org/t/p/w500" + str(movie['poster_path']),
        'poster_extension': str(movie['poster_path'])[1:],
        'date_watched': entry.date_watched,
        'rating': entry.rating,
        'comments': entry.comments,
        'genres': genre_list,
    }


def get_movie_posters(movie_id):
    """Given a movie_id this function will return the title's poster extensions."""

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
    data = requests.get(url, headers=get_tmdb_headers()).json()
    getpaths = []
    for poster in data['posters']:
        path = poster['file_path'][1:]
        getpaths.append(path)
    
    if len(getpaths) > 25:
        getpaths = getpaths[:25]

    return getpaths


def get_movie_json(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
    return requests.get(url, headers=get_tmdb_headers()).json()


def get_tmdb_headers():
    return {
        "accept": "application/json",
        "Authorization": \
        "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3M2EwNmJjMDg5YmE0NTM5MmQ5MmZmMGMyMzRkOGI4OSIsInN1YiI6IjY1ZmE1OGU5YmYzMWYyMDE3ZWZkNDQ1ZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.FB5IdhUHZGlYDPj_Io14s2knhdP_45YSmAsjhPWu20s"
    }


def get_user_id(request):
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SELECT movielist_user.id FROM movielist_user WHERE movielist_user.username = %s", [request.user.username])
        return cursor.fetchone()
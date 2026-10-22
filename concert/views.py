from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
import requests
from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending


def index(request):
    return render(request, "index.html")


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(**form.cleaned_data)
        login(request, user)
        return redirect("index")
    return render(request, "signup.html", {"form":form})


def login_view(request):
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("index")
    return render(request, "login.html", {"form":form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")


def songs(request):
    try:
        response = requests.get(settings.SONGS_URL.rstrip("/") + "/song", timeout=5)
        response.raise_for_status()
        songs = response.json()["songs"]
    except (requests.RequestException, ValueError, KeyError):
        return render(request, "songs.html", {"songs": [], "service_error":"Songs service is temporarily unavailable."}, status=503)
    return render(request, "songs.html", {"songs":songs})


def photos(request):
    try:
        response = requests.get(settings.PICTURES_URL.rstrip("/") + "/picture", timeout=5)
        response.raise_for_status()
        photos = response.json()
    except (requests.RequestException, ValueError):
        return render(request, "photos.html", {"photos": [], "service_error":"Pictures service is temporarily unavailable."}, status=503)
    for photo in photos:
        photo["pic_url"] = photo["pic_url"].replace("http://dummyimage.com/", "https://dummyimage.com/")
    return render(request, "photos.html", {"photos":photos})


@login_required(login_url="login")
def concerts(request):
    statuses = dict(ConcertAttending.objects.filter(user=request.user).values_list("concert_id","attending"))
    return render(request, "concerts.html", {"concerts":[{"concert":c, "status":statuses.get(c.pk,"-")} for c in Concert.objects.order_by("date")]})


@login_required(login_url="login")
def concert_detail(request, id):
    concert = get_object_or_404(Concert, pk=id)
    attendance = concert.attendee.filter(user=request.user).first()
    return render(request, "concert_detail.html", {"concert_details":concert, "status":attendance.attending if attendance else "-", "attending_choices":ConcertAttending.AttendingChoices.choices})


@require_POST
@login_required(login_url="login")
def concert_attendee(request):
    concert = get_object_or_404(Concert, pk=request.POST.get("concert_id"))
    status = request.POST.get("attendee_choice")
    if status not in ConcertAttending.AttendingChoices.values:
        return HttpResponseBadRequest("Invalid attendance choice")
    ConcertAttending.objects.update_or_create(concert=concert, user=request.user, defaults={"attending":status})
    return redirect("concerts")

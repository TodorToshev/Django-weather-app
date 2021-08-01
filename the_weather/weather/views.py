from django.http.response import Http404
from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm
from django.contrib import messages
import urllib.request
import json

import os

# Create your views here.

def index(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data["name"]
            start_url = ("http://api.openweathermap.org/data/2.5/weather?q=" + 
                        new_city + f"&units=metric&appid={os.environ.get('WEATHER-API-KEY')}")
            url = start_url.replace(" ", "+")

            # avoids 404 code from weather provider:
            try:
                source = urllib.request.urlopen(url).read()
                list_of_data = json.loads(source)
            except:
                context = {"form": form, "message": messages.error(request, "City not found.")}
                return render(request, "weather/weather.html", context)

            # checks if the city is already in the DB:
            existing_city_count = City.objects.filter(name=new_city).count()
            if existing_city_count == 0:
                form.save()
            else:
                messages.warning(request, "City already exists.")

    form = CityForm
    cities = City.objects.all()
    weather_data = []

    for city in cities:
        data = {
            "city": city.name,
            "country_code":str(list_of_data["sys"]["country"]),
            "coordinate":str(list_of_data["coord"]["lon"]) + ", " + 
                str(list_of_data["coord"]["lat"]),
            "temp":str(list_of_data["main"]["temp"]) + " C",
            "pressure":str(list_of_data["main"]["pressure"]),
            "humidity":str(list_of_data["main"]["humidity"]),
            "main":str(list_of_data["weather"][0]["main"]),
            "description":str(list_of_data["weather"][0]["description"]),
            "icon":str(list_of_data["weather"][0]["icon"]),
        }
        weather_data.append(data)

    context = {"weather_data": weather_data, "form": form}
    return render(request, "weather/weather.html", context)

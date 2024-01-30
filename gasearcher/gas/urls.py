from django.urls import path

from . import views

urlpatterns = [
    path("", views.start, name="start"),
    path("search", views.search, name="search"),
    path("end", views.end, name="end"),
]

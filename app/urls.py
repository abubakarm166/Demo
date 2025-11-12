from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("demo/", views.demo, name="demo"),
    path("chatbot/", views.demo, name="chatbot"),
    path("api/coach/", views.coach_demo_api, name="coach_demo_api"),
]
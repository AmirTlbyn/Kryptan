from django.urls import path, include

urlpatterns = [
    path("user/", include("users.urls")),
    path("idea/",include("ideas.urls")),
]

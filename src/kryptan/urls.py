from django.urls import path, include

urlpatterns = [
    path("user/", include("urls.users")),
    path("idea/", include("urls.ideas")),
    path("room/", include("urls.directs")),
    path("admin/",include("urls.admins")),
]

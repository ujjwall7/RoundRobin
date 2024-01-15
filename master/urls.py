from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.DashboardLogin.as_view()),
    path("logout/", views.Logout.as_view()),
    path("assigned-tasks/", views.AssignedTask.as_view()),
]

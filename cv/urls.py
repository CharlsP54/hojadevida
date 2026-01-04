from django.urls import path
from .views import mi_cv

urlpatterns = [
    path("", mi_cv, name="mi_cv"),
]

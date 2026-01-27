from django.urls import path
from . import views

urlpatterns = [
    path("<int:idperfil>/", views.cv_detail, name="cv_detail"),
    path("<int:idperfil>/print/", views.cv_print, name="cv_print"),
]

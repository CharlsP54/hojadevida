from django.urls import path
from . import views

urlpatterns = [
    path("", views.cv_home, name="cv_home"),
    path("<int:idperfil>/", views.perfil_detail, name="cv_detail"),
    path("<int:idperfil>/print/", views.cv_print, name="cv_print"),
]

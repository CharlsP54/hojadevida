from django.urls import path
from . import views

urlpatterns = [
    # /cv/  -> página sin datos (sirve perfecto con el redirect de /)
    path("", views.sin_datos, name="cv_home"),

    # /cv/<idperfil>/  -> perfil principal
    path("<int:idperfil>/", views.perfil_detail, name="cv_detail"),

    # /cv/<idperfil>/print/  -> impresión PDF
    path("<int:idperfil>/print/", views.cv_print, name="cv_print"),
]

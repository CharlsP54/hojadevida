from django.urls import path
from . import views

urlpatterns = [
    path("", views.cv_home, name="cv_home"),
    path("sin-datos/", views.sin_datos, name="sin_datos"),

    path("<int:idperfil>/", views.perfil_detail, name="cv_detail"),
    path("<int:idperfil>/print/", views.cv_print, name="cv_print"),

    # Link “Ver Documento / Ver PDF” (redirige al archivo real, firmado si hace falta)
    path("doc/<str:model>/<int:pk>/", views.doc_redirect, name="cv_doc"),
]

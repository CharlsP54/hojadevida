from django.urls import path
from . import views

urlpatterns = [
    # CAMBIO IMPORTANTE: name="home" (antes tenías "cv_home")
    # Esto es necesario porque en views.py hay un "return redirect('home')"
    path("", views.cv_home, name="home"),
    
    path("sin-datos/", views.sin_datos, name="sin_datos"),

    # Tus rutas originales (están perfectas, déjalas así)
    path("<int:idperfil>/", views.perfil_detail, name="cv_detail"),
    path("<int:idperfil>/print/", views.cv_print, name="cv_print"),

    # Redirección de documentos
    path("doc/<str:model>/<int:pk>/", views.doc_redirect, name="cv_doc"),
]
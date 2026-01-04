from django.shortcuts import render
from django.http import Http404
from datetime import date, datetime

from .models import (
    Datospersonales,
    Experiencialaboral,
    Cursosrealizados,
    Productosacademicos,
    Productoslaborales,
    Reconocimientos,
)
HUMAN_LABELS = {
    "descripcionperfil": "Descripción del perfil",
    "perfilactivo": "Perfil activo",
    "apellidos": "Apellidos",
    "nombres": "Nombres",
    "nacionalidad": "Nacionalidad",
    "lugarnacimiento": "Lugar de nacimiento",
    "fechanacimiento": "Fecha de nacimiento",
    "numerocedula": "Número de cédula",
    "sexo": "Sexo",
    "estadocivil": "Estado civil",
    "licenciaconducir": "Licencia de conducir",
    "telefonoconvencional": "Teléfono convencional",
    "telefonofijo": "Teléfono móvil",
    "direcciontrabajo": "Dirección de trabajo",
    "direcciondomiciliaria": "Dirección domiciliaria",
    "sitioweb": "Sitio web",
}

def instance_to_kv(obj, exclude=None):
    """
    Convierte un modelo en lista de (Label, Value) SOLO para campos no vacíos.
    Esto evita hardcodear campos en el HTML y hace que se vea TODO lo que llenaste.
    """
    exclude = set(exclude or [])
    kv = []

    for f in obj._meta.fields:
        name = f.name
        if name in exclude:
            continue

        value = getattr(obj, name, None)

        # ignora vacíos
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue

        # formato simple para fechas
        if isinstance(value, (date, datetime)):
            value = value.strftime("%Y-%m-%d")

        label = HUMAN_LABELS.get(name, name.replace("_", " ").title())
        kv.append((label, value))

    return kv


def mi_cv(request):

    perfil = Datospersonales.objects.filter(perfilactivo=1).first()


    if not perfil:
        return render(request, "sin_datos.html")


    perfil_id = perfil.idperfil


    experiencias = Experiencialaboral.objects.filter(
        idperfilconqueestaactivo=perfil,  # FK
        activarparaqueseveaenfront=True
    ).order_by("-fechainiciogestion")

    cursos = Cursosrealizados.objects.filter(
        idperfilconqueestaactivo=perfil,  # FK
        activarparaqueseveaenfront=True
    ).order_by("-fechafin")

    productos_academicos = Productosacademicos.objects.filter(
        idperfilconqueestaactivo=perfil,  # FK
        activarparaqueseveaenfront=True
    ).order_by('-idproductoacademico')

    productos_laborales = Productoslaborales.objects.filter(
        idperfilconqueestaactivo=perfil,  # FK
        activarparaqueseveaenfront=True
    )

    reconocimientos = Reconocimientos.objects.filter(
        idperfilconqueestaactivo=perfil,  # FK al perfil
        activarparaqueseveaenfront=True
    ).order_by("-fechareconocimiento")

    # excluir campos “técnicos” (IDs / flags)
    EXCLUDE_TECH = {
        "idperfilconqueestaactivo",
        "activarparaqueseveaenfront",
        "idperfil",
        "idcursorealizado",
        "idexperiencilaboral",
        "idproductoacademico",
        "idproductoslaborales",
        "idreconocimiento",
    }

    context = {
        "perfil": perfil,

        "experiencias": experiencias,
        "cursos": cursos,
        "productos_academicos": productos_academicos,
        "productos_laborales": productos_laborales,
        "reconocimientos": reconocimientos,

        # “detalles completos” (para que el HTML muestre TODO lo no vacío)
        "perfil_kv": instance_to_kv(perfil, exclude={"idperfil"}),

        "exp_det": [(e, instance_to_kv(e, exclude=EXCLUDE_TECH)) for e in experiencias],
        "cur_det": [(c, instance_to_kv(c, exclude=EXCLUDE_TECH)) for c in cursos],
        "pa_det":  [(p, instance_to_kv(p, exclude=EXCLUDE_TECH)) for p in productos_academicos],
        "pl_det":  [(p, instance_to_kv(p, exclude=EXCLUDE_TECH)) for p in productos_laborales],
        "rec_det": [(r, instance_to_kv(r, exclude=EXCLUDE_TECH)) for r in reconocimientos],
    }

    return render(request, "perfil_detail.html", context)

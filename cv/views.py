from __future__ import annotations

from io import BytesIO
import re
import requests
from pypdf import PdfReader

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.http import Http404

from .models import (
    Datospersonales,
    Experiencialaboral,
    Cursosrealizados,
    Productosacademicos,
    Productoslaborales,
    Reconocimientos,
    Ventagarage,
)

# Cloudinary (para firmar URLs si tu cuenta exige signed/strict transformations)
try:
    import cloudinary
    from cloudinary.utils import cloudinary_url
except Exception:  # pragma: no cover
    cloudinary_url = None


# ============================================================
# Cloudinary helpers (firmar + transformar)
# ============================================================

_CLOUDINARY_HOST_RE = re.compile(r"^https?://res\.cloudinary\.com/[^/]+/")

def _is_cloudinary(url: str) -> bool:
    return bool(url) and bool(_CLOUDINARY_HOST_RE.match(url))

def _parse_cloudinary_parts(url: str):
    """
    Devuelve (resource_type, delivery_type, public_id, ext)
    Soporta URLs tipo:
      https://res.cloudinary.com/<cloud>/<resource>/<type>/.../v123/folder/name.pdf
      https://res.cloudinary.com/<cloud>/<resource>/<type>/<transformations>/v123/folder/name
    """
    # ejemplo: /image/upload/...
    m = re.search(r"/(image|raw|video)/(upload|authenticated|private)/", url)
    if not m:
        return None

    resource_type, delivery_type = m.group(1), m.group(2)

    right = url.split(f"/{resource_type}/{delivery_type}/", 1)[1]  # lo que viene después

    # Quitar firma querystring
    right = right.split("?", 1)[0]

    # Separar por '/'
    parts = [p for p in right.split("/") if p]

    # Si hay transformación(s) van antes de v123...
    # Ej: f_jpg,q_auto,w_1200,c_scale,pg_1/v123/...
    while parts and ("," in parts[0] or "_" in parts[0] and parts[0].startswith(("c_", "w_", "q_", "f_"))):
        parts.pop(0)

    # Quitar versión v123 si existe
    if parts and re.match(r"^v\d+$", parts[0]):
        parts.pop(0)

    if not parts:
        return None

    # public_id es todo lo restante (incluye carpetas)
    public_path = "/".join(parts)

    # detectar extensión
    ext = None
    if "." in parts[-1]:
        base, ext = parts[-1].rsplit(".", 1)
        parts[-1] = base
        public_id = "/".join(parts)
    else:
        public_id = public_path

    return (resource_type, delivery_type, public_id, ext)


def _cloudinary_signed_original(url: str) -> str:
    """
    Devuelve URL firmada (si cloudinary_url está disponible), si no, devuelve la original.
    """
    if not _is_cloudinary(url) or cloudinary_url is None:
        return url

    parsed = _parse_cloudinary_parts(url)
    if not parsed:
        return url

    resource_type, delivery_type, public_id, ext = parsed

    # Si ext existe, la pasamos como format para reconstruir
    # (si no, Cloudinary igual sirve, pero esto ayuda)
    built, _ = cloudinary_url(
        public_id,
        resource_type=resource_type,
        type=delivery_type,
        format=ext,
        secure=True,
        sign_url=True,
    )
    return built


def _cloudinary_signed_transform(
    url: str,
    *,
    transformation: list[dict],
    out_format: str | None = None,
) -> str:
    """
    Genera URL firmada con transformación.
    """
    if not _is_cloudinary(url) or cloudinary_url is None:
        return ""  # si no es cloudinary, lo manejamos con fallback fuera

    parsed = _parse_cloudinary_parts(url)
    if not parsed:
        return ""

    resource_type, delivery_type, public_id, ext = parsed

    built, _ = cloudinary_url(
        public_id,
        resource_type=resource_type,
        type=delivery_type,
        format=out_format,          # extensión de salida (ej: jpg)
        transformation=transformation,
        secure=True,
        sign_url=True,              # <-- CLAVE para evitar 401 en strict transformations
    )
    return built


# ============================================================
# Helpers: PDF -> páginas/miniatura
# ============================================================

def _is_pdf_url(file_url: str) -> bool:
    return bool(file_url) and ".pdf" in file_url.lower()

def _count_pdf_pages_from_url(file_url: str, timeout: int = 15) -> int:
    try:
        r = requests.get(file_url, timeout=timeout)
        r.raise_for_status()
        reader = PdfReader(BytesIO(r.content))
        return max(len(reader.pages), 1)
    except Exception:
        return 1

def _build_doc_pages_and_thumb(
    file_url: str,
    *,
    max_pages: int = 20,
    img_width: int = 1200,
    thumb_width: int = 650,
):
    """
    Retorna:
      is_pdf, pages_urls, thumb_url, view_url
    - view_url: URL del archivo “tal cual” (firmada si hace falta).
    - thumb_url: para tarjetas (PDF->pg1 jpg, imagen->misma imagen con resize si possible)
    - pages_urls: para anexos en cv_print (PDF->pg_i jpg, imagen-> [imagen])
    """
    if not file_url:
        return (False, [], "", "")

    # URL para “ver documento” (solo PDF/imagen)
    view_url = _cloudinary_signed_original(file_url)

    # Si NO es PDF, tratamos como imagen/archivo directo
    if not _is_pdf_url(file_url):
        # miniatura: si es cloudinary intentamos firmar un resize, si no, usamos la misma
        thumb = _cloudinary_signed_transform(
            file_url,
            transformation=[{"fetch_format": "auto", "quality": "auto", "width": thumb_width, "crop": "fit"}],
            out_format=None,
        ) or view_url
        return (False, [view_url], thumb, view_url)

    # PDF: miniatura + páginas
    # Miniatura (página 1)
    thumb = _cloudinary_signed_transform(
        file_url,
        transformation=[{"fetch_format": "jpg", "quality": "auto", "width": thumb_width, "crop": "scale", "page": 1}],
        out_format="jpg",
    )

    # Páginas (para anexos)
    pages = _count_pdf_pages_from_url(view_url)
    pages = min(max(pages, 1), max_pages)

    pages_urls = []
    for i in range(1, pages + 1):
        u = _cloudinary_signed_transform(
            file_url,
            transformation=[{"fetch_format": "jpg", "quality": "auto", "width": img_width, "crop": "scale", "page": i}],
            out_format="jpg",
        )
        if u:
            pages_urls.append(u)

    # Si por alguna razón cloudinary_url no generó nada, dejamos vacío (no revienta)
    return (True, pages_urls, thumb or "", view_url)


def _enrich_items(items, *, model_key: str, file_attr: str = "archivo_digital"):
    """
    Agrega a cada obj:
      - file_is_pdf
      - file_thumb_url
      - file_view_url  (ruta interna /cv/doc/<model>/<pk>/)
      - doc_pages       (para anexos en cv_print)
    """
    for obj in items:
        f = getattr(obj, file_attr, None)
        file_url = getattr(f, "url", "") if f else ""

        is_pdf, pages, thumb, view = _build_doc_pages_and_thumb(file_url)

        obj.file_is_pdf = is_pdf
        obj.file_thumb_url = thumb
        obj.doc_pages = pages

        # Link interno “Ver Documento” (evita exponer cloudinary directo y permite firmar siempre)
        obj.file_view_url = reverse("cv_doc", kwargs={"model": model_key, "pk": obj.pk})

    return items


# ============================================================
# Views
# ============================================================

def cv_home(request):
    perfil = (
        Datospersonales.objects
        .filter(activarparaqueseveaenfront=True)
        .order_by("idperfil")
        .first()
    )
    if perfil:
        return redirect("cv_detail", idperfil=perfil.idperfil)
    return render(request, "sin_datos.html")


def sin_datos(request):
    return render(request, "sin_datos.html")


def doc_redirect(request, model: str, pk: int):
    """
    Abre SOLO el archivo (PDF/imagen) en una pestaña.
    Si Cloudinary exige firma, aquí devolvemos URL firmada.
    """
    model_map = {
        "exp": (Experiencialaboral, "archivo_digital"),
        "cur": (Cursosrealizados, "archivo_digital"),
        "rec": (Reconocimientos, "archivo_digital"),
        "gar": (Ventagarage, "archivo_digital"),
    }
    if model not in model_map:
        raise Http404("Documento no encontrado")

    Model, field_name = model_map[model]
    obj = get_object_or_404(Model, pk=pk)

    f = getattr(obj, field_name, None)
    file_url = getattr(f, "url", "") if f else ""
    if not file_url:
        raise Http404("Sin archivo")

    return redirect(_cloudinary_signed_original(file_url))


def perfil_detail(request, idperfil):
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    experiencias = Experiencialaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by("-fechainiciogestion")

    cursos = Cursosrealizados.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by("-fechainicio")

    productos_academicos = Productosacademicos.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by("-idproductoacademico")

    productos_laborales = Productoslaborales.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by("-fechaproducto")

    reconocimientos = Reconocimientos.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by("-fechareconocimiento")

    ventas_garage = Ventagarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activo=True,
    ).order_by("-fechapublicacion")

    # Enriquecer para miniaturas + ver documento + anexos
    _enrich_items(experiencias, model_key="exp")
    _enrich_items(cursos, model_key="cur")
    _enrich_items(reconocimientos, model_key="rec")
    _enrich_items(ventas_garage, model_key="gar")

    context = {
        "perfil": perfil,
        "experiencias": experiencias,
        "cursos": cursos,
        "productos_academicos": productos_academicos,
        "productos_laborales": productos_laborales,
        "reconocimientos": reconocimientos,
        "ventas_garage": ventas_garage,
    }
    return render(request, "perfil_detail.html", context)


def cv_print(request, idperfil):
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    def want(key: str, default: bool):
        if request.GET.get("from_modal") == "true":
            return key in request.GET
        return default

    include_exp = want("exp", True)
    include_edu = want("edu", True)
    include_acad = want("acad", True)
    include_lab = want("lab", True)
    include_rec = want("rec", True)
    include_garage = want("garage", False)

    experiencias = (
        Experiencialaboral.objects.filter(
            idperfilconqueestaactivo=perfil,
            activarparaqueseveaenfront=True,
        ).order_by("-fechainiciogestion")
        if include_exp else []
    )

    cursos = (
        Cursosrealizados.objects.filter(
            idperfilconqueestaactivo=perfil,
            activarparaqueseveaenfront=True,
        ).order_by("-fechainicio")
        if include_edu else []
    )

    productos_academicos = (
        Productosacademicos.objects.filter(
            idperfilconqueestaactivo=perfil,
            activarparaqueseveaenfront=True,
        ).order_by("-idproductoacademico")
        if include_acad else []
    )

    productos_laborales = (
        Productoslaborales.objects.filter(
            idperfilconqueestaactivo=perfil,
            activarparaqueseveaenfront=True,
        ).order_by("-fechaproducto")
        if include_lab else []
    )

    reconocimientos = (
        Reconocimientos.objects.filter(
            idperfilconqueestaactivo=perfil,
            activarparaqueseveaenfront=True,
        ).order_by("-fechareconocimiento")
        if include_rec else []
    )

    ventas_garage = (
        Ventagarage.objects.filter(
            idperfilconqueestaactivo=perfil,
            activo=True,
        ).order_by("-fechapublicacion")
        if include_garage else []
    )

    # Anexos (páginas de PDF como imágenes)
    _enrich_items(experiencias, model_key="exp")
    _enrich_items(cursos, model_key="cur")
    _enrich_items(reconocimientos, model_key="rec")
    _enrich_items(ventas_garage, model_key="gar")

    context = {
        "perfil": perfil,
        "experiencias": experiencias,
        "cursos": cursos,
        "productos_academicos": productos_academicos,
        "productos_laborales": productos_laborales,
        "reconocimientos": reconocimientos,
        "ventas_garage": ventas_garage,
    }
    return render(request, "cv_print.html", context)

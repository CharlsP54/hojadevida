# cv/views.py
from __future__ import annotations

from io import BytesIO
import requests
from pypdf import PdfReader

from django.shortcuts import get_object_or_404, render, redirect

from .models import (
    Datospersonales,
    Experiencialaboral,
    Cursosrealizados,
    Productosacademicos,
    Productoslaborales,
    Reconocimientos,
    Ventagarage,
)

# ============================================================
# Helpers: Cloudinary PDF -> imágenes por página (pg_1, pg_2...)
# ============================================================

def _inject_cloudinary_transform(url: str, transform: str) -> str:
    marker = "/upload/"
    if marker not in url:
        return url
    left, right = url.split(marker, 1)
    return f"{left}{marker}{transform}/{right}"


def _as_cloudinary_image_url(url: str) -> str:
    # Si el archivo está como raw/upload, lo pasamos a image/upload para poder usar pg_1, f_jpg, etc.
    return url.replace("/raw/upload/", "/image/upload/")


def _is_pdf_url(file_url: str) -> bool:
    return bool(file_url) and ".pdf" in file_url.lower()


def _count_pdf_pages_from_url(file_url: str, timeout: int = 15) -> int:
    # Cuenta páginas descargando el PDF; si falla, 1.
    try:
        r = requests.get(file_url, timeout=timeout)
        r.raise_for_status()
        reader = PdfReader(BytesIO(r.content))
        return len(reader.pages) or 1
    except Exception:
        return 1


def _build_doc_pages(
    file_url: str,
    *,
    max_pages: int = 20,
    img_width: int = 1200,
) -> tuple[bool, list[str]]:
    """
    Devuelve:
      - is_pdf: True si es PDF
      - pages_urls: lista de URLs (cada página renderizada como JPG por Cloudinary)
        Si NO es PDF, devuelve [file_url] como única "página".
    """
    if not file_url:
        return (False, [])

    if not _is_pdf_url(file_url):
        return (False, [file_url])

    pages = _count_pdf_pages_from_url(file_url)
    pages = min(max(pages, 1), max_pages)

    base_img_url = _as_cloudinary_image_url(file_url)

    pages_urls: list[str] = []
    for i in range(1, pages + 1):
        transform = f"f_jpg,q_auto,w_{img_width},c_scale,pg_{i}"
        pages_urls.append(_inject_cloudinary_transform(base_img_url, transform))

    return (True, pages_urls)


def _build_thumb_url(file_url: str, *, width: int = 420) -> tuple[bool, str]:
    """
    Devuelve:
      - is_pdf
      - thumb_url: miniatura para cards (PDF => pg_1 jpg; Imagen => misma url)
    """
    if not file_url:
        return (False, "")

    is_pdf = _is_pdf_url(file_url)
    if not is_pdf:
        return (False, file_url)

    base_img_url = _as_cloudinary_image_url(file_url)
    # Miniatura: página 1 del PDF
    transform = f"f_jpg,q_auto,w_{width},c_scale,pg_1"
    thumb = _inject_cloudinary_transform(base_img_url, transform)
    return (True, thumb)


def _enrich_files(items, file_attr: str = "archivo_digital"):
    """
    Agrega atributos dinámicos a cada objeto:
      - obj.file_is_pdf (bool)
      - obj.file_view_url (str)  # abre solo el archivo
      - obj.file_thumb_url (str) # miniatura (pdf => pg_1, imagen => url)
      - obj.doc_is_pdf (bool)
      - obj.doc_pages (list[str]) # páginas para anexos en cv_print
    """
    for obj in items:
        f = getattr(obj, file_attr, None)
        file_url = getattr(f, "url", "") if f else ""

        # View (abrir archivo "puro")
        obj.file_view_url = file_url

        # Thumb
        is_pdf_thumb, thumb_url = _build_thumb_url(file_url)
        obj.file_is_pdf = is_pdf_thumb
        obj.file_thumb_url = thumb_url

        # Pages (anexos en print)
        is_pdf_pages, pages_urls = _build_doc_pages(file_url)
        obj.doc_is_pdf = is_pdf_pages
        obj.doc_pages = pages_urls

    return items


# ============================================
# Views
# ============================================

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

    # Miniaturas + URLs + anexos (para print)
    _enrich_files(experiencias)
    _enrich_files(cursos)
    _enrich_files(reconocimientos)
    _enrich_files(ventas_garage)

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

    # Anexos (doc_pages) solo en las secciones seleccionadas (ya lo controla include_*)
    _enrich_files(experiencias)
    _enrich_files(cursos)
    _enrich_files(reconocimientos)
    _enrich_files(ventas_garage)

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


def sin_datos(request):
    return render(request, "sin_datos.html")

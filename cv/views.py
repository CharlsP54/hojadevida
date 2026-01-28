# cv/views.py

from __future__ import annotations

from io import BytesIO
import requests
from pypdf import PdfReader

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseBadRequest

from .models import (
    Datospersonales,
    Experiencialaboral,
    Cursosrealizados,
    Productosacademicos,
    Productoslaborales,
    Reconocimientos,
    Ventagaraje,
)


# ============================================================
# Helpers: Cloudinary PDF -> imágenes por página (pg_1, pg_2...)
# ============================================================

def _inject_cloudinary_transform(url: str, transform: str) -> str:
    """
    Inserta transformaciones Cloudinary después de /upload/
    Ej:
    https://res.cloudinary.com/.../image/upload/v1/path/file.pdf
    -> https://res.cloudinary.com/.../image/upload/<transform>/v1/path/file.pdf
    """
    marker = "/upload/"
    if marker not in url:
        return url
    left, right = url.split(marker, 1)
    return f"{left}{marker}{transform}/{right}"


def _as_cloudinary_image_url(url: str) -> str:
    """
    Si el archivo está como raw/upload, lo pasamos a image/upload para poder usar pg_1, f_jpg, etc.
    """
    return url.replace("/raw/upload/", "/image/upload/")


def _is_pdf_url(file_url: str) -> bool:
    return bool(file_url) and ".pdf" in file_url.lower()


def _count_pdf_pages_from_url(file_url: str, timeout: int = 15) -> int:
    """
    Cuenta páginas descargando el PDF.
    Si falla (timeout, permisos, etc.), devuelve 1.
    """
    try:
        r = requests.get(file_url, timeout=timeout)
        r.raise_for_status()
        reader = PdfReader(BytesIO(r.content))
        pages = len(reader.pages) or 1
        return pages
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

    # Contar páginas (para meter "documento completo" en el PDF final)
    pages = _count_pdf_pages_from_url(file_url)
    pages = min(max(pages, 1), max_pages)

    base_img_url = _as_cloudinary_image_url(file_url)

    pages_urls: list[str] = []
    for i in range(1, pages + 1):
        # f_jpg -> convierte a imagen
        # q_auto -> calidad automática
        # w_1200,c_scale -> tamaño
        # pg_i -> página i del PDF
        transform = f"f_jpg,q_auto,w_{img_width},c_scale,pg_{i}"
        pages_urls.append(_inject_cloudinary_transform(base_img_url, transform))

    return (True, pages_urls)


def _enrich_with_doc_pages(items, file_attr: str = "archivo_digital"):
    """
    Agrega atributos dinámicos a cada objeto:
      - obj.doc_is_pdf (bool)
      - obj.doc_pages (list[str])  # si pdf => páginas como imágenes, si imagen => [url]
    """
    for obj in items:
        f = getattr(obj, file_attr, None)
        file_url = getattr(f, "url", "") if f else ""
        is_pdf, pages_urls = _build_doc_pages(file_url)
        obj.doc_is_pdf = is_pdf
        obj.doc_pages = pages_urls
    return items


# ============================================
# Views
# ============================================

def perfil_detail(request, idperfil):
    """
    Dashboard principal (tu perfil_detail.html)
    """
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    experiencias = Experiencialaboral.objects.filter(idperfil=perfil).order_by("-fechainiciogestion")
    cursos = Cursosrealizados.objects.filter(idperfil=perfil).order_by("-fechainicio")
    productos_academicos = Productosacademicos.objects.filter(idperfil=perfil).order_by("-idproductosacademicos")
    productos_laborales = Productoslaborales.objects.filter(idperfil=perfil).order_by("-fechaproducto")
    reconocimientos = Reconocimientos.objects.filter(idperfil=perfil).order_by("-idreconocimiento")
    ventas_garage = Ventagaraje.objects.filter(idperfil=perfil).order_by("-fechapublicacion")

    # Esto NO es obligatorio para tu HTML actual, pero ayuda si luego quieres usar doc_pages ahí también.
    # Si no lo usas, no afecta.
    _enrich_with_doc_pages(experiencias)
    _enrich_with_doc_pages(cursos)
    _enrich_with_doc_pages(reconocimientos)

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
    """
    Exporta PDF del CV (cv_print.html) incluyendo anexos:
      - Si hay archivo_digital PDF, mete TODAS las páginas dentro del PDF final (como imágenes).
    """

    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    # Helpers para el modal:
    # Si el modal está activo (from_modal=true), los checkboxes no marcados NO vienen en GET.
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

    experiencias = Experiencialaboral.objects.filter(idperfil=perfil).order_by("-fechainiciogestion") if include_exp else []
    cursos = Cursosrealizados.objects.filter(idperfil=perfil).order_by("-fechainicio") if include_edu else []
    productos_academicos = Productosacademicos.objects.filter(idperfil=perfil).order_by("-idproductosacademicos") if include_acad else []
    productos_laborales = Productoslaborales.objects.filter(idperfil=perfil).order_by("-fechaproducto") if include_lab else []
    reconocimientos = Reconocimientos.objects.filter(idperfil=perfil).order_by("-idreconocimiento") if include_rec else []
    ventas_garage = Ventagaraje.objects.filter(idperfil=perfil).order_by("-fechapublicacion") if include_garage else []

    # IMPORTANTÍSIMO:
    # Esto hace que en el PDF final puedas imprimir el certificado COMPLETO (páginas)
    _enrich_with_doc_pages(experiencias)
    _enrich_with_doc_pages(cursos)
    _enrich_with_doc_pages(reconocimientos)

    # Si en garage guardas archivos también, descomenta:
    # _enrich_with_doc_pages(ventas_garage)

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

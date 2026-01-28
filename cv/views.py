# cv/views.py

from __future__ import annotations

from io import BytesIO
import requests
from pypdf import PdfReader

from django.shortcuts import get_object_or_404, render

from .models import (
    Datospersonales,
    Experiencialaboral,
    Cursosrealizados,
    Productosacademicos,
    Productoslaborales,
    Reconocimientos,
    Ventagarage,   # <-- CORRECTO (sin "j")
)


# ============================================================
# Helpers: Cloudinary PDF -> imágenes por página (pg_1, pg_2...)
# ============================================================

def _inject_cloudinary_transform(url: str, transform: str) -> str:
    """
    Inserta transformaciones Cloudinary después de /upload/
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


def _count_pdf_pages_from_url(file_url: str, timeout: int = 20) -> int:
    """
    Cuenta páginas descargando el PDF. Si falla, devuelve 1.
    """
    try:
        r = requests.get(file_url, timeout=timeout)
        r.raise_for_status()
        reader = PdfReader(BytesIO(r.content))
        return max(len(reader.pages), 1)
    except Exception:
        return 1


def _build_doc_pages(
    file_url: str,
    *,
    max_pages: int = 20,
    img_width: int = 1200,
) -> tuple[bool, list[str]]:
    """
    Retorna:
    - is_pdf: True si el archivo es PDF
    - pages_urls: lista de URLs de páginas (JPG) si es PDF, o [url] si es imagen
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
        # f_jpg: convierte a JPG
        # q_auto: calidad automática
        # w_1200,c_scale: escala a ancho fijo
        # pg_i: página i del PDF
        transform = f"f_jpg,q_auto,w_{img_width},c_scale,pg_{i}"
        pages_urls.append(_inject_cloudinary_transform(base_img_url, transform))

    return (True, pages_urls)


def _enrich_with_doc_pages(items, file_attr: str = "archivo_digital"):
    """
    Agrega propiedades dinámicas:
      obj.doc_is_pdf (bool)
      obj.doc_pages (list[str])
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
    Dashboard principal (perfil_detail.html)
    """
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    # NOTA: tu FK se llama idperfilconqueestaactivo
    experiencias = (
        Experiencialaboral.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechainiciogestion")
    )

    cursos = (
        Cursosrealizados.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechainicio")
    )

    productos_academicos = (
        Productosacademicos.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-idproductoacademico")
    )

    productos_laborales = (
        Productoslaborales.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechaproducto")
    )

    reconocimientos = (
        Reconocimientos.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechareconocimiento")
    )

    ventas_garage = (
        Ventagarage.objects
        .filter(idperfilconqueestaactivo=perfil, activo=True)
        .order_by("-fechapublicacion")
    )

    # (Opcional) Deja listo doc_pages por si luego quieres usarlo también en el detalle.
    _enrich_with_doc_pages(experiencias)
    _enrich_with_doc_pages(cursos)
    _enrich_with_doc_pages(reconocimientos)
    _enrich_with_doc_pages(ventas_garage)

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
    Exporta CV (cv_print.html).
    Incluye anexos: si hay PDF en archivo_digital, inserta sus páginas renderizadas.
    """
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    # Si viene del modal, lo NO marcado no viene en GET
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
        Experiencialaboral.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechainiciogestion")
        if include_exp else []
    )

    cursos = (
        Cursosrealizados.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechainicio")
        if include_edu else []
    )

    productos_academicos = (
        Productosacademicos.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-idproductoacademico")
        if include_acad else []
    )

    productos_laborales = (
        Productoslaborales.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechaproducto")
        if include_lab else []
    )

    reconocimientos = (
        Reconocimientos.objects
        .filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
        .order_by("-fechareconocimiento")
        if include_rec else []
    )

    ventas_garage = (
        Ventagarage.objects
        .filter(idperfilconqueestaactivo=perfil, activo=True)
        .order_by("-fechapublicacion")
        if include_garage else []
    )

    # Clave: preparar anexos para el PDF final
    _enrich_with_doc_pages(experiencias)
    _enrich_with_doc_pages(cursos)
    _enrich_with_doc_pages(reconocimientos)
    _enrich_with_doc_pages(ventas_garage)

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

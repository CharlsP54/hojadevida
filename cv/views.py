# cv/views.py
from __future__ import annotations

import re
from urllib.parse import urlparse
from io import BytesIO

import requests
from pypdf import PdfReader

from django.shortcuts import get_object_or_404, render, redirect

from cloudinary.utils import cloudinary_url  # <-- IMPORTANTE

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
# Cloudinary helpers (soporta URLs protegidas con firma)
# ============================================================

_CLOUDINARY_HOST = "res.cloudinary.com"
_RE_VERSION = re.compile(r"^v\d+$")

def _parse_cloudinary(file_url: str):
    """
    Parsea URLs tipo:
    https://res.cloudinary.com/<cloud>/<resource_type>/<delivery_type>/upload/.../v123/<public_id>.<ext>

    Devuelve:
      (resource_type, delivery_type, public_id, ext|None)
    """
    if not file_url:
        return None

    u = urlparse(file_url)
    if _CLOUDINARY_HOST not in (u.netloc or ""):
        return None

    path = (u.path or "").lstrip("/")
    parts = path.split("/")
    if len(parts) < 5:
        return None

    # parts[0] = cloud_name
    resource_type = parts[1]  # image/raw/video
    delivery_type = parts[2]  # upload / authenticated / private / etc

    # ubicamos "upload"
    try:
        upos = parts.index("upload")
    except ValueError:
        return None

    after = parts[upos + 1 :]

    # Saltar transformaciones hasta encontrar v123
    vpos = None
    for i, seg in enumerate(after):
        if _RE_VERSION.match(seg):
            vpos = i
            break

    public_parts = after[vpos + 1 :] if vpos is not None else after
    public_path = "/".join(public_parts)

    # extraer extensión si existe
    last = public_path.split("/")[-1]
    if "." in last:
        base, ext = public_path.rsplit(".", 1)
        public_id = base
        fmt = ext
    else:
        public_id = public_path
        fmt = None

    return (resource_type, delivery_type, public_id, fmt)

def _signed_cloudinary(public_id: str, *, resource_type: str, delivery_type: str, fmt: str | None, transformation=None) -> str:
    url, _ = cloudinary_url(
        public_id,
        resource_type=resource_type,
        type=delivery_type,
        format=fmt,
        secure=True,
        sign_url=True,
        transformation=transformation,
    )
    return url

def _is_pdf_field(file_field) -> bool:
    if not file_field:
        return False
    name = (getattr(file_field, "name", "") or "").lower()
    url = (getattr(file_field, "url", "") or "").lower()
    return name.endswith(".pdf") or url.endswith(".pdf") or ".pdf" in name or ".pdf" in url

def _count_pdf_pages_from_url(file_url: str, timeout: int = 15) -> int:
    """
    Ojo: si Cloudinary exige firma, aquí debemos contar usando URL firmada.
    """
    try:
        r = requests.get(file_url, timeout=timeout)
        r.raise_for_status()
        reader = PdfReader(BytesIO(r.content))
        return max(1, len(reader.pages) or 1)
    except Exception:
        return 1

def _build_urls_for_file(file_field):
    """
    Devuelve:
      (is_pdf, view_url, thumb_url)
    """
    if not file_field:
        return (False, "", "")

    raw_url = getattr(file_field, "url", "") or ""
    is_pdf = _is_pdf_field(file_field)

    parsed = _parse_cloudinary(raw_url)
    if not parsed:
        # No es cloudinary -> usamos url directo
        return (is_pdf, raw_url, raw_url)

    resource_type, delivery_type, public_id, fmt = parsed

    # VIEW (abrir solo el documento)
    if is_pdf:
        # fuerza formato pdf aunque en la URL no venga extensión
        view_url = _signed_cloudinary(
            public_id,
            resource_type=resource_type,   # suele ser raw o image según cómo suba el storage
            delivery_type=delivery_type,
            fmt="pdf",
            transformation=None,
        )
        # THUMB (miniatura estable: página 1 -> jpg)
        thumb_url = _signed_cloudinary(
            public_id,
            resource_type="image",
            delivery_type=delivery_type,
            fmt="jpg",
            transformation=[{"page": 1}, {"width": 900, "crop": "scale"}, {"quality": "auto"}, {"fetch_format": "jpg"}],
        )
        return (True, view_url, thumb_url)

    # si es imagen
    view_url = _signed_cloudinary(
        public_id,
        resource_type=resource_type,
        delivery_type=delivery_type,
        fmt=fmt,
        transformation=None,
    )
    thumb_url = _signed_cloudinary(
        public_id,
        resource_type="image",
        delivery_type=delivery_type,
        fmt=(fmt or "jpg"),
        transformation=[{"width": 900, "crop": "fill"}, {"quality": "auto"}],
    )
    return (False, view_url, thumb_url)

def _build_doc_pages(file_field, *, max_pages: int = 20, img_width: int = 1200):
    """
    Para export (cv_print): si es PDF -> devuelve lista de URLs de páginas como JPG (firmadas).
    """
    if not file_field:
        return (False, [])

    raw_url = getattr(file_field, "url", "") or ""
    is_pdf = _is_pdf_field(file_field)
    if not is_pdf:
        return (False, [raw_url] if raw_url else [])

    parsed = _parse_cloudinary(raw_url)
    if not parsed:
        # Sin cloudinary, no podemos renderizar páginas fácilmente
        return (True, [])

    resource_type, delivery_type, public_id, _fmt = parsed

    # Para contar páginas, usamos URL firmada del PDF
    pdf_url_signed = _signed_cloudinary(
        public_id,
        resource_type=resource_type,
        delivery_type=delivery_type,
        fmt="pdf",
        transformation=None,
    )

    pages = _count_pdf_pages_from_url(pdf_url_signed)
    pages = min(max(pages, 1), max_pages)

    urls = []
    for i in range(1, pages + 1):
        page_url = _signed_cloudinary(
            public_id,
            resource_type="image",
            delivery_type=delivery_type,
            fmt="jpg",
            transformation=[{"page": i}, {"width": img_width, "crop": "scale"}, {"quality": "auto"}, {"fetch_format": "jpg"}],
        )
        urls.append(page_url)

    return (True, urls)

def _enrich_items(items, file_attr: str = "archivo_digital"):
    """
    Inyecta en cada obj:
      obj.file_is_pdf
      obj.file_view_url
      obj.file_thumb_url
      obj.doc_pages
    """
    for obj in items:
        f = getattr(obj, file_attr, None)

        is_pdf, view_url, thumb_url = _build_urls_for_file(f)
        obj.file_is_pdf = is_pdf
        obj.file_view_url = view_url
        obj.file_thumb_url = thumb_url

        doc_is_pdf, doc_pages = _build_doc_pages(f)
        obj.doc_is_pdf = doc_is_pdf
        obj.doc_pages = doc_pages

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

    # ✅ Miniaturas + Ver PDF + doc_pages (firmado)
    _enrich_items(experiencias)
    _enrich_items(cursos)
    _enrich_items(reconocimientos)
    _enrich_items(ventas_garage)

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

    # ✅ doc_pages firmadas (para anexos en el PDF)
    _enrich_items(experiencias)
    _enrich_items(cursos)
    _enrich_items(reconocimientos)
    _enrich_items(ventas_garage)

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

import io
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML, CSS
from django.contrib.staticfiles import finders
from pypdf import PdfWriter

from .models import (
    Datospersonales,
    Experiencialaboral,
    Cursosrealizados,
    Reconocimientos,
    Productosacademicos,
    Productoslaborales,
    Ventagarage
)

# =========================
# Helpers Cloudinary URLs
# =========================
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")

def _is_probably_image_url(url: str) -> bool:
    u = (url or "").lower()
    return u.endswith(IMAGE_EXTS)

def cloudinary_pdf_view_url(url: str) -> str:
    """
    Fuerza formato PDF si Cloudinary entrega URL sin extensión.
    Si ya termina en .pdf, la deja igual.
    """
    if not url:
        return url
    if url.lower().endswith(".pdf"):
        return url
    # Cloudinary acepta pedir formato por extensión
    return url + ".pdf"

def cloudinary_pdf_thumb_url(url: str) -> str:
    """
    Miniatura (página 1) como JPG usando transformación.
    Inserta la transformación justo después de /upload/
    y fuerza salida JPG.
    """
    if not url:
        return url

    # si ya trae transformaciones, igual funcionará, pero este método es simple
    marker = "/upload/"
    if marker not in url:
        # fallback: al menos intenta JPG
        return url + ".jpg"

    # página 1, ajustar ancho, calidad auto, formato jpg
    transform = "pg_1,w_700,c_fit,q_auto,f_jpg"
    base = url.replace(marker, f"{marker}{transform}/", 1)

    # fuerza salida jpg por extensión
    if base.lower().endswith(".jpg"):
        return base
    return base + ".jpg"

def annotate_media_for_preview(items, field_name="archivo_digital"):
    """
    Agrega a cada item:
      - item.file_is_pdf
      - item.file_view_url
      - item.file_thumb_url
    Sin tocar tu modelo.
    """
    for it in items:
        f = getattr(it, field_name, None)
        if not f:
            it.file_is_pdf = False
            it.file_view_url = ""
            it.file_thumb_url = ""
            continue

        url = getattr(f, "url", "") or ""
        name = (getattr(f, "name", "") or "").lower()

        # Heurística:
        # - si el name incluye .pdf -> PDF
        # - si no, pero NO parece imagen -> intentamos tratarlo como PDF (porque certificados suelen ser PDF)
        is_pdf = (".pdf" in name) or (url and not _is_probably_image_url(url))

        it.file_is_pdf = is_pdf

        if is_pdf:
            it.file_view_url = cloudinary_pdf_view_url(url)
            it.file_thumb_url = cloudinary_pdf_thumb_url(url)
        else:
            it.file_view_url = url
            it.file_thumb_url = url

    return items


# =========================================
# 1. VISTA HOME
# =========================================
def home(request):
    perfil = Datospersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        perfil = Datospersonales.objects.first()

    if perfil:
        return redirect('cv_detail', idperfil=perfil.idperfil)
    return HttpResponse("<h1>No hay perfiles creados en la Base de Datos.</h1>")


# =========================================
# 2. VISTA DASHBOARD WEB
# =========================================
def cv_detail(request, idperfil):
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    experiencias = list(Experiencialaboral.objects.filter(idperfilconqueestaactivo=perfil))
    cursos = list(Cursosrealizados.objects.filter(idperfilconqueestaactivo=perfil))
    reconocimientos = list(Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil))
    productos_academicos = Productosacademicos.objects.filter(idperfilconqueestaactivo=perfil)
    productos_laborales = Productoslaborales.objects.filter(idperfilconqueestaactivo=perfil)
    ventas_garage = list(Ventagarage.objects.filter(idperfilconqueestaactivo=perfil))

    # 🔥 Esto arregla miniaturas + link "Ver Certificado" en Cloudinary
    annotate_media_for_preview(experiencias, "archivo_digital")
    annotate_media_for_preview(cursos, "archivo_digital")
    annotate_media_for_preview(reconocimientos, "archivo_digital")
    annotate_media_for_preview(ventas_garage, "archivo_digital")

    context = {
        'perfil': perfil,
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
    }

    return render(request, 'perfil_detail.html', context)


# =========================================
# 3. VISTA PDF FUSIONADO
# =========================================
def cv_print(request, idperfil):
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    # 1) Filtros
    show_exp = request.GET.get('exp') is not None
    show_edu = request.GET.get('edu') is not None
    show_acad = request.GET.get('acad') is not None
    show_lab = request.GET.get('lab') is not None
    show_rec = request.GET.get('rec') is not None
    show_garage = request.GET.get('garage') is not None

    # por defecto todo activo excepto garage
    if not request.GET:
        show_exp = show_edu = show_acad = show_lab = show_rec = True
        show_garage = False

    # 2) Querysets
    experiencias = Experiencialaboral.objects.filter(idperfilconqueestaactivo=perfil) if show_exp else []
    cursos = Cursosrealizados.objects.filter(idperfilconqueestaactivo=perfil) if show_edu else []
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil) if show_rec else []
    productos_academicos = Productosacademicos.objects.filter(idperfilconqueestaactivo=perfil) if show_acad else []
    productos_laborales = Productoslaborales.objects.filter(idperfilconqueestaactivo=perfil) if show_lab else []
    ventas_garage = Ventagarage.objects.filter(idperfilconqueestaactivo=perfil) if show_garage else []

    context = {
        'perfil': perfil,
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
    }

    # 3) Render HTML
    html_string = render_to_string('cv_print.html', context)
    base_url = request.build_absolute_uri('/')
    html = HTML(string=html_string, base_url=base_url)

    css_path = finders.find("css/print_cv.css")
    stylesheets = [CSS(filename=css_path)] if css_path else []

    # PDF base
    cv_buffer = io.BytesIO()
    html.write_pdf(target=cv_buffer, stylesheets=stylesheets)
    cv_buffer.seek(0)

    # 4) Merge con anexos
    merger = PdfWriter()
    merger.append(cv_buffer)

    def anexar_certificados(queryset):
        for item in queryset:
            f = getattr(item, "archivo_digital", None)
            if not f:
                continue

            try:
                url = getattr(f, "url", None)
                if not url:
                    continue

                # Forzar PDF si Cloudinary no pone extensión
                pdf_url = cloudinary_pdf_view_url(url)

                # Solo anexar si realmente es PDF (por heurística simple)
                if not pdf_url.lower().endswith(".pdf"):
                    continue

                r = requests.get(pdf_url, timeout=30)
                r.raise_for_status()
                merger.append(io.BytesIO(r.content))

            except Exception as e:
                print(f"Error anexando certificado: {e}")

    if show_edu:
        anexar_certificados(cursos)
    if show_exp:
        anexar_certificados(experiencias)
    if show_rec:
        anexar_certificados(reconocimientos)

    # 5) Salida
    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()
    output_buffer.seek(0)

    response = HttpResponse(output_buffer.getvalue(), content_type='application/pdf')
    filename = f"CV_{perfil.nombres or 'perfil'}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

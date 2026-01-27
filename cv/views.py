import io
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string

from weasyprint import HTML, CSS
from django.contrib.staticfiles import finders

from pypdf import PdfWriter

# Importar tus modelos
from .models import (
    Datospersonales, 
    Experiencialaboral, 
    Cursosrealizados, 
    Reconocimientos, 
    Productosacademicos, 
    Productoslaborales, 
    Ventagarage
)

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

    experiencias = Experiencialaboral.objects.filter(idperfilconqueestaactivo=perfil)
    cursos = Cursosrealizados.objects.filter(idperfilconqueestaactivo=perfil)
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil)
    productos_academicos = Productosacademicos.objects.filter(idperfilconqueestaactivo=perfil)
    productos_laborales = Productoslaborales.objects.filter(idperfilconqueestaactivo=perfil)
    ventas_garage = Ventagarage.objects.filter(idperfilconqueestaactivo=perfil)

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

    # 1. Filtros (si existe la clave en GET => marcado)
    show_exp = request.GET.get('exp') is not None
    show_edu = request.GET.get('edu') is not None
    show_acad = request.GET.get('acad') is not None
    show_lab = request.GET.get('lab') is not None
    show_rec = request.GET.get('rec') is not None
    show_garage = request.GET.get('garage') is not None

    # Botón azul directo: por defecto todo activo excepto garage
    if not request.GET:
        show_exp = show_edu = show_acad = show_lab = show_rec = True
        show_garage = False  # cámbialo a True si quieres por defecto

    # 2. Querysets
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

    # 3. Render HTML del template
    html_string = render_to_string('cv_print.html', context)

    # base_url ayuda a resolver rutas (/static, imágenes, etc.)
    base_url = request.build_absolute_uri('/')

    html = HTML(string=html_string, base_url=base_url)

    # ✅ FORZAR CSS por filesystem (lo más estable en Render)
    # Asegúrate que exista: cv/static/css/print_cv.css
    css_path = finders.find("css/print_cv.css")
    stylesheets = [CSS(filename=css_path)] if css_path else []

    # Generar PDF base
    cv_buffer = io.BytesIO()
    html.write_pdf(target=cv_buffer, stylesheets=stylesheets)
    cv_buffer.seek(0)

    # 4. Fusión con PyPDF
    merger = PdfWriter()
    merger.append(cv_buffer)

    def anexar_certificados(queryset):
        for item in queryset:
            if item.archivo_digital:
                try:
                    # Solo anexamos PDFs
                    if item.archivo_digital.name.lower().endswith('.pdf'):
                        merger.append(item.archivo_digital.path)
                except Exception as e:
                    print(f"Error anexando certificado: {e}")

    if show_edu:
        anexar_certificados(cursos)
    if show_exp:
        anexar_certificados(experiencias)
    if show_rec:
        anexar_certificados(reconocimientos)

    # 5. Salida
    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()

    output_buffer.seek(0)
    response = HttpResponse(output_buffer, content_type='application/pdf')
    filename = f"CV_{perfil.nombres}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

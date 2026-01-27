import io
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
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
    # Busca el primer perfil activo
    perfil = Datospersonales.objects.filter(perfilactivo=1).first()
    
    if not perfil:
        # Si no hay activos, trae el primero que exista
        perfil = Datospersonales.objects.first()
    
    if perfil:
        # Redirige usando el nombre 'cv_detail' que definimos en urls.py
        return redirect('cv_detail', idperfil=perfil.idperfil)
    else:
        return HttpResponse("<h1>No hay perfiles creados en la Base de Datos.</h1>")

# =========================================
# 2. VISTA DASHBOARD WEB (RENOMBRADA)
# =========================================
# ANTES SE LLAMABA perfil_detail, AHORA ES cv_detail PARA COINCIDIR CON URLS.PY
def cv_detail(request, idperfil): 
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)
    
    # Consultas
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
    
    # 1. Filtros
    show_exp = request.GET.get('exp', 'on') == 'on'
    show_edu = request.GET.get('edu', 'on') == 'on'
    show_acad = request.GET.get('acad', 'on') == 'on'
    show_lab = request.GET.get('lab', 'on') == 'on'
    show_rec = request.GET.get('rec', 'on') == 'on'
    show_garage = request.GET.get('garage') == 'on'

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

    # 3. Generar PDF Base
    html_string = render_to_string('cv_print.html', context)
    base_url = request.build_absolute_uri('/')
    html = HTML(string=html_string, base_url=base_url)
    
    cv_buffer = io.BytesIO()
    html.write_pdf(target=cv_buffer)
    cv_buffer.seek(0)

    # 4. Fusión con PyPDF
    merger = PdfWriter()
    merger.append(cv_buffer)

    def anexar_certificados(queryset):
        for item in queryset:
            if item.archivo_digital:
                try:
                    if item.archivo_digital.name.lower().endswith('.pdf'):
                        merger.append(item.archivo_digital.path)
                except Exception as e:
                    print(f"Error anexando certificado: {e}")

    if show_edu: anexar_certificados(cursos)
    if show_exp: anexar_certificados(experiencias)
    if show_rec: anexar_certificados(reconocimientos)

    # 5. Salida
    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()
    
    output_buffer.seek(0)
    response = HttpResponse(output_buffer, content_type='application/pdf')
    filename = f"CV_{perfil.nombres}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response
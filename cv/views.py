# cv/views.py
import io
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.urls import reverse
from weasyprint import HTML
from pypdf import PdfWriter

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
# HELPER: Generador de Miniaturas Cloudinary
# ============================================================
def _get_cloudinary_thumbnail(file_url):
    """
    Transforma la URL de un PDF en Cloudinary para obtener 
    una imagen JPG de la primera página.
    """
    if not file_url:
        return None
    
    # Si no es Cloudinary, devolvemos la URL original (para imagenes locales)
    if "cloudinary" not in file_url:
        return file_url

    # Truco de Cloudinary: Cambiar extensión a .jpg y pedir página 1
    # Ejemplo entrada: .../upload/v1234/archivo.pdf
    # Ejemplo salida:  .../upload/w_600,f_jpg,pg_1/v1234/archivo.jpg
    
    try:
        if "/upload/" in file_url:
            base_part, id_part = file_url.split("/upload/")
            # Inyectamos transformaciones: 
            # w_600 (ancho), f_jpg (formato imagen), pg_1 (pagina 1)
            new_url = f"{base_part}/upload/w_600,q_auto,f_jpg,pg_1/{id_part}"
            
            # Aseguramos que termine en .jpg si era .pdf
            if new_url.lower().endswith(".pdf"):
                new_url = new_url[:-4] + ".jpg"
            return new_url
    except Exception:
        return file_url
    
    return file_url

def _enrich_objects(objects):
    """
    Recorre una lista de objetos y les agrega atributos temporales
    para el frontend: .thumbnail, .is_pdf
    """
    for obj in objects:
        if obj.archivo_digital:
            url = obj.archivo_digital.url
            obj.is_pdf = url.lower().endswith('.pdf')
            # Generar miniatura inteligente
            obj.thumbnail = _get_cloudinary_thumbnail(url)
        else:
            obj.is_pdf = False
            obj.thumbnail = None
    return objects

# ============================================================
# VISTAS
# ============================================================

def doc_redirect(request, model, pk):
    """ Redirecciona al archivo original (útil para links cortos) """
    # Mapeo simple de modelos
    MODELS = {
        "exp": Experiencialaboral,
        "cursos": Cursosrealizados,
        "rec": Reconocimientos,
        "garage": Ventagarage,
    }
    ModelClass = MODELS.get(model)
    if not ModelClass:
        raise Http404("Modelo no encontrado")
    
    obj = get_object_or_404(ModelClass, pk=pk)
    if obj.archivo_digital:
        return redirect(obj.archivo_digital.url)
    if getattr(obj, 'rutacertificado', None):
        return redirect(obj.rutacertificado)
    return redirect('home')

def cv_home(request):
    perfil = Datospersonales.objects.filter(activarparaqueseveaenfront=True).first()
    if perfil:
        return redirect("cv_detail", idperfil=perfil.idperfil)
    return HttpResponse("<h1>No hay perfiles activos</h1>")

def perfil_detail(request, idperfil):
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)

    # Consultas
    experiencias = Experiencialaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainiciogestion")
    cursos = Cursosrealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainicio")
    productos_academicos = Productosacademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-idproductoacademico")
    productos_laborales = Productoslaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechaproducto")
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechareconocimiento")
    ventas_garage = Ventagarage.objects.filter(idperfilconqueestaactivo=perfil, activo=True).order_by("-fechapublicacion")

    # Enriquecer con miniaturas para el HTML
    _enrich_objects(experiencias)
    _enrich_objects(cursos)
    _enrich_objects(reconocimientos)
    _enrich_objects(ventas_garage)

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

    # 1. Lógica de Filtros (Checkboxes)
    # Si viene del modal, usamos lo que diga el checkbox. Si no, todo True.
    from_modal = request.GET.get("from_modal") == "true"
    
    def check(key):
        return request.GET.get(key) is not None if from_modal else True

    show_exp = check("exp")
    show_edu = check("edu")
    show_acad = check("acad")
    show_lab = check("lab")
    show_rec = check("rec")
    show_garage = check("garage") if from_modal else False # Garage false por defecto

    # 2. Filtrar Querysets
    experiencias = Experiencialaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainiciogestion") if show_exp else []
    cursos = Cursosrealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainicio") if show_edu else []
    prod_acad = Productosacademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True) if show_acad else []
    prod_lab = Productoslaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True) if show_lab else []
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True) if show_rec else []
    garage = Ventagarage.objects.filter(idperfilconqueestaactivo=perfil, activo=True) if show_garage else []

    # 3. Generar PDF Principal (WeasyPrint)
    context = {
        "perfil": perfil,
        "experiencias": experiencias,
        "cursos": cursos,
        "productos_academicos": prod_acad,
        "productos_laborales": prod_lab,
        "reconocimientos": reconocimientos,
        "ventas_garage": garage,
    }
    
    html_string = render_to_string('cv_print.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    
    main_buffer = io.BytesIO()
    html.write_pdf(main_buffer)
    main_buffer.seek(0)

    # 4. Fusión de Anexos (PyPDF + Requests)
    merger = PdfWriter()
    
    # A) Primero el CV generado
    merger.append(main_buffer)

    # B) Función para descargar y pegar
    def append_attachments(queryset):
        for item in queryset:
            if item.archivo_digital:
                url = item.archivo_digital.url
                if url.lower().endswith(".pdf"):
                    try:
                        # Descargar desde Cloudinary
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            # Crear buffer en memoria para este archivo
                            remote_pdf = io.BytesIO(response.content)
                            merger.append(remote_pdf)
                    except Exception as e:
                        print(f"Error uniendo PDF {url}: {e}")

    # C) Orden de anexos al final
    if show_edu: append_attachments(cursos)
    if show_exp: append_attachments(experiencias)
    if show_rec: append_attachments(reconocimientos)
    if show_garage: append_attachments(garage)

    # 5. Salida Final
    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()
    
    output_buffer.seek(0)
    response = HttpResponse(output_buffer, content_type='application/pdf')
    filename = f"CV_{perfil.nombres}_{perfil.apellidos}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response
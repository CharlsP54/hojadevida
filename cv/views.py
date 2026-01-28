import io
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from weasyprint import HTML
from pypdf import PdfWriter

from .models import (
    Datospersonales, Experiencialaboral, Cursosrealizados,
    Productosacademicos, Productoslaborales, Reconocimientos, Ventagarage
)

def _get_cloudinary_thumbnail(file_url):
    if not file_url or "cloudinary" not in file_url: return file_url
    try:
        if "/upload/" in file_url:
            base_part, id_part = file_url.split("/upload/")
            new_url = f"{base_part}/upload/w_600,q_auto,f_jpg,pg_1/{id_part}"
            if new_url.lower().endswith(".pdf"):
                new_url = new_url[:-4] + ".jpg"
            return new_url
    except Exception: return file_url
    return file_url

def _enrich_objects(objects):
    for obj in objects:
        url_final = None
        if obj.archivo_digital: url_final = obj.archivo_digital.url
        elif getattr(obj, 'rutacertificado', None): url_final = obj.rutacertificado

        if url_final:
            obj.final_url = url_final
            obj.is_pdf = url_final.lower().endswith('.pdf')
            obj.thumbnail = _get_cloudinary_thumbnail(url_final)
        else:
            obj.final_url = None
            obj.is_pdf = False
            obj.thumbnail = None
    return objects

def doc_redirect(request, model, pk):
    MODELS = { "exp": Experiencialaboral, "cursos": Cursosrealizados, "rec": Reconocimientos, "garage": Ventagarage }
    ModelClass = MODELS.get(model)
    if not ModelClass: raise Http404("Modelo no encontrado")
    obj = get_object_or_404(ModelClass, pk=pk)
    if obj.archivo_digital: return redirect(obj.archivo_digital.url)
    if getattr(obj, 'rutacertificado', None): return redirect(obj.rutacertificado)
    return redirect('home')

def cv_home(request):
    perfil = Datospersonales.objects.filter(activarparaqueseveaenfront=True).first()
    if perfil: return redirect("cv_detail", idperfil=perfil.idperfil)
    return sin_datos(request)

def sin_datos(request):
    return HttpResponse("<div style='text-align:center; padding:50px;'><h1>No hay perfiles activos</h1><a href='/admin'>Ir al Admin</a></div>")

def perfil_detail(request, idperfil):
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)
    experiencias = Experiencialaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainiciogestion")
    cursos = Cursosrealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainicio")
    productos_academicos = Productosacademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-idproductoacademico")
    productos_laborales = Productoslaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechaproducto")
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechareconocimiento")
    ventas_garage = Ventagarage.objects.filter(idperfilconqueestaactivo=perfil, activo=True).order_by("-fechapublicacion")

    _enrich_objects(experiencias)
    _enrich_objects(cursos)
    _enrich_objects(reconocimientos)
    _enrich_objects(ventas_garage)

    context = {
        "perfil": perfil, "experiencias": experiencias, "cursos": cursos,
        "productos_academicos": productos_academicos, "productos_laborales": productos_laborales,
        "reconocimientos": reconocimientos, "ventas_garage": ventas_garage,
    }
    return render(request, "perfil_detail.html", context)

def cv_print(request, idperfil):
    perfil = get_object_or_404(Datospersonales, idperfil=idperfil)
    
    # 1. Filtros del Modal (LÓGICA ACTUALIZADA)
    from_modal = request.GET.get("from_modal") == "true"
    def check(key): return request.GET.get(key) is not None if from_modal else True

    show_exp = check("exp")
    show_edu = check("edu")
    show_acad = check("acad") # ✅ Nuevo filtro
    show_lab = check("lab")   # ✅ Nuevo filtro
    show_rec = check("rec")
    show_garage = check("garage") if from_modal else False 

    # 2. Consultas Filtradas
    experiencias = Experiencialaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainiciogestion") if show_exp else []
    cursos = Cursosrealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by("-fechainicio") if show_edu else []
    
    # ✅ Filtrado correcto de productos
    prod_acad = Productosacademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True) if show_acad else []
    prod_lab = Productoslaborales.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True) if show_lab else []
    
    reconocimientos = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True) if show_rec else []
    garage = Ventagarage.objects.filter(idperfilconqueestaactivo=perfil, activo=True) if show_garage else []
    
    _enrich_objects(experiencias)
    _enrich_objects(cursos)
    _enrich_objects(reconocimientos)

    # 3. Generar PDF Principal
    context = {
        "perfil": perfil, "experiencias": experiencias, "cursos": cursos,
        "productos_academicos": prod_acad, "productos_laborales": prod_lab,
        "reconocimientos": reconocimientos, "ventas_garage": garage,
    }
    
    html_string = render_to_string('cv_print.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    main_buffer = io.BytesIO()
    html.write_pdf(main_buffer)
    main_buffer.seek(0)

    # 4. Fusión de Anexos
    merger = PdfWriter()
    merger.append(main_buffer)

    def append_attachments(queryset):
        for item in queryset:
            url_to_download = None
            if item.archivo_digital:
                url_to_download = item.archivo_digital.url
            elif getattr(item, 'rutacertificado', None):
                link = item.rutacertificado
                if link and link.lower().strip().endswith('.pdf'):
                    url_to_download = link

            if url_to_download:
                try:
                    # Descargamos el archivo
                    response = requests.get(url_to_download, timeout=15)
                    if response.status_code == 200:
                        # Lo metemos al merger como PÁGINA NUEVA
                        remote_pdf = io.BytesIO(response.content)
                        merger.append(remote_pdf)
                except Exception as e:
                    print(f"Error uniendo PDF {url_to_download}: {e}")

    # ✅ Aseguramos que se adjunten archivos de todas las secciones
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
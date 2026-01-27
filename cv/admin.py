from django.contrib import admin
from .models import (
    Datospersonales,
    Experiencialaboral,
    Cursosrealizados,
    Reconocimientos,
    Productosacademicos,
    Productoslaborales,
    Ventagarage,
)

# ==========================================
# CONFIGURACIÓN DE BRANDING (QA OBSERVED)
# ==========================================
admin.site.site_header = "Gestión de Perfil Profesional"
admin.site.site_title = "Admin CV"
admin.site.index_title = "Panel de Control"


@admin.register(Datospersonales)
class DatospersonalesAdmin(admin.ModelAdmin):
    list_display = (
        "nombres", "apellidos", "numerocedula", 
        "activarparaqueseveaenfront", "perfilactivo"
    )
    
    list_filter = (
        "activarparaqueseveaenfront",
        "perfilactivo",
        # Filtros de secciones
        "mostrar_experiencia",
        "mostrar_cursos",
        "mostrar_ventagarage",
    )
    
    search_fields = ("nombres", "apellidos", "numerocedula")
    
    fieldsets = (
        ("Información Personal", {
            "fields": (
                ("nombres", "apellidos"),
                ("numerocedula", "nacionalidad"),
                ("fechanacimiento", "lugarnacimiento"),
                ("estadocivil", "sexo"),
                ("licenciaconducir", "foto_perfil_url"),
                "descripcionperfil",
            )
        }),
        ("Contacto y Ubicación", {
            "fields": (
                ("telefonoconvencional", "telefonofijo"),
                "sitioweb",
                ("direcciondomiciliaria", "direcciontrabajo"),
            )
        }),
        ("Configuración", {
            "fields": (
                ("perfilactivo", "activarparaqueseveaenfront"),
                "mostrar_experiencia",
                "mostrar_cursos",
                "mostrar_reconocimientos",
                "mostrar_productos_academicos",
                "mostrar_productos_laborales",
                "mostrar_ventagarage",
            ),
            "classes": ("collapse",), # Ocultable para no saturar
        }),
    )


@admin.register(Experiencialaboral)
class ExperiencialaboralAdmin(admin.ModelAdmin):
    list_display = ("cargodesempenado", "nombrempresa", "fechainiciogestion", "fechafingestion", "activarparaqueseveaenfront")
    list_filter = ("activarparaqueseveaenfront",)
    search_fields = ("cargodesempenado", "nombrempresa")
    # ordering se toma del Model Meta


@admin.register(Cursosrealizados)
class CursosrealizadosAdmin(admin.ModelAdmin):
    list_display = ("nombrecurso", "entidadpatrocinadora", "fechainicio", "totalhoras")
    list_filter = ("activarparaqueseveaenfront",)
    search_fields = ("nombrecurso",)


@admin.register(Reconocimientos)
class ReconocimientosAdmin(admin.ModelAdmin):
    list_display = ("tiporeconocimiento", "entidadpatrocinadora", "fechareconocimiento")
    list_filter = ("activarparaqueseveaenfront",)


@admin.register(Productosacademicos)
class ProductosacademicosAdmin(admin.ModelAdmin):
    list_display = ("nombrerecurso", "clasificador", "activarparaqueseveaenfront")
    list_filter = ("activarparaqueseveaenfront",)


@admin.register(Productoslaborales)
class ProductoslaboralesAdmin(admin.ModelAdmin):
    list_display = ("nombreproducto", "fechaproducto", "activarparaqueseveaenfront")


@admin.register(Ventagarage)
class VentagarageAdmin(admin.ModelAdmin):
    list_display = ("nombreproducto", "precio", "estado", "fechapublicacion", "activo")
    list_filter = ("estado", "activo")
    search_fields = ("nombreproducto",)
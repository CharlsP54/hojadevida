# cv/models.py
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
import os
import uuid

# ============================================================
# Upload helpers (Funciones para renombrar archivos)
# ============================================================

def _upload_uuid(prefix: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return f"{prefix}/{uuid.uuid4().hex}{ext}"

def upload_perfil(instance, filename): return _upload_uuid("perfil", filename)
def upload_experiencia(instance, filename): return _upload_uuid("certificados/experiencia", filename)
def upload_cursos(instance, filename): return _upload_uuid("certificados/cursos", filename)
def upload_logros(instance, filename): return _upload_uuid("certificados/logros", filename)
def upload_garage(instance, filename): return _upload_uuid("garage", filename)


# ============================================================
# VALIDADORES (Lógica de Negocio y Reglas)
# ============================================================

def validar_no_futuro(fecha):
    """Impide seleccionar fechas futuras."""
    if fecha and fecha > date.today():
        raise ValidationError("No se permiten fechas futuras.")

def validar_rango_fechas(inicio, fin):
    """Impide que la fecha de fin sea anterior a la de inicio."""
    if inicio and fin and fin < inicio:
        raise ValidationError("La fecha final debe ser posterior a la inicial.")

def validar_edad_18_100(fecha):
    """
    Valida que la persona tenga entre 18 y 100 años.
    """
    if not fecha:
        return
    
    hoy = date.today()
    # Calculo preciso de edad (considera si ya pasó el cumpleaños este año)
    edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))

    if edad < 18:
        raise ValidationError(f"Debes ser mayor de edad (Tienes {edad} años).")
    if edad > 100:
        raise ValidationError(f"La fecha parece incorrecta, la edad ({edad} años) excede el límite permitido.")

def validar_10_digitos(valor):
    """
    Valida que el campo tenga exactamente 10 números (para cédula y celular).
    """
    if not valor:
        return
    
    if not valor.isdigit():
        raise ValidationError("Este campo solo debe contener números.")
    
    if len(valor) != 10:
        raise ValidationError(f"Debe tener exactamente 10 dígitos (actualmente tiene {len(valor)}).")


class CleanSaveMixin(models.Model):
    class Meta: abstract = True
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


# ============================================================
# MODELOS
# ============================================================

class Datospersonales(CleanSaveMixin, models.Model):
    idperfil = models.BigAutoField(primary_key=True)
    
    # Datos básicos
    nombres = models.CharField(max_length=60, blank=True, null=True)
    apellidos = models.CharField(max_length=60, blank=True, null=True)
    descripcionperfil = models.CharField(max_length=50, blank=True, null=True)
    
    # URL de Foto (Mantenemos tu configuración actual)
    foto_perfil_url = models.URLField(blank=True, null=True, verbose_name="Link Foto Perfil")

    # Otros datos
    perfilactivo = models.IntegerField(blank=True, null=True)
    nacionalidad = models.CharField(max_length=20, blank=True, null=True)
    lugarnacimiento = models.CharField(max_length=60, blank=True, null=True)
    
    # ✅ VALIDACIÓN DE EDAD APLICADA
    fechanacimiento = models.DateField(
        blank=True, 
        null=True, 
        validators=[validar_edad_18_100],
        verbose_name="Fecha de Nacimiento"
    )
    
    # ✅ VALIDACIÓN DE 10 DÍGITOS APLICADA
    numerocedula = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        validators=[validar_10_digitos],
        verbose_name="Cédula"
    )
    
    sexo = models.CharField(max_length=1, blank=True, null=True)
    estadocivil = models.CharField(max_length=50, blank=True, null=True)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)
    
    # Contacto
    # ✅ VALIDACIÓN DE 10 DÍGITOS APLICADA (Celular)
    telefonoconvencional = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        validators=[validar_10_digitos],
        verbose_name="Celular"
    )
    
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True, null=True)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)
    
    # Configuración
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    
    mostrar_experiencia = models.BooleanField(default=True)
    mostrar_cursos = models.BooleanField(default=True)
    mostrar_reconocimientos = models.BooleanField(default=True)
    mostrar_productos_academicos = models.BooleanField(default=True)
    mostrar_productos_laborales = models.BooleanField(default=True)
    mostrar_ventagarage = models.BooleanField(default=True)

    def clean(self):
        # Mantenemos validaciones extra por si acaso
        if self.fechanacimiento: 
            validar_no_futuro(self.fechanacimiento)
            validar_edad_18_100(self.fechanacimiento)

    class Meta:
        db_table = "datospersonales"
        managed = True


class Experiencialaboral(CleanSaveMixin, models.Model):
    idexperiencilaboral = models.BigAutoField(primary_key=True)
    cargodesempenado = models.CharField(max_length=100, blank=True, null=True)
    nombrempresa = models.CharField(max_length=50, blank=True, null=True)
    lugarempresa = models.CharField(max_length=50, blank=True, null=True)
    emailempresa = models.CharField(max_length=100, blank=True, null=True)
    sitiowebempresa = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoempresarial = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoempresarial = models.CharField(max_length=60, blank=True, null=True)
    fechainiciogestion = models.DateField(blank=True, null=True)
    fechafingestion = models.DateField(blank=True, null=True)
    descripcionfunciones = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    rutacertificado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Externo")
    archivo_digital = models.FileField(upload_to=upload_experiencia, blank=True, null=True, verbose_name="Subir PDF/Imagen")
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="experiencias")
    
    def clean(self):
        if self.fechainiciogestion: validar_no_futuro(self.fechainiciogestion)
        if self.fechafingestion: validar_no_futuro(self.fechafingestion)
        if self.fechainiciogestion and self.fechafingestion: validar_rango_fechas(self.fechainiciogestion, self.fechafingestion)

    class Meta:
        db_table = "experiencialaboral"
        managed = True
        ordering = ["-fechainiciogestion"]


class Cursosrealizados(CleanSaveMixin, models.Model):
    idcursorealizado = models.BigAutoField(primary_key=True)
    nombrecurso = models.CharField(max_length=100, blank=True, null=True)
    fechainicio = models.DateField(blank=True, null=True)
    fechafin = models.DateField(blank=True, null=True)
    totalhoras = models.IntegerField(blank=True, null=True)
    descripcioncurso = models.CharField(max_length=100, blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    emailempresapatrocinadora = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    rutacertificado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Externo")
    archivo_digital = models.FileField(upload_to=upload_cursos, blank=True, null=True, verbose_name="Subir PDF/Imagen")
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="cursos")
    
    def clean(self):
        if self.fechainicio: validar_no_futuro(self.fechainicio)
        if self.fechafin: validar_no_futuro(self.fechafin)
        if self.fechainicio and self.fechafin: validar_rango_fechas(self.fechainicio, self.fechafin)

    class Meta:
        db_table = "cursosrealizados"
        managed = True
        ordering = ["-fechainicio"]


class Reconocimientos(CleanSaveMixin, models.Model):
    idreconocimiento = models.BigAutoField(primary_key=True)
    tiporeconocimiento = models.CharField(max_length=20, blank=True, null=True)
    fechareconocimiento = models.DateField(blank=True, null=True)
    descripcionreconocimiento = models.CharField(max_length=100, blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    rutacertificado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Externo")
    archivo_digital = models.FileField(upload_to=upload_logros, blank=True, null=True, verbose_name="Subir PDF/Imagen")
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="reconocimientos")
    
    def clean(self):
        if self.fechareconocimiento: validar_no_futuro(self.fechareconocimiento)

    class Meta:
        db_table = "reconocimientos"
        managed = True
        ordering = ["-fechareconocimiento"]


class Productosacademicos(CleanSaveMixin, models.Model):
    idproductoacademico = models.BigAutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="productos_academicos")
    nombrerecurso = models.CharField(max_length=100, blank=True, null=True)
    clasificador = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    class Meta: db_table = "productosacademicos"


class Productoslaborales(CleanSaveMixin, models.Model):
    idproductoslaborales = models.BigAutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="productos_laborales")
    nombreproducto = models.CharField(max_length=100, blank=True, null=True)
    fechaproducto = models.DateField(blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    
    def clean(self):
        if self.fechaproducto: validar_no_futuro(self.fechaproducto)

    class Meta:
        db_table = "productoslaborales"
        managed = True
        ordering = ["-fechaproducto"]


class Ventagarage(CleanSaveMixin, models.Model):
    ESTADO_CHOICES = [("Bueno", "Bueno"), ("Regular", "Regular")]
    idventagaraje = models.BigAutoField(primary_key=True)
    nombreproducto = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    fechapublicacion = models.DateField()
    imagen = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    archivo_digital = models.FileField(upload_to=upload_garage, blank=True, null=True, verbose_name="Foto Real del Producto")
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="ventas_garage")

    def clean(self):
        if self.fechapublicacion: validar_no_futuro(self.fechapublicacion)
        if self.estado:
            estado_normalizado = self.estado.capitalize()
            if estado_normalizado not in ["Bueno", "Regular"]: raise ValidationError("Estado inválido")
            self.estado = estado_normalizado

    class Meta:
        db_table = "ventagarage"
        managed = True
        ordering = ["-fechapublicacion"]
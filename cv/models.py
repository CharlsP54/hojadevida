from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import date

# =========================
# VALIDADORES (Lógica de Negocio)
# =========================
def validar_no_futuro(fecha):
    """Lanza error si la fecha es mayor a hoy."""
    if fecha and fecha > date.today():
        raise ValidationError("No se permiten fechas futuras (viajes en el tiempo).")

def validar_rango_fechas(inicio, fin):
    """Lanza error si el fin es antes del inicio."""
    if inicio and fin and fin < inicio:
        raise ValidationError("La fecha de finalización no puede ser anterior a la de inicio.")

class CleanSaveMixin(models.Model):
    """
    Mixin para forzar que el método .clean() se ejecute siempre al guardar,
    incluso si se guarda desde código y no desde el Admin.
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean() # Esto dispara las validaciones
        return super().save(*args, **kwargs)

# =========================
# MODELOS
# =========================

class Datospersonales(CleanSaveMixin, models.Model):
    idperfil = models.IntegerField(primary_key=True)
    descripcionperfil = models.CharField(max_length=50, blank=True, null=True)
    perfilactivo = models.IntegerField(blank=True, null=True)
    apellidos = models.CharField(max_length=60, blank=True, null=True)
    nombres = models.CharField(max_length=60, blank=True, null=True)
    nacionalidad = models.CharField(max_length=20, blank=True, null=True)
    lugarnacimiento = models.CharField(max_length=60, blank=True, null=True)
    fechanacimiento = models.DateField(blank=True, null=True)
    numerocedula = models.CharField(max_length=10, blank=True, null=True)
    sexo = models.CharField(max_length=1, blank=True, null=True)
    estadocivil = models.CharField(max_length=50, blank=True, null=True)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)
    telefonoconvencional = models.CharField(max_length=15, blank=True, null=True)
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True, null=True)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)
    foto_perfil_url = models.URLField(blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    
    # Switches
    mostrar_experiencia = models.BooleanField(default=True)
    mostrar_cursos = models.BooleanField(default=True)
    mostrar_reconocimientos = models.BooleanField(default=True)
    mostrar_productos_academicos = models.BooleanField(default=True)
    mostrar_productos_laborales = models.BooleanField(default=True)
    mostrar_ventagarage = models.BooleanField(default=True)

    def clean(self):
        if self.fechanacimiento:
            validar_no_futuro(self.fechanacimiento)

    class Meta:
        db_table = "datospersonales"
        managed = True


class Experiencialaboral(CleanSaveMixin, models.Model):
    idexperiencilaboral = models.IntegerField(primary_key=True)
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
    
    # LINK EXTERNO
    rutacertificado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Externo")
    
    # NUEVO: ARCHIVO (PDF/IMG)
    archivo_digital = models.FileField(upload_to='certificados/experiencia/', blank=True, null=True, verbose_name="Subir PDF/Imagen")
    
    idperfilconqueestaactivo = models.ForeignKey(
        Datospersonales, models.DO_NOTHING, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="experiencias"
    )

    def clean(self):
        if self.fechainiciogestion: validar_no_futuro(self.fechainiciogestion)
        if self.fechafingestion: validar_no_futuro(self.fechafingestion)
        if self.fechafingestion and self.fechainiciogestion:
            validar_rango_fechas(self.fechainiciogestion, self.fechafingestion)

    class Meta:
        db_table = "experiencialaboral"
        managed = True
        ordering = ['-fechainiciogestion']


class Cursosrealizados(CleanSaveMixin, models.Model):
    idcursorealizado = models.IntegerField(primary_key=True)
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
    
    # LINK EXTERNO
    rutacertificado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Externo")
    
    # NUEVO: ARCHIVO (PDF/IMG)
    archivo_digital = models.FileField(upload_to='certificados/cursos/', blank=True, null=True, verbose_name="Subir PDF/Imagen")
    
    idperfilconqueestaactivo = models.ForeignKey(
        Datospersonales, models.DO_NOTHING, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="cursos"
    )

    def clean(self):
        if self.fechainicio: validar_no_futuro(self.fechainicio)
        if self.fechafin: validar_no_futuro(self.fechafin)
        if self.fechainicio and self.fechafin:
            validar_rango_fechas(self.fechainicio, self.fechafin)

    class Meta:
        db_table = "cursosrealizados"
        managed = True
        ordering = ['-fechainicio']


class Reconocimientos(CleanSaveMixin, models.Model):
    idreconocimiento = models.IntegerField(primary_key=True)
    tiporeconocimiento = models.CharField(max_length=20, blank=True, null=True)
    fechareconocimiento = models.DateField(blank=True, null=True)
    descripcionreconocimiento = models.CharField(max_length=100, blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    
    # LINK EXTERNO
    rutacertificado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link Externo")
    
    # NUEVO: ARCHIVO (PDF/IMG)
    archivo_digital = models.FileField(upload_to='certificados/logros/', blank=True, null=True, verbose_name="Subir PDF/Imagen")
    
    idperfilconqueestaactivo = models.ForeignKey(
        Datospersonales, models.DO_NOTHING, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="reconocimientos"
    )

    def clean(self):
        if self.fechareconocimiento:
            validar_no_futuro(self.fechareconocimiento)

    class Meta:
        db_table = "reconocimientos"
        managed = True
        ordering = ['-fechareconocimiento']


class Productosacademicos(CleanSaveMixin, models.Model):
    idproductoacademico = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(
        Datospersonales, models.DO_NOTHING, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="productos_academicos"
    )
    nombrerecurso = models.CharField(max_length=100, blank=True, null=True)
    clasificador = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        db_table = "productosacademicos"
        managed = True


class Productoslaborales(CleanSaveMixin, models.Model):
    idproductoslaborales = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(
        Datospersonales, models.DO_NOTHING, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="productos_laborales"
    )
    nombreproducto = models.CharField(max_length=100, blank=True, null=True)
    fechaproducto = models.DateField(blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)

    def clean(self):
        if self.fechaproducto:
            validar_no_futuro(self.fechaproducto)

    class Meta:
        db_table = "productoslaborales"
        managed = True
        ordering = ['-fechaproducto']


class Ventagarage(CleanSaveMixin, models.Model):
    ESTADO_CHOICES = [
        ("Bueno", "Bueno"),
        ("Regular", "Regular"),
    ]

    idventagaraje = models.IntegerField(primary_key=True)
    nombreproducto = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    fechapublicacion = models.DateField()
    imagen = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField()
    
    # NUEVO: Subida de archivo (Foto real)
    archivo_digital = models.FileField(upload_to='garage/', blank=True, null=True, verbose_name="Foto Real del Producto")
    
    idperfilconqueestaactivo = models.ForeignKey(
        Datospersonales, models.DO_NOTHING, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="ventas_garage"
    )

    def clean(self):
        if self.fechapublicacion:
            validar_no_futuro(self.fechapublicacion)
        
        if self.estado:
            estado_normalizado = self.estado.capitalize()
            if estado_normalizado not in ["Bueno", "Regular"]:
                raise ValidationError("El estado solo puede ser 'Bueno' o 'Regular'")
            self.estado = estado_normalizado

    class Meta:
        db_table = "ventagarage"
        managed = True
        ordering = ['-fechapublicacion']
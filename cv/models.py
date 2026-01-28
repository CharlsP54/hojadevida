from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
import os
import uuid

# ============================================================
# Upload helpers
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
# VALIDADORES
# ============================================================

def validar_no_futuro(fecha):
    if fecha and fecha > date.today():
        raise ValidationError("No se permiten fechas futuras.")

def validar_rango_fechas(inicio, fin):
    if inicio and fin and fin < inicio:
        raise ValidationError("La fecha final debe ser posterior a la inicial.")

def validar_edad_18_100(fecha):
    if not fecha: return
    hoy = date.today()
    edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
    if edad < 18: raise ValidationError(f"Debes ser mayor de edad (Tienes {edad} años).")
    if edad > 100: raise ValidationError(f"Edad no válida ({edad} años).")

def validar_10_digitos(valor):
    if not valor: return
    if not valor.isdigit(): raise ValidationError("Solo se permiten números.")
    if len(valor) != 10: raise ValidationError(f"Debe tener exactamente 10 dígitos (tiene {len(valor)}).")

def validar_positivo(valor):
    if valor is not None and valor <= 0:
        raise ValidationError("El valor debe ser mayor a 0 (no se permiten negativos ni cero).")


class CleanSaveMixin(models.Model):
    class Meta: abstract = True
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


# ============================================================
# MODELOS
# ============================================================

class Datospersonales(CleanSaveMixin, models.Model):
    # ✅ Opciones de Estado Civil
    ESTADO_CIVIL_CHOICES = [
        ('Soltero', 'Soltero'),
        ('Casado', 'Casado'),
        ('Viudo', 'Viudo'),
        ('Divorciado', 'Divorciado'),
        ('Union de hecho', 'Unión de hecho'),
    ]

    # ✅ Opciones de Sexo
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Prefiero no decir', 'Prefiero no decir'),
    ]

    # ✅ Opciones de Licencia (Con descripción normativa)
    LICENCIA_CHOICES = [
        ('A', 'Tipo A: Motocicletas, ciclomotores, tricar y cuadrones'),
        ('B', 'Tipo B: Automóviles y camionetas (hasta 1.75 ton)'),
        ('F', 'Tipo F: Automotores especiales adaptados (Discapacidad)'),
        ('A1', 'Tipo A1: Mototaxis o tricimotos de servicio comercial'),
        ('C', 'Tipo C: Taxis, camionetas livianas (hasta 3.5 ton)'),
        ('C1', 'Tipo C1: Vehículos policiales, ambulancias, militares'),
        ('D', 'Tipo D: Servicio de pasajeros (intracantonal, interprovincial)'),
        ('D1', 'Tipo D1: Escolar, institucional y turismo'),
        ('E', 'Tipo E: Camiones pesados y extra pesados (tráiler, volqueta)'),
        ('E1', 'Tipo E1: Ferrocarriles, autoferros, trolebuses'),
        ('G', 'Tipo G: Maquinaria agrícola y equipo caminero'),
    ]

    idperfil = models.BigAutoField(primary_key=True)
    
    nombres = models.CharField(max_length=60, blank=True, null=True)
    apellidos = models.CharField(max_length=60, blank=True, null=True)
    descripcionperfil = models.CharField(max_length=50, blank=True, null=True)
    foto_perfil_url = models.URLField(blank=True, null=True, verbose_name="Link Foto Perfil")

    perfilactivo = models.IntegerField(blank=True, null=True)
    nacionalidad = models.CharField(max_length=20, blank=True, null=True)
    lugarnacimiento = models.CharField(max_length=60, blank=True, null=True)
    
    fechanacimiento = models.DateField(blank=True, null=True, validators=[validar_edad_18_100], verbose_name="Fecha Nacimiento")
    numerocedula = models.CharField(max_length=10, blank=True, null=True, validators=[validar_10_digitos], verbose_name="Cédula")
    
    # ✅ AHORA ES LISTA DESPLEGABLE
    sexo = models.CharField(
        max_length=20, 
        choices=SEXO_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="Género / Sexo"
    )
    
    # ✅ AHORA ES LISTA DESPLEGABLE
    estadocivil = models.CharField(
        max_length=50, 
        choices=ESTADO_CIVIL_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="Estado Civil"
    )
    
# ✅ AHORA ES LISTA DESPLEGABLE (Permite elegir el tipo exacto)
    licenciaconducir = models.CharField(
        max_length=50,  # <--- ¡IMPORTANTE! CÁMBIALO A 50 AQUÍ
        choices=LICENCIA_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="Tipo de Licencia"
    )
    
    telefonoconvencional = models.CharField(max_length=15, blank=True, null=True, validators=[validar_10_digitos], verbose_name="Celular")
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    email_contacto = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email de Contacto")
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True, null=True)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)
    
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    mostrar_experiencia = models.BooleanField(default=True)
    mostrar_cursos = models.BooleanField(default=True)
    mostrar_reconocimientos = models.BooleanField(default=True)
    mostrar_productos_academicos = models.BooleanField(default=True)
    mostrar_productos_laborales = models.BooleanField(default=True)
    mostrar_ventagarage = models.BooleanField(default=True)

    def clean(self):
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
    emailempresa = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email Empresa")
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
    totalhoras = models.IntegerField(blank=True, null=True, validators=[validar_positivo], verbose_name="Total Horas")
    descripcioncurso = models.CharField(max_length=100, blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    emailempresapatrocinadora = models.EmailField(max_length=60, blank=True, null=True, verbose_name="Email Patrocinador")
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
    TIPO_CHOICES = [('Publico', 'Público'), ('Privado', 'Privado'), ('Academico', 'Académico')]
    idreconocimiento = models.BigAutoField(primary_key=True)
    tiporeconocimiento = models.CharField(max_length=20, choices=TIPO_CHOICES, blank=True, null=True, verbose_name="Tipo de Reconocimiento")
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
    CLASIFICADOR_CHOICES = [
        ('Articulo cientifico', 'Artículo científico'), ('Ponencia', 'Ponencia'),
        ('Proyecto de investigacion', 'Proyecto de investigación'), ('Libro', 'Libro'),
        ('Capitulo de libro', 'Capítulo de libro'), ('Recurso didactico', 'Recurso didáctico'),
    ]
    idproductoacademico = models.BigAutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo", blank=True, null=True, related_name="productos_academicos")
    nombrerecurso = models.CharField(max_length=100, blank=True, null=True)
    clasificador = models.CharField(max_length=50, choices=CLASIFICADOR_CHOICES, blank=True, null=True, verbose_name="Tipo de Producto")
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, null=True, blank=True)
    class Meta: db_table = "productosacademicos"; managed = True


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
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[validar_positivo], verbose_name="Precio")
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
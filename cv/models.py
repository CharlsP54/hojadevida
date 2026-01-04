# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Cursosrealizados(models.Model):
    idcursorealizado = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey('Datospersonales', models.DO_NOTHING, db_column='idperfilconqueestaactivo', blank=True, null=True)
    nombrecurso = models.CharField(max_length=100, blank=True, null=True)
    fechainicio = models.DateField(blank=True, null=True)
    fechafin = models.DateField(blank=True, null=True)
    totalhoras = models.IntegerField(blank=True, null=True)
    descripcioncurso = models.CharField(max_length=100, blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    emailempresapatrocinadora = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(blank=True, null=True)
    rutacertificado = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cursosrealizados'


class Datospersonales(models.Model):
    idperfil = models.IntegerField(primary_key=True)
    descripcionperfil = models.CharField(max_length=50, blank=True, null=True)
    perfilactivo = models.IntegerField(blank=True, null=True)
    apellidos = models.CharField(max_length=60, blank=True, null=True)
    nombres = models.CharField(max_length=60, blank=True, null=True)
    nacionalidad = models.CharField(max_length=20, blank=True, null=True)
    lugarnacimiento = models.CharField(max_length=60, blank=True, null=True)
    fechanacimiento = models.DateField(blank=True, null=True)
    numerocedula = models.CharField(unique=True, max_length=10, blank=True, null=True)
    sexo = models.CharField(max_length=1, blank=True, null=True)
    estadocivil = models.CharField(max_length=50, blank=True, null=True)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)
    telefonoconvencional = models.CharField(max_length=15, blank=True, null=True)
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True, null=True)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)
    foto_perfil_url = models.URLField(blank=True, null=True, db_column="foto_perfil_url")
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    class Meta:
        managed = True
        db_table = 'datospersonales'


class Experiencialaboral(models.Model):
    idexperiencilaboral = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, models.DO_NOTHING, db_column='idperfilconqueestaactivo', blank=True, null=True)
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
    activarparaqueseveaenfront = models.BooleanField(blank=True, null=True)
    rutacertificado = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'experiencialaboral'


class Productosacademicos(models.Model):
    idproductoacademico = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, models.DO_NOTHING, db_column='idperfilconqueestaactivo', blank=True, null=True)
    nombrerecurso = models.CharField(max_length=100, blank=True, null=True)
    clasificador = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'productosacademicos'


class Productoslaborales(models.Model):
    idproductoslaborales = models.IntegerField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(Datospersonales, models.DO_NOTHING, db_column='idperfilconqueestaactivo', blank=True, null=True)
    nombreproducto = models.CharField(max_length=100, blank=True, null=True)
    fechaproducto = models.DateField(blank=True, null=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'productoslaborales'


class Reconocimientos(models.Model):
    TIPO_RECONOCIMIENTO_CHOICES = [
        ("Académico", "Académico"),
        ("Público", "Público"),
        ("Privado", "Privado"),
    ]

    idreconocimiento = models.IntegerField(primary_key=True)

    idperfilconqueestaactivo = models.ForeignKey(
        Datospersonales,
        models.DO_NOTHING,
        db_column='idperfilconqueestaactivo',
        blank=True,
        null=True
    )

    tiporeconocimiento = models.CharField(
        max_length=20,
        choices=TIPO_RECONOCIMIENTO_CHOICES,
        blank=True,
        null=True
    )

    fechareconocimiento = models.DateField(blank=True, null=True)
    descripcionreconocimiento = models.CharField(max_length=100, blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(blank=True, null=True)
    rutacertificado = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'reconocimientos'



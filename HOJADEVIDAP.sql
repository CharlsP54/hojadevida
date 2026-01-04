-- TABLA 1: DATOS PERSONALES
CREATE TABLE datospersonales (
    idperfil int PRIMARY KEY,
    descripcionperfil varchar(50),
    perfilactivo int,
    apellidos varchar(60),
    nombres varchar(60),
    nacionalidad varchar(20),
    lugarnacimiento varchar(60),
    fechanacimiento date,
    numerocedula varchar(10),
    sexo varchar(1),
    estadocivil varchar(50),
    licenciaconducir varchar(6),
    telefonoconvencional varchar(15),
    telefonofijo varchar(15),
    direcciontrabajo varchar(50),
    direcciondomiciliaria varchar(50),
    sitioweb varchar(60),
    CONSTRAINT chk_datospersonales_sexo CHECK (sexo IN ('H', 'M')),
    CONSTRAINT uq_datospersonales_ci UNIQUE (numerocedula)
);

-- TABLA 2: EXPERIENCIA LABORAL
CREATE TABLE experiencialaboral (
    idexperiencilaboral int PRIMARY KEY,
    idperfilconqueestaactivo int,
    cargodesempenado varchar(100),
    nombrempresa varchar(50),
    lugarempresa varchar(50),
    emailempresa varchar(100),
    sitiowebempresa varchar(100),
    nombrecontactoempresarial varchar(100),
    telefonocontactoempresarial varchar(60),
    fechainiciogestion date,
    fechafingestion date,
    descripcionfunciones varchar(100),
    activarparaqueseveaenfront boolean DEFAULT TRUE, -- Cambiado de BIT a BOOLEAN
    rutacertificado varchar(100),
    CONSTRAINT fk_experiencialaboral_datospersonales FOREIGN KEY (idperfilconqueestaactivo) REFERENCES datospersonales(idperfil)
);

-- TABLA 3: RECONOCIMIENTOS
CREATE TABLE reconocimientos (
    idreconocimiento int PRIMARY KEY,
    idperfilconqueestaactivo int,
    tiporeconocimiento varchar(100),
    fechareconocimiento date,
    descripcionreconocimiento varchar(100),
    entidadpatrocinadora varchar(100),
    nombrecontactoauspicia varchar(100),
    telefonocontactoauspicia varchar(60),
    activarparaqueseveaenfront boolean DEFAULT TRUE,
    rutacertificado varchar(100),
    CONSTRAINT chk_reconocimiento_tiporeconocimiento CHECK (tiporeconocimiento IN ('Académico', 'Público', 'Privado')),
    CONSTRAINT fk_reconocimientos_datospersonales FOREIGN KEY (idperfilconqueestaactivo) REFERENCES datospersonales(idperfil)
);

-- TABLA 4: CURSOS REALIZADOS
CREATE TABLE cursosrealizados (
    idcursorealizado int PRIMARY KEY,
    idperfilconqueestaactivo int,
    nombrecurso varchar(100),
    fechainicio date,
    fechafin date,
    totalhoras int,
    descripcioncurso varchar(100),
    entidadpatrocinadora varchar(100),
    nombrecontactoauspicia varchar(100),
    telefonocontactoauspicia varchar(60),
    emailempresapatrocinadora varchar(60),
    activarparaqueseveaenfront boolean DEFAULT TRUE,
    rutacertificado varchar(100),
    CONSTRAINT fk_cursosrealizados_datospersonales FOREIGN KEY (idperfilconqueestaactivo) REFERENCES datospersonales(idperfil)
);

-- TABLA 5: PRODUCTOS ACADEMICOS
CREATE TABLE productosacademicos (
    idproductoacademico int PRIMARY KEY,
    idperfilconqueestaactivo int,
    nombrerecurso varchar(100),
    clasificador varchar(100),
    descripcion varchar(100),
    activarparaqueseveaenfront boolean DEFAULT TRUE,
    CONSTRAINT fk_productosacademicos_datospersonales FOREIGN KEY (idperfilconqueestaactivo) REFERENCES datospersonales(idperfil)
);

-- TABLA 6: PRODUCTOS LABORALES
CREATE TABLE productoslaborales (
    idproductoslaborales int PRIMARY KEY,
    idperfilconqueestaactivo int,
    nombreproducto varchar(100),
    fechaproducto date,
    descripcion varchar(100),
    activarparaqueseveaenfront boolean DEFAULT TRUE,
    CONSTRAINT fk_productoslaborales_datospersonales FOREIGN KEY (idperfilconqueestaactivo) REFERENCES datospersonales(idperfil)
);


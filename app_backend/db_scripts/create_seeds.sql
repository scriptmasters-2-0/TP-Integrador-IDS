USE sistema_prestamos;
SET NAMES utf8mb4;

-- ==============================================================================
-- 0. PREPARACIÓN (Limpieza de tablas y reseteo de AUTO_INCREMENT)
-- ==============================================================================
SET
  FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE qr;

TRUNCATE TABLE estado_devuelto;

TRUNCATE TABLE penalizacion;

TRUNCATE TABLE reserva;

TRUNCATE TABLE articulos;

TRUNCATE TABLE usuario;

TRUNCATE TABLE normativa;

SET
  FOREIGN_KEY_CHECKS = 1;

-- ==============================================================================
-- 1. USUARIOS (Roles distribuidos, contraseñas dummy, estados activos/inactivos)
-- ==============================================================================
-- Hash para la contraseña "password"
SET
  @dummy_hash = '$2b$12$.yNicNI/5TBWFR.cxzZyculiuEX/6lsgU/4V8um308AtCNfpDasm2';

INSERT INTO
  usuario (
    padron,
    nombre,
    email,
    rol,
    carrera,
    contrasenia_hash,
    activo
  )
VALUES
  (
    100000,
    'Admin Sistema',
    'admin@fi.uba.ar',
    'admin',
    NULL,
    @dummy_hash,
    1
  )
  ,
  (
    100001,
    'Biblio Principal',
    'biblioteca@fi.uba.ar',
    'bibliotecario',
    NULL,
    @dummy_hash,
    1
  )
  ,
  (
    100002,
    'Profesor Laboratorio',
    'proflab@fi.uba.ar',
    'profesor',
    'Ingeniería Electrónica',
    @dummy_hash,
    1
  )
  ,
  (
    100003,
    'Profesor Taller',
    'proftaller@fi.uba.ar',
    'profesor',
    'Ingeniería Mecánica',
    @dummy_hash,
    1
  )
  ,
  (
    100004,
    'Profesor Sistemas',
    'profsis@fi.uba.ar',
    'profesor',
    'Ingeniería en Informática',
    @dummy_hash,
    1
  )
  ,
  (
    100005,
    'Ana Martinez',
    'amartinez@fi.uba.ar',
    'alumno',
    'Ingeniería Civil',
    @dummy_hash,
    1
  )
  ,
  (
    100006,
    'Carlos Ruiz',
    'cruiz@fi.uba.ar',
    'alumno',
    'Ingeniería en Alimentos',
    @dummy_hash,
    1
  )
  ,
  (
    100007,
    'Laura Gomez',
    'lgomez@fi.uba.ar',
    'alumno',
    'Ingeniería en Energía Eléctrica',
    @dummy_hash,
    1
  )
  ,
  (
    100008,
    'Diego Fernandez',
    'dfernandez@fi.uba.ar',
    'alumno',
    'Ingeniería Electrónica',
    @dummy_hash,
    1
  )
  ,
  (
    100009,
    'Sofia Silva',
    'ssilva@fi.uba.ar',
    'alumno',
    'Ingeniería en Agrimensura',
    @dummy_hash,
    1
  )
  ,
  (
    100010,
    'Martin Castro',
    'mcastro@fi.uba.ar',
    'alumno',
    'Ingeniería en Informática',
    @dummy_hash,
    0
  )
  ,
  (
    100011,
    'Lucia Torres',
    'ltorres@fi.uba.ar',
    'alumno',
    'Ingeniería en Petróleo',
    @dummy_hash,
    1
  )
  ,
  (
    100012,
    'Javier Lopez',
    'jlopez@fi.uba.ar',
    'alumno',
    'Ingeniería Industrial',
    @dummy_hash,
    1
  )
  ,
  (
    100013,
    'Camila Diaz',
    'cdiaz@fi.uba.ar',
    'alumno',
    'Ingeniería Mecánica',
    @dummy_hash,
    1
  )
  ,
  (
    100014,
    'Facundo Morales',
    'fmorales@fi.uba.ar',
    'alumno',
    'Ingeniería Naval',
    @dummy_hash,
    1
  )
  ,
  (
    100015,
    'Valentina Herrera',
    'vherrera@fi.uba.ar',
    'alumno',
    'Ingeniería Química',
    @dummy_hash,
    1
  )
  ,
  (
    100016,
    'Matias Romero',
    'mromero@fi.uba.ar',
    'alumno',
    'Lic. en Análisis de Sistemas',
    @dummy_hash,
    1
  )
  ,
  (
    100017,
    'Florencia Suarez',
    'fsuarez@fi.uba.ar',
    'alumno',
    'Bioingeniería',
    @dummy_hash,
    1
  )
  ,
  (
    100018,
    'Ezequiel Dominguez',
    'edominguez@fi.uba.ar',
    'alumno',
    'Ingeniería Civil',
    @dummy_hash,
    1
  )
  ,
  (
    100019,
    'Julieta Gimenez',
    'jgimenez@fi.uba.ar',
    'alumno',
    'Ingeniería en Alimentos',
    @dummy_hash,
    1
  )
  ,
  (
    100020,
    'Tomas Alonso',
    'talonso@fi.uba.ar',
    'alumno',
    'Ingeniería en Energía Eléctrica',
    @dummy_hash,
    0
  )
  ,
  (
    100021,
    'Rocio Blanco',
    'rblanco@fi.uba.ar',
    'alumno',
    'Ingeniería Electrónica',
    @dummy_hash,
    1
  )
  ,
  (
    100022,
    'Nicolas Medina',
    'nmedina@fi.uba.ar',
    'alumno',
    'Ingeniería en Agrimensura',
    @dummy_hash,
    1
  )
  ,
  (
    100023,
    'Micaela Vega',
    'mvega@fi.uba.ar',
    'alumno',
    'Ingeniería en Informática',
    @dummy_hash,
    1
  )
  ,
  (
    100024,
    'Gaston Navarro',
    'gnavarro@fi.uba.ar',
    'alumno',
    'Ingeniería en Petróleo',
    @dummy_hash,
    1
  )
  ,
  (
    100025,
    'Paula Iglesias',
    'piglesias@fi.uba.ar',
    'alumno',
    'Ingeniería Industrial',
    @dummy_hash,
    1
  )
  ,
  (
    100026,
    'Agustin Cabrera',
    'acabrera@fi.uba.ar',
    'alumno',
    'Ingeniería Mecánica',
    @dummy_hash,
    1
  )
  ,
  (
    100027,
    'Carolina Vidal',
    'cvidal@fi.uba.ar',
    'alumno',
    'Ingeniería Naval',
    @dummy_hash,
    1
  )
  ,
  (
    100028,
    'Julian Mendoza',
    'jmendoza@fi.uba.ar',
    'alumno',
    'Ingeniería Química',
    @dummy_hash,
    1
  )
  ,
  (
    100029,
    'Emilia Ortiz',
    'eortiz@fi.uba.ar',
    'alumno',
    'Lic. en Análisis de Sistemas',
    @dummy_hash,
    1
  )
  ,
  (
    100030,
    'Lucas Rios',
    'lrios@fi.uba.ar',
    'alumno',
    'Bioingeniería',
    @dummy_hash,
    1
  )
  ,
  (
    100031,
    'Agostina Castillo',
    'acastillo@fi.uba.ar',
    'alumno',
    'Ingeniería Civil',
    @dummy_hash,
    1
  )
  ,
  (
    100032,
    'Franco Acosta',
    'facosta@fi.uba.ar',
    'alumno',
    'Ingeniería en Alimentos',
    @dummy_hash,
    1
  )
  ,
  (
    100033,
    'Daniela Peralta',
    'dperalta@fi.uba.ar',
    'alumno',
    'Ingeniería en Energía Eléctrica',
    @dummy_hash,
    1
  )
  ,
  (
    100034,
    'Ignacio Paz',
    'ipaz@fi.uba.ar',
    'alumno',
    'Ingeniería Electrónica',
    @dummy_hash,
    1
  )
  ,
  (
    100035,
    'Martina Nuñez',
    'mnunez@fi.uba.ar',
    'alumno',
    'Ingeniería en Agrimensura',
    @dummy_hash,
    1
  )
  ,
  (
    100036,
    'Pablo Aguilar',
    'paguilar@fi.uba.ar',
    'alumno',
    'Ingeniería en Informática',
    @dummy_hash,
    1
  )
  ,
  (
    100037,
    'Victoria Mendez',
    'vmendez@fi.uba.ar',
    'alumno',
    'Ingeniería en Petróleo',
    @dummy_hash,
    1
  )
  ,
  (
    100038,
    'Rodrigo Cruz',
    'rcruz@fi.uba.ar',
    'alumno',
    'Ingeniería Industrial',
    @dummy_hash,
    1
  )
  ,
  (
    100039,
    'Belen Arias',
    'barias@fi.uba.ar',
    'alumno',
    'Ingeniería Mecánica',
    @dummy_hash,
    1
  )
  ,
  (
    100040,
    'Joaquin Cabrera',
    'jcabrera@fi.uba.ar',
    'alumno',
    'Ingeniería Naval',
    @dummy_hash,
    1
  )
  ,
  (
    100041,
    'Candela Molina',
    'cmolina@fi.uba.ar',
    'alumno',
    'Ingeniería Química',
    @dummy_hash,
    1
  )
  ,
  (
    100042,
    'Alejandro Rojas',
    'arojas@fi.uba.ar',
    'alumno',
    'Lic. en Análisis de Sistemas',
    @dummy_hash,
    1
  )
  ,
  (
    100043,
    'Renata Luna',
    'rluna@fi.uba.ar',
    'alumno',
    'Bioingeniería',
    @dummy_hash,
    1
  )
  ,
  (
    100044,
    'Esteban Miranda',
    'emiranda@fi.uba.ar',
    'alumno',
    'Ingeniería Civil',
    @dummy_hash,
    1
  )
  ,
  (
    100045,
    'Josefina Soto',
    'jsoto@fi.uba.ar',
    'alumno',
    'Ingeniería en Alimentos',
    @dummy_hash,
    1
  )
  ,
  (
    100046,
    'Marcos Bravo',
    'mbravo@fi.uba.ar',
    'alumno',
    'Ingeniería en Energía Eléctrica',
    @dummy_hash,
    1
  )
  ,
  (
    100047,
    'Antonella Gallardo',
    'agallardo@fi.uba.ar',
    'alumno',
    'Ingeniería Electrónica',
    @dummy_hash,
    1
  )
  ,
  (
    100048,
    'Leandro Marquez',
    'lmarquez@fi.uba.ar',
    'alumno',
    'Ingeniería en Agrimensura',
    @dummy_hash,
    1
  )
  ,
  (
    100049,
    'Solange Paredes',
    'sparedes@fi.uba.ar',
    'alumno',
    'Ingeniería en Informática',
    @dummy_hash,
    1
  )
  ,
  (
    100050,
    'Emanuel Rivas',
    'erivas@fi.uba.ar',
    'alumno',
    'Ingeniería en Petróleo',
    @dummy_hash,
    1
  )
  ,
  (
    100051,
    'Abril Ferreyra',
    'aferreyra@fi.uba.ar',
    'alumno',
    'Ingeniería Industrial',
    @dummy_hash,
    1
  )
  ,
  (
    100052,
    'Guillermo Ponce',
    'gponce@fi.uba.ar',
    'alumno',
    'Ingeniería Mecánica',
    @dummy_hash,
    1
  )
  ,
  (
    100053,
    'Melina Correa',
    'mcorrea@fi.uba.ar',
    'alumno',
    'Ingeniería Naval',
    @dummy_hash,
    1
  )
  ,
  (
    100054,
    'Hernan Varela',
    'hvarela@fi.uba.ar',
    'alumno',
    'Ingeniería Química',
    @dummy_hash,
    1
  )
;

-- ==============================================================================
-- 2. ARTICULOS (Equipamiento real de laboratorio, IT, herramientas manuales y libros)
-- ==============================================================================
INSERT INTO
  articulos (
    nombre_art,
    tipo,
    seccion,
    prestacion_maxima,
    stock,
    necesita_reparacion
  )
VALUES
  (
    'Osciloscopio Digital Rigol DS1054Z',
    'Electronicos',
    'Laboratorio',
    3,
    5,
    0
  ),
  (
    'Multímetro Fluke 117',
    'Herramienta',
    'Laboratorio',
    7,
    12,
    0
  ),
  (
    'Estación de Soldado Hakko FX-888D',
    'Electronicos',
    'Laboratorio',
    5,
    4,
    1
  ),
  (
    'Placa Arduino UNO R3',
    'Accesorios',
    'Tecnologia',
    15,
    30,
    0
  ),
  (
    'Raspberry Pi 4 Model B (4GB)',
    'Electronicos',
    'Tecnologia',
    7,
    15,
    0
  ),
  (
    'Taladro Inalámbrico Bosch 18V',
    'Herramienta',
    'Tecnologia',
    3,
    6,
    0
  ),
  (
    'Crimpeadora RJ45 Rj11 AMP',
    'Herramienta',
    'Tecnologia',
    5,
    8,
    0
  ),
  (
    'Tester de Redes LAN',
    'Electronicos',
    'Laboratorio',
    3,
    4,
    0
  ),
  (
    'Router Cisco ISR 4321',
    'Electronicos',
    'Laboratorio',
    14,
    2,
    0
  ),
  (
    'Switch Catalyst 2960-X',
    'Electronicos',
    'Laboratorio',
    14,
    3,
    1
  ),
  (
    'Libro: Clean Code - Robert C. Martin',
    'Libro',
    'Biblioteca',
    21,
    5,
    0
  ),
  (
    'Libro: Diseño Digital - Mano & Ciletti',
    'Libro',
    'Biblioteca',
    14,
    3,
    0
  ),
  (
    'Fuente de Alimentacion Regulable 30V 5A',
    'Electronicos',
    'Laboratorio',
    5,
    8,
    0
  ),
  (
    'Generador de Funciones 20MHz',
    'Electronicos',
    'Laboratorio',
    3,
    4,
    0
  ),
  (
    'Protoboard 830 Puntos',
    'Accesorios',
    'Tecnologia',
    15,
    50,
    0
  ),
  (
    'Set de Destornilladores de Precisión Wiha',
    'Herramienta',
    'Tecnologia',
    7,
    10,
    0
  ),
  (
    'Kit de Componentes Pasivos (Res/Cap)',
    'Accesorios',
    'Tecnologia',
    15,
    20,
    0
  ),
  (
    'Impresora 3D Creality Ender 3 V2',
    'Electronicos',
    'Laboratorio',
    2,
    3,
    0
  ),
  (
    'Filamento PLA 1KG (Varios Colores)',
    'Accesorios',
    'Tecnologia',
    3,
    15,
    0
  ),
  (
    'Cámara Térmica FLIR C5',
    'Electronicos',
    'Laboratorio',
    2,
    1,
    0
  ),
  (
    'Pinza Amperimétrica UNI-T UT204',
    'Herramienta',
    'Tecnologia',
    5,
    6,
    0
  ),
  (
    'Calibre Digital Mitutoyo 150mm',
    'Herramienta',
    'Tecnologia',
    5,
    4,
    0
  ),
  (
    'Proyector Epson PowerLite E20',
    'Proyector',
    'Tecnologia',
    1,
    5,
    0
  ),
  (
    'Microfono Condensador Audio-Technica',
    'Electronicos',
    'Tecnologia',
    3,
    2,
    0
  ),
  (
    'Teclado Controlador MIDI M-Audio 49',
    'Electronicos',
    'Tecnologia',
    7,
    3,
    0
  ),
  (
    'Guitarra Acústica Yamaha F310',
    'Herramienta',
    'Otros',
    4,
    1,
    0
  ),
  (
    'Bajo Eléctrico Squier Affinity',
    'Electronicos',
    'Otros',
    7,
    2,
    0
  ),
  (
    'Amplificador Fender Champion 20',
    'Electronicos',
    'Tecnologia',
    3,
    3,
    0
  ),
  (
    'Libro: Cálculo - James Stewart',
    'Libro',
    'Biblioteca',
    21,
    10,
    0
  ),
  (
    'Libro: Física Universitaria - Sears Zemansky',
    'Libro',
    'Biblioteca',
    21,
    12,
    1
  ),
  (
    'Módulo ESP32 NodeMCU',
    'Accesorios',
    'Tecnologia',
    15,
    25,
    0
  ),
  (
    'Sensor Ultrasónico HC-SR04',
    'Accesorios',
    'Tecnologia',
    15,
    40,
    0
  ),
  (
    'Amoladora Angular Makita 115mm',
    'Herramienta',
    'Tecnologia',
    3,
    4,
    0
  ),
  (
    'Sierra Circular DeWalt',
    'Herramienta',
    'Tecnologia',
    3,
    2,
    0
  ),
  (
    'Set de Llaves Combinadas Bahco',
    'Herramienta',
    'Laboratorio',
    7,
    5,
    0
  ),
  (
    'Cautín Tipo Lapiz 40W',
    'Herramienta',
    'Laboratorio',
    5,
    15,
    0
  ),
  (
    'Malla Desoldadora',
    'Accesorios',
    'Laboratorio',
    15,
    30,
    0
  ),
  (
    'Estaño 60/40 1mm (Rollo 250g)',
    'Accesorios',
    'Laboratorio',
    15,
    20,
    0
  ),
  (
    'Lupa con Iluminación LED',
    'Herramienta',
    'Laboratorio',
    5,
    8,
    0
  ),
  (
    'Módulo de Relés 4 Canales 5V',
    'Accesorios',
    'Tecnologia',
    15,
    15,
    0
  ),
  (
    'Servomotor SG90',
    'Accesorios',
    'Tecnologia',
    15,
    30,
    0
  ),
  (
    'Microcontrolador PIC16F877A',
    'Accesorios',
    'Tecnologia',
    15,
    20,
    0
  ),
  (
    'Programador PICkit 3',
    'Electronicos',
    'Laboratorio',
    5,
    5,
    0
  ),
  (
    'Analizador Lógico 8 Canales 24MHz',
    'Electronicos',
    'Laboratorio',
    5,
    4,
    0
  ),
  (
    'Cable HDMI 3 Metros',
    'Accesorios',
    'Bedelia',
    7,
    15,
    0
  ),
  (
    'Cámara Reflex Canon EOS Rebel T7',
    'Electronicos',
    'Tecnologia',
    2,
    2,
    0
  ),
  (
    'Trípode Manfrotto',
    'Herramienta',
    'Tecnologia',
    3,
    3,
    0
  ),
  (
    'Libro: Redes de Computadoras - Tanenbaum',
    'Libro',
    'Biblioteca',
    14,
    4,
    0
  ),
  (
    'Pizarra Blanca Magnética Móvil',
    'Herramienta',
    'Bedelia',
    1,
    5,
    0
  ),
  (
    'Set de marcadores para pizarra',
    'Herramienta',
    'Bedelia',
    1,
    10,
    0
  ),
  (
    'Alargue reforzado 10m',
    'Accesorios',
    'Bedelia',
    1,
    5,
    0
  ),
  (
    'Puntero láser inalabrico Logitech R400',
    'Herramienta',
    'Bedelia',
    1,
    8,
    0
  ),
  (
    'Kit de Limpieza de Contactos (Alcohol Iso)',
    'Accesorios',
    'Otros',
    3,
    10,
    0
  );

-- ==============================================================================
-- 3. RESERVAS
-- ==============================================================================
INSERT INTO
  reserva (
    id_usuario,
    id_reservado,
    estado_reserva,
    fecha_retiro,
    fecha_regreso
  )
VALUES
  (
    1,
    4,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 30 DAY),
    DATE_SUB(NOW(), INTERVAL 28 DAY)
  ),
  (
    2,
    1,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY)
  ),
  (
    3,
    11,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 45 DAY),
    DATE_SUB(NOW(), INTERVAL 30 DAY)
  ),
  (
    4,
    29,
    'rechazado',
    DATE_SUB(NOW(), INTERVAL 10 DAY),
    DATE_SUB(NOW(), INTERVAL 5 DAY)
  ),
  (
    5,
    5,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 5 DAY)
  ),
  (
    6,
    6,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(NOW(), INTERVAL 1 DAY)
  ),
  (
    7,
    30,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 15 DAY),
    DATE_SUB(NOW(), INTERVAL 10 DAY)
  ),
  (
    8,
    2,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 3 DAY)
  ),
  (
    9,
    15,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 3 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY)
  ),
  (
    10,
    22,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 20 DAY),
    DATE_SUB(NOW(), INTERVAL 18 DAY)
  ),
  (
    11,
    4,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 14 DAY)
  ),
  (
    12,
    13,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY)
  ),
  (
    13,
    26,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 60 DAY),
    DATE_SUB(NOW(), INTERVAL 55 DAY)
  ),
  (
    14,
    48,
    'rechazado',
    DATE_SUB(NOW(), INTERVAL 5 DAY),
    DATE_ADD(NOW(), INTERVAL 5 DAY)
  ),
  (
    15,
    31,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 7 DAY)
  ),
  (
    16,
    8,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(NOW(), INTERVAL 1 DAY)
  ),
  (
    17,
    18,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 12 DAY),
    DATE_SUB(NOW(), INTERVAL 10 DAY)
  ),
  (
    18,
    21,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 4 DAY)
  ),
  (
    19,
    32,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 6 DAY)
  ),
  (
    20,
    29,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 40 DAY),
    DATE_SUB(NOW(), INTERVAL 35 DAY)
  ),
  (
    21,
    33,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(NOW(), INTERVAL 1 DAY)
  ),
  (
    22,
    16,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 5 DAY)
  ),
  (
    23,
    44,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 18 DAY),
    DATE_SUB(NOW(), INTERVAL 13 DAY)
  ),
  (
    24,
    7,
    'rechazado',
    DATE_SUB(NOW(), INTERVAL 3 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY)
  ),
  (
    25,
    49,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 3 DAY)
  ),
  (
    26,
    25,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 5 DAY),
    DATE_SUB(NOW(), INTERVAL 1 DAY)
  ),
  (
    27,
    3,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 22 DAY),
    DATE_SUB(NOW(), INTERVAL 20 DAY)
  ),
  (
    28,
    14,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY)
  ),
  (
    29,
    9,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 4 DAY)
  ),
  (
    30,
    28,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 35 DAY),
    DATE_SUB(NOW(), INTERVAL 30 DAY)
  ),
  (
    31,
    34,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(NOW(), INTERVAL 1 DAY)
  ),
  (
    32,
    10,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 5 DAY)
  ),
  (
    33,
    42,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 14 DAY),
    DATE_SUB(NOW(), INTERVAL 10 DAY)
  ),
  (
    34,
    12,
    'rechazado',
    DATE_SUB(NOW(), INTERVAL 6 DAY),
    DATE_SUB(NOW(), INTERVAL 1 DAY)
  ),
  (
    35,
    17,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 6 DAY)
  ),
  (
    36,
    19,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 3 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY)
  ),
  (
    37,
    37,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 25 DAY),
    DATE_SUB(NOW(), INTERVAL 20 DAY)
  ),
  (
    38,
    41,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 7 DAY)
  ),
  (
    39,
    45,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 6 DAY)
  ),
  (
    40,
    50,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 50 DAY),
    DATE_SUB(NOW(), INTERVAL 40 DAY)
  ),
  (
    41,
    20,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 4 DAY),
    DATE_SUB(NOW(), INTERVAL 2 DAY)
  ),
  (
    42,
    23,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY)
  ),
  (
    43,
    27,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 16 DAY),
    DATE_SUB(NOW(), INTERVAL 14 DAY)
  ),
  (
    44,
    35,
    'rechazado',
    DATE_SUB(NOW(), INTERVAL 8 DAY),
    DATE_SUB(NOW(), INTERVAL 3 DAY)
  ),
  (
    45,
    36,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 4 DAY)
  ),
  (
    46,
    38,
    'entregado',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(NOW(), INTERVAL 1 DAY)
  ),
  (
    47,
    39,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 28 DAY),
    DATE_SUB(NOW(), INTERVAL 26 DAY)
  ),
  (
    48,
    43,
    'pendiente',
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    DATE_ADD(NOW(), INTERVAL 5 DAY)
  ),
  (
    49,
    46,
    'aprobado',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 4 DAY)
  ),
  (
    50,
    47,
    'devuelto',
    DATE_SUB(NOW(), INTERVAL 33 DAY),
    DATE_SUB(NOW(), INTERVAL 30 DAY)
  );

-- ==============================================================================
-- 4. ESTADO DEVUELTO (Aprovechando el límite VARCHAR 255)
-- ==============================================================================
INSERT INTO
  estado_devuelto (id_reserva, dias_retraso, condiciones)
VALUES
  (
    1,
    0,
    'Óptimo estado, todos los pines de la placa se encuentran rectos y funcionales.'
  ),
  (
    3,
    0,
    'Condición impecable, libro sin marcas ni hojas dobladas.'
  ),
  (
    7,
    2,
    'Punta del cautín levemente desgastada por el uso. Atraso menor en la entrega.'
  ),
  (
    10,
    0,
    'Cables del multímetro en perfecto estado, funcionando correctamente.'
  ),
  (
    13,
    0,
    'Guitarra afinada y sin rayas en el barniz exterior.'
  ),
  (
    17,
    0,
    'Limpieza profunda realizada por el usuario antes de devolver la impresora 3D.'
  ),
  (
    20,
    0,
    'Tapa del libro levemente doblada, evidencia uso normal de lectura.'
  ),
  (
    23,
    5,
    'Entregado con retraso significativo, falta caja original de la placa Arduino.'
  ),
  (
    27,
    0,
    'Equipo de soldadura funcionando correctamente, esponja humedecida.'
  ),
  (
    30,
    0,
    'Conector plug de audio sin ruidos estáticos, estado general muy bueno.'
  ),
  (
    33,
    0,
    'Cuchilla de corte en condiciones de uso seguras y limpias.'
  ),
  (
    37,
    1,
    'Falta un poco de malla desoldadora en el rollo pero dentro de lo esperado.'
  ),
  (
    40,
    0,
    'Lente de cámara sin rayones ni polvo, tapa incluida.'
  ),
  (
    43,
    0,
    'Patas de goma del trípode completas y perillas ajustadas.'
  ),
  (
    47,
    0,
    'Filamento restante devuelto correctamente en su bolsa original sellada.'
  ),
  (
    50,
    3,
    'Devuelto con manchas de grasa considerables en la carcasa exterior de la herramienta.'
  );

-- ==============================================================================
-- 5. PENALIZACIONES (Alineadas y vinculadas con ID de Reserva específico y Severidad)
-- ==============================================================================
INSERT INTO
  penalizacion (
    id_usuario,
    id_reserva,
    motivo,
    fecha_inicio,
    fecha_fin,
    activa,
    severidad
  )
VALUES
  (
    7,
    7,
    'Devolución fuera de término (2 días de retraso)',
    DATE_SUB(NOW(), INTERVAL 10 DAY),
    DATE_SUB(NOW(), INTERVAL 3 DAY),
    0,
    'baja'
  ),
  (
    23,
    23,
    'Retraso crítico en devolución de equipo delicado (5 días)',
    DATE_SUB(NOW(), INTERVAL 13 DAY),
    DATE_ADD(NOW(), INTERVAL 2 DAY),
    1,
    'alta'
  ),
  (
    50,
    50,
    'Entrega de material con suciedad/grasa',
    DATE_SUB(NOW(), INTERVAL 30 DAY),
    DATE_SUB(NOW(), INTERVAL 15 DAY),
    0,
    'media'
  ),
  (
    26,
    26,
    'Retraso actual en devolución (pendiente de entrega)',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(NOW(), INTERVAL 6 DAY),
    1,
    'media'
  ),
  (
    41,
    41,
    'Retraso actual en devolución de cámara térmica',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(NOW(), INTERVAL 5 DAY),
    1,
    'alta'
  ),
  (
    4,
    NULL,
    'Maltrato verbal al personal de pañol',
    DATE_SUB(NOW(), INTERVAL 5 DAY),
    DATE_ADD(NOW(), INTERVAL 25 DAY),
    1,
    'alta'
  ),
  (
    14,
    NULL,
    'Intentó retirar equipo sin autorización previa',
    DATE_SUB(NOW(), INTERVAL 15 DAY),
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    0,
    'alta'
  ),
  (
    24,
    24,
    'Pérdida de conector BNC del osciloscopio',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(NOW(), INTERVAL 28 DAY),
    1,
    'media'
  );

-- ==============================================================================
-- 6. QR
-- ==============================================================================
INSERT INTO
  qr (id_reserva, fecha_generado, codigo, escaneado)
VALUES
  (
    1,
    DATE_SUB(NOW(), INTERVAL 31 DAY),
    'QR-MAT-0001-A',
    1
  ),
  (
    2,
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    'QR-EQP-0002-B',
    0
  ),
  (
    3,
    DATE_SUB(NOW(), INTERVAL 46 DAY),
    'QR-BIB-0003-A',
    1
  ),
  (
    6,
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    'QR-HER-0006-C',
    1
  ),
  (
    7,
    DATE_SUB(NOW(), INTERVAL 16 DAY),
    'QR-MAT-0007-A',
    1
  ),
  (
    9,
    DATE_SUB(NOW(), INTERVAL 3 DAY),
    'QR-MAT-0009-B',
    1
  ),
  (
    10,
    DATE_SUB(NOW(), INTERVAL 21 DAY),
    'QR-HER-0010-A',
    1
  ),
  (
    11,
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    'QR-MAT-0011-B',
    1
  ),
  (
    12,
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    'QR-EQP-0012-A',
    0
  ),
  (
    13,
    DATE_SUB(NOW(), INTERVAL 61 DAY),
    'QR-INS-0013-C',
    1
  ),
  (
    16,
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    'QR-EQP-0016-A',
    1
  ),
  (
    17,
    DATE_SUB(NOW(), INTERVAL 13 DAY),
    'QR-EQP-0017-B',
    1
  ),
  (
    19,
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    'QR-MAT-0019-A',
    0
  ),
  (
    20,
    DATE_SUB(NOW(), INTERVAL 41 DAY),
    'QR-BIB-0020-B',
    1
  ),
  (
    21,
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    'QR-HER-0021-A',
    1
  ),
  (
    22,
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    'QR-HER-0022-C',
    0
  ),
  (
    23,
    DATE_SUB(NOW(), INTERVAL 19 DAY),
    'QR-EQP-0023-A',
    1
  ),
  (
    26,
    DATE_SUB(NOW(), INTERVAL 6 DAY),
    'QR-INS-0026-B',
    1
  ),
  (
    27,
    DATE_SUB(NOW(), INTERVAL 23 DAY),
    'QR-EQP-0027-A',
    1
  ),
  (
    29,
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    'QR-EQP-0029-C',
    0
  ),
  (
    30,
    DATE_SUB(NOW(), INTERVAL 36 DAY),
    'QR-EQP-0030-A',
    1
  ),
  (
    31,
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    'QR-HER-0031-B',
    1
  ),
  (
    32,
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    'QR-EQP-0032-A',
    0
  ),
  (
    33,
    DATE_SUB(NOW(), INTERVAL 15 DAY),
    'QR-MAT-0033-C',
    1
  ),
  (
    36,
    DATE_SUB(NOW(), INTERVAL 4 DAY),
    'QR-MAT-0036-A',
    1
  ),
  (
    37,
    DATE_SUB(NOW(), INTERVAL 26 DAY),
    'QR-MAT-0037-B',
    1
  ),
  (
    39,
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    'QR-AUD-0039-A',
    0
  ),
  (
    40,
    DATE_SUB(NOW(), INTERVAL 51 DAY),
    'QR-MAT-0040-C',
    1
  ),
  (
    41,
    DATE_SUB(NOW(), INTERVAL 5 DAY),
    'QR-HER-0041-A',
    1
  ),
  (
    42,
    DATE_SUB(NOW(), INTERVAL 0 DAY),
    'QR-AUD-0042-B',
    0
  ),
  (
    43,
    DATE_SUB(NOW(), INTERVAL 17 DAY),
    'QR-EQP-0043-A',
    1
  ),
  (
    46,
    DATE_SUB(NOW(), INTERVAL 3 DAY),
    'QR-HER-0046-C',
    1
  ),
  (
    47,
    DATE_SUB(NOW(), INTERVAL 29 DAY),
    'QR-EQP-0047-A',
    1
  ),
  (
    49,
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    'QR-AUD-0049-B',
    0
  ),
  (
    50,
    DATE_SUB(NOW(), INTERVAL 34 DAY),
    'QR-BIB-0050-A',
    1
  );

-- ==============================================================================
-- 7. NORMATIVA
-- ==============================================================================
INSERT INTO
  normativa (titulo, descripcion, fecha)
VALUES
  (
    'Reglamento General de Préstamos',
    'Define las reglas básicas para el retiro, cuidado y devolución de cualquier activo perteneciente a la institución.',
    DATE_SUB(NOW(), INTERVAL 400 DAY)
  ),
  (
    'Política de Retrasos y Sanciones',
    'Especifica el sistema de penalizaciones y los tiempos de inhabilitación por entregas fuera de término.',
    DATE_SUB(NOW(), INTERVAL 390 DAY)
  ),
  (
    'Uso Adecuado de Estaciones de Soldado',
    'Instrucciones obligatorias: uso de esponja vegetal húmeda, limpieza de punta y apagado preventivo.',
    DATE_SUB(NOW(), INTERVAL 380 DAY)
  ),
  (
    'Normas de Seguridad Eléctrica',
    'Prohibición estricta de puentear fusibles o alterar conexiones de puesta a tierra en el instrumental.',
    DATE_SUB(NOW(), INTERVAL 370 DAY)
  ),
  (
    'Manejo de Instrumentos de Medición',
    'Todo multímetro u osciloscopio debe ser devuelto con sus cables y puntas de prueba originales enrollados.',
    DATE_SUB(NOW(), INTERVAL 360 DAY)
  ),
  (
    'Cuidado del Material de Biblioteca',
    'Prohibido subrayar, doblar o alterar de cualquier forma las hojas y cubiertas de los textos de consulta.',
    DATE_SUB(NOW(), INTERVAL 350 DAY)
  ),
  (
    'Préstamos Excepcionales de Fin de Semana',
    'Los retiros de día viernes requieren aprobación de un profesor responsable del proyecto.',
    DATE_SUB(NOW(), INTERVAL 340 DAY)
  ),
  (
    'Reposición por Pérdida o Daño',
    'En caso de pérdida o daño total, el alumno o equipo de trabajo deberá reponer un ítem de iguales o superiores características.',
    DATE_SUB(NOW(), INTERVAL 330 DAY)
  ),
  (
    'Protocolo de Uso de Impresoras 3D',
    'Obligatorio asistir al curso de nivelación antes de operar maquinarias de fabricación digital.',
    DATE_SUB(NOW(), INTERVAL 320 DAY)
  ),
  (
    'Limpieza Post-Operativa',
    'Las herramientas mecánicas (taladros, amoladoras) deben devolverse libres de polvo y viruta metálica.',
    DATE_SUB(NOW(), INTERVAL 310 DAY)
  );


-- =========================
-- CREACIÓN DE TABLAS ECOENERGY
-- =========================

-- 1. Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de hogares
CREATE TABLE hogares (
    id_hogar SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    direccion VARCHAR(255),
    nombre_hogar VARCHAR(100),
    CONSTRAINT fk_hogar_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario)
        ON DELETE CASCADE
);

-- 3. Tabla de dispositivos
CREATE TABLE dispositivos (
    id_dispositivos SERIAL PRIMARY KEY,
    id_hogar INT NOT NULL,
    alias VARCHAR(100),
    id_dispositivo_iot VARCHAR(100) UNIQUE, -- identificador externo del IoT
    tipo_dispositivo_ia VARCHAR(100),
    estado_activo BOOLEAN DEFAULT TRUE,
    fecha_conexion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_dispositivo_hogar FOREIGN KEY (id_hogar)
        REFERENCES hogares (id_hogar)
        ON DELETE CASCADE
);

-- 4. Tabla de registros de consumo
CREATE TABLE registros_consumo (
    id_registro SERIAL PRIMARY KEY,
    id_dispositivo INT NOT NULL,
    consumo_kwh DECIMAL(10,2) NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    watts DECIMAL(10,2) NOT NULL,
    voltage DECIMAL(10,2) NOT NULL,
    current DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_registro_dispositivo
        FOREIGN KEY (id_dispositivo)
        REFERENCES dispositivos (id_dispositivos)
        ON DELETE CASCADE
);

-- 5. Tabla de recomendaciones
CREATE TABLE recomendaciones (
    id_recomendacion SERIAL PRIMARY KEY,
    id_hogar INT NOT NULL,
    id_dispositivo INT,
    contenido TEXT NOT NULL,
    tipo VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_lectura BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_recomendacion_hogar FOREIGN KEY (id_hogar)
        REFERENCES hogares (id_hogar)
        ON DELETE CASCADE,
    CONSTRAINT fk_recomendacion_dispositivo FOREIGN KEY (id_dispositivo)
        REFERENCES dispositivos (id_dispositivos)
        ON DELETE SET NULL
);

-- 6. Tabla de recomendación y ahorro diario (una por hogar por día)
CREATE TABLE recomendacion_ahorro_diaria (
    id SERIAL PRIMARY KEY,
    id_hogar INT NOT NULL,
    fecha DATE NOT NULL,
    recomendaciones JSONB NOT NULL DEFAULT '[]',
    ahorro_financiero VARCHAR(255),
    impacto_ambiental VARCHAR(255),
    indicador_didactico VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recomendacion_diaria_hogar FOREIGN KEY (id_hogar)
        REFERENCES hogares (id_hogar) ON DELETE CASCADE,
    CONSTRAINT uq_hogar_fecha UNIQUE (id_hogar, fecha)
);

-- 7. Tabla de suscriptores
CREATE TABLE subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

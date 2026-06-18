-- init.sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE registros_financieros (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    ingresos DECIMAL(10,2) NOT NULL,
    costos_fijos DECIMAL(10,2) NOT NULL,
    costos_variables DECIMAL(10,2) NOT NULL,
    riesgo VARCHAR(20) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertamos un usuario demo (ID 1) para que el endpoint de tu API tenga a quién asignarle los datos
INSERT INTO usuarios (nombre, email) VALUES ('Emprendedor Demo', 'demo@empresa.com');
const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());
app.use(cors());

// Secreto para firmar los tokens (en producción esto va en variables de entorno)
const JWT_SECRET = "super_secreto_tecnologias_emergentes";

const pool = new Pool({
    connectionString: 'postgres://postgres:root@db:5432/microemprendimientos_db'
});

// ==========================================
// 1. ENDPOINT: Registro de Usuario
// ==========================================
app.post('/api/auth/registro', async (req, res) => {
    const { nombre, email, password } = req.body;
    try {
        // Encriptar la contraseña
        const salt = await bcrypt.genSalt(10);
        const password_hash = await bcrypt.hash(password, salt);

        // Guardar en base de datos
        const query = `INSERT INTO usuarios (nombre, email, password_hash) VALUES ($1, $2, $3) RETURNING id, nombre, email`;
        const result = await pool.query(query, [nombre, email, password_hash]);
        
        res.status(201).json({ mensaje: "Usuario registrado con éxito", usuario: result.rows[0] });
    } catch (error) {
        res.status(500).json({ error: "Error al registrar. ¿El email ya existe?" });
    }
});

// ==========================================
// 2. ENDPOINT: Login de Usuario
// ==========================================
app.post('/api/auth/login', async (req, res) => {
    const { email, password } = req.body;
    try {
        // Buscar usuario
        const result = await pool.query(`SELECT * FROM usuarios WHERE email = $1`, [email]);
        if (result.rows.length === 0) return res.status(400).json({ error: "Usuario no encontrado" });

        const usuario = result.rows[0];

        // Verificar contraseña
        const passValida = await bcrypt.compare(password, usuario.password_hash);
        if (!passValida) return res.status(400).json({ error: "Contraseña incorrecta" });

        // Generar Token JWT
        const token = jwt.sign({ id: usuario.id }, JWT_SECRET, { expiresIn: '1h' });
        
        res.json({ mensaje: "Login exitoso", token });
    } catch (error) {
        res.status(500).json({ error: "Error en el servidor" });
    }
});

// ==========================================
// MIDDLEWARE: Proteger Rutas
// ==========================================
const verificarToken = (req, res, next) => {
    const token = req.header('Authorization');
    if (!token) return res.status(401).json({ error: "Acceso denegado. No hay token." });

    try {
        const verificado = jwt.verify(token.replace("Bearer ", ""), JWT_SECRET);
        req.usuario = verificado; // Guardamos el ID del usuario en la request
        next();
    } catch (error) {
        res.status(400).json({ error: "Token no válido" });
    }
};

// ==========================================
// 3. ENDPOINT PROTEGIDO: Guardar Registro
// ==========================================
app.post('/api/registros', verificarToken, async (req, res) => {
    const { ingresos, costos_fijos, costos_variables, riesgo } = req.body;
    try {
        const query = `
            INSERT INTO registros_financieros (usuario_id, ingresos, costos_fijos, costos_variables, riesgo) 
            VALUES ($1, $2, $3, $4, $5) RETURNING *`;
        const values = [req.usuario.id, ingresos, costos_fijos, costos_variables, riesgo];
        
        const result = await pool.query(query, values);
        res.status(201).json({ mensaje: "Datos guardados", data: result.rows[0] });
    } catch (error) {
        res.status(500).json({ error: "Error al guardar registro" });
    }
});

app.listen(4000, () => console.log('API Backend segura corriendo en puerto 4000'));
from flask import Flask, request
import sqlite3

app = Flask(__name__)

# Iniciar la base de datos local SQLite
def init_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# RUTA PARA REGISTRAR
@app.route('/registro', methods=['POST'])
def registro():
    usuario = request.form.get('usuario')
    password = request.form.get('password')

    print(f"\n[REGISTRO] Intentando registrar a: {usuario}")

    if not usuario or not password:
        return "FALTAN_DATOS", 400

    try:
        conn = sqlite3.connect('usuarios.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (usuario, password))
        conn.commit()
        conn.close()
        print(f"[ÉXITO] Usuario {usuario} guardado correctamente.")
        return "REGISTRO_OK", 200
    except sqlite3.IntegrityError:
        print(f"[ERROR] El nombre '{usuario}' ya está en uso.")
        return "USUARIO_EXISTE", 400
    except sqlite3.OperationalError as e:
        print(f"[ERROR] Base de datos ocupada: {e}")
        return "BASE_OCUPADA", 500

# RUTA PARA LOGIN
@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    password = request.form.get('password')

    print(f"\n[LOGIN] Intentando ingresar: {usuario}")

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (usuario, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("[ÉXITO] Credenciales correctas. LOGIN OK.")
        return "LOGIN_OK", 200
    else:
        print("[FALLO] Usuario o contraseña incorrectos.")
        return "ERROR_CREDENCIALES", 400

# RUTA PARA VER USUARIOS (solo para revisar, no para producción)
@app.route('/ver_usuarios')
def ver_usuarios():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, password FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    html = "<h2>Usuarios registrados</h2>"
    html += "<table border='1' cellpadding='8'>"
    html += "<tr><th>ID</th><th>Usuario</th><th>Password</th></tr>"

    for fila in usuarios:
        html += f"<tr><td>{fila[0]}</td><td>{fila[1]}</td><td>{fila[2]}</td></tr>"

    html += "</table>"
    return html

if __name__ == '__main__':
    init_db()
    print("Servidor encendido y escuchando...")
    # Ejecuta en el puerto 5000 y permite conexiones externas
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
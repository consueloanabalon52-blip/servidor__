from flask import Flask, request
import sqlite3

app = Flask(__name__)

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

init_db()  # <-- Esto se ejecuta SIEMPRE, sea Gunicorn o python directo

@app.route('/registro', methods=['POST'])
def registro():
    usuario = request.form.get('usuario')
    password = request.form.get('password')

    if not usuario or not password:
        return "FALTAN_DATOS", 400

    try:
        conn = sqlite3.connect('usuarios.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (usuario, password))
        conn.commit()
        conn.close()
        return "REGISTRO_OK", 200
    except sqlite3.IntegrityError:
        return "USUARIO_EXISTE", 400
    except sqlite3.OperationalError as e:
        return "BASE_OCUPADA", 500

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    password = request.form.get('password')

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (usuario, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return "LOGIN_OK", 200
    else:
        return "ERROR_CREDENCIALES", 400

@app.route('/ver_usuarios')
def ver_usuarios():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, password FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    html = "<h2>Usuarios registrados</h2><table border='1' cellpadding='8'><tr><th>ID</th><th>Usuario</th><th>Password</th></tr>"
    for fila in usuarios:
        html += f"<tr><td>{fila[0]}</td><td>{fila[1]}</td><td>{fila[2]}</td></tr>"
    html += "</table>"
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'

# ── Conexión a la base de datos ──────────────────────────────────────────────
def get_db():
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQLHOST', 'localhost'),
        user=os.environ.get('MYSQLUSER', 'root'),
        password=os.environ.get('MYSQLPASSWORD', 'Cris132511-'),
        database=os.environ.get('MYSQLDATABASE', 'gestion_estudiantes'),
        port=int(os.environ.get('MYSQLPORT', 3306)),
        ssl_disabled=False
    )
    cursor = conn.cursor()
    cursor.execute("SET time_zone = '-04:00'")
    cursor.close()
    return conn

# ── Decoradores de seguridad ─────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion para acceder', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion para acceder', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('No tienes permisos para realizar esta accion', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ── LOGIN ────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, username, rol FROM usuarios ORDER BY nombre")
    usuarios = cursor.fetchall()
    cursor.close(); db.close()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db(); cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s",
            (username, password))
        usuario = cursor.fetchone()
        cursor.close(); db.close()

        if usuario:
            session['usuario_id'] = usuario['id']
            session['nombre'] = usuario['nombre']
            session['username'] = usuario['username']
            session['rol'] = usuario['rol']
            flash(f'Bienvenido/a, {usuario["nombre"]}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contrasena incorrectos', 'danger')

    return render_template('login.html', usuarios=usuarios)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesion cerrada correctamente', 'success')
    return redirect(url_for('login'))

# ── INICIO ───────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM alumnos")
    total_alumnos = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM cursos")
    total_cursos = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total FROM notas")
    total_notas = cursor.fetchone()['total']
    cursor.close(); db.close()
    return render_template('index.html',
                           total_alumnos=total_alumnos,
                           total_cursos=total_cursos,
                           total_notas=total_notas)

# ── ALUMNOS (solo admin puede crear/editar/eliminar) ─────────────────────────
@app.route('/alumnos')
@login_required
def alumnos():
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alumnos ORDER BY apellido")
    lista = cursor.fetchall()
    cursor.close(); db.close()
    return render_template('alumnos.html', alumnos=lista)

@app.route('/alumnos/nuevo', methods=['GET','POST'])
@admin_required
def nuevo_alumno():
    if request.method == 'POST':
        db = get_db(); cursor = db.cursor()
        cursor.execute(
            "INSERT INTO alumnos (nombre, apellido, email, fecha_nacimiento) VALUES (%s,%s,%s,%s)",
            (request.form['nombre'], request.form['apellido'],
             request.form['email'], request.form['fecha_nacimiento'] or None))
        db.commit(); cursor.close(); db.close()
        flash('Alumno agregado correctamente', 'success')
        return redirect(url_for('alumnos'))
    return render_template('alumnos.html', modo='nuevo')

@app.route('/alumnos/editar/<int:id>', methods=['GET','POST'])
@admin_required
def editar_alumno(id):
    db = get_db(); cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute(
            "UPDATE alumnos SET nombre=%s, apellido=%s, email=%s, fecha_nacimiento=%s WHERE id=%s",
            (request.form['nombre'], request.form['apellido'],
             request.form['email'], request.form['fecha_nacimiento'] or None, id))
        db.commit(); cursor.close(); db.close()
        flash('Alumno actualizado', 'success')
        return redirect(url_for('alumnos'))
    cursor.execute("SELECT * FROM alumnos WHERE id=%s", (id,))
    alumno = cursor.fetchone()
    cursor.close(); db.close()
    return render_template('alumnos.html', modo='editar', alumno=alumno)

@app.route('/alumnos/eliminar/<int:id>')
@admin_required
def eliminar_alumno(id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("DELETE FROM alumnos WHERE id=%s", (id,))
    db.commit(); cursor.close(); db.close()
    flash('Alumno eliminado', 'warning')
    return redirect(url_for('alumnos'))

# ── CURSOS (solo admin puede crear/editar/eliminar) ──────────────────────────
@app.route('/cursos')
@login_required
def cursos():
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos ORDER BY nombre")
    lista = cursor.fetchall()
    cursor.close(); db.close()
    return render_template('cursos.html', cursos=lista)

@app.route('/cursos/nuevo', methods=['GET','POST'])
@admin_required
def nuevo_curso():
    if request.method == 'POST':
        db = get_db(); cursor = db.cursor()
        cursor.execute(
            "INSERT INTO cursos (nombre, descripcion, profesor) VALUES (%s,%s,%s)",
            (request.form['nombre'], request.form['descripcion'], request.form['profesor']))
        db.commit(); cursor.close(); db.close()
        flash('Curso agregado correctamente', 'success')
        return redirect(url_for('cursos'))
    return render_template('cursos.html', modo='nuevo')

@app.route('/cursos/editar/<int:id>', methods=['GET','POST'])
@admin_required
def editar_curso(id):
    db = get_db(); cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute(
            "UPDATE cursos SET nombre=%s, descripcion=%s, profesor=%s WHERE id=%s",
            (request.form['nombre'], request.form['descripcion'],
             request.form['profesor'], id))
        db.commit(); cursor.close(); db.close()
        flash('Curso actualizado', 'success')
        return redirect(url_for('cursos'))
    cursor.execute("SELECT * FROM cursos WHERE id=%s", (id,))
    curso = cursor.fetchone()
    cursor.close(); db.close()
    return render_template('cursos.html', modo='editar', curso=curso)

@app.route('/cursos/eliminar/<int:id>')
@admin_required
def eliminar_curso(id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("DELETE FROM cursos WHERE id=%s", (id,))
    db.commit(); cursor.close(); db.close()
    flash('Curso eliminado', 'warning')
    return redirect(url_for('cursos'))

# ── NOTAS (admin y profesores pueden CRUD) ───────────────────────────────────
@app.route('/notas')
@login_required
def notas():
    db = get_db(); cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT n.id, CONCAT(a.nombre,' ',a.apellido) as alumno,
               c.nombre as curso, n.nota, n.fecha,
               n.registrado_por, n.modificado_por
        FROM notas n
        JOIN alumnos a ON n.alumno_id = a.id
        JOIN cursos c ON n.curso_id = c.id
        ORDER BY a.apellido
    """)
    lista = cursor.fetchall()
    cursor.execute("""
        SELECT CONCAT(a.nombre,' ',a.apellido) as alumno,
               ROUND(AVG(n.nota),1) as promedio
        FROM notas n JOIN alumnos a ON n.alumno_id=a.id
        GROUP BY a.id ORDER BY promedio DESC
    """)
    promedios = cursor.fetchall()
    cursor.execute("SELECT * FROM alumnos ORDER BY apellido")
    alumnos = cursor.fetchall()
    cursor.execute("SELECT * FROM cursos ORDER BY nombre")
    cursos = cursor.fetchall()
    cursor.close(); db.close()
    return render_template('notas.html', notas=lista,
                           promedios=promedios, alumnos=alumnos, cursos=cursos)

@app.route('/notas/nueva', methods=['POST'])
@login_required
def nueva_nota():
    db = get_db(); cursor = db.cursor()
    cursor.execute(
        "INSERT INTO notas (alumno_id, curso_id, nota, fecha, registrado_por) VALUES (%s,%s,%s,%s,%s)",
        (request.form['alumno_id'], request.form['curso_id'],
         request.form['nota'], request.form['fecha'], session['nombre']))
    db.commit(); cursor.close(); db.close()
    flash('Nota registrada correctamente', 'success')
    return redirect(url_for('notas'))

@app.route('/notas/editar/<int:id>', methods=['GET','POST'])
@login_required
def editar_nota(id):
    db = get_db(); cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        cursor.execute(
            "UPDATE notas SET alumno_id=%s, curso_id=%s, nota=%s, fecha=%s, modificado_por=%s WHERE id=%s",
            (request.form['alumno_id'], request.form['curso_id'],
             request.form['nota'], request.form['fecha'], session['nombre'], id))
        db.commit(); cursor.close(); db.close()
        flash('Nota actualizada correctamente', 'success')
        return redirect(url_for('notas'))
    cursor.execute("""
        SELECT n.*, CONCAT(a.nombre,' ',a.apellido) as alumno_nombre,
               c.nombre as curso_nombre
        FROM notas n
        JOIN alumnos a ON n.alumno_id = a.id
        JOIN cursos c ON n.curso_id = c.id
        WHERE n.id=%s
    """, (id,))
    nota = cursor.fetchone()
    cursor.execute("SELECT * FROM alumnos ORDER BY apellido")
    alumnos = cursor.fetchall()
    cursor.execute("SELECT * FROM cursos ORDER BY nombre")
    cursos = cursor.fetchall()
    cursor.close(); db.close()
    return render_template('notas.html', modo='editar', nota_editar=nota,
                           alumnos=alumnos, cursos=cursos, notas=[], promedios=[])

@app.route('/notas/eliminar/<int:id>')
@login_required
def eliminar_nota(id):
    db = get_db(); cursor = db.cursor()
    cursor.execute("DELETE FROM notas WHERE id=%s", (id,))
    db.commit(); cursor.close(); db.close()
    flash('Nota eliminada', 'warning')
    return redirect(url_for('notas'))

if __name__ == '__main__':
    app.run(debug=True)
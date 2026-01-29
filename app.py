from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv() 

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuración Base de Datos
basedir = os.path.abspath(os.path.dirname(__file__))
db_file_env = os.getenv('DB_FILE', 'database/mi_app.sqlite')

if db_file_env.startswith("sqlite"):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_file_env
else:
    clean_path = db_file_env.replace('./', '').replace('.\\\\', '')
    db_abs_path = os.path.join(basedir, clean_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_abs_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'dev_secret_key') 

db = SQLAlchemy(app)

# --- MODELOS ---
class Bailarin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.String(50)) 
    contacto_emergencia = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True) 

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255)) 
    rol = db.Column(db.String(20), default='alumno') # admin, administrativo, maestro, alumno
    es_admin = db.Column(db.Boolean, default=False) 

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    fecha = db.Column(db.String(50))
    lugar = db.Column(db.String(100))
    hora = db.Column(db.String(50))

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bailarin_nombre = db.Column(db.String(100))
    concepto = db.Column(db.String(100))
    monto = db.Column(db.Float)
    fecha_pago = db.Column(db.String(20), default=datetime.now().strftime("%Y-%m-%d"))

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(20)) # YYYY-MM-DD
    bailarin_id = db.Column(db.Integer, db.ForeignKey('bailarin.id'))
    presente = db.Column(db.Boolean, default=False)
    bailarin = db.relationship('Bailarin', backref='asistencias')

class Vestuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50)) # Traje, Accesorio
    cantidad = db.Column(db.Integer, default=1)
    talla = db.Column(db.String(20))
    estado_conservacion = db.Column(db.String(50), default='Bueno')

# --- RUTAS VISTAS ---
@app.route('/')
def inicio(): return render_template('index.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

# --- API LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    usuario = Usuario.query.filter_by(username=data.get('usuario')).first()
    if usuario and check_password_hash(usuario.password, data.get('password')):
        # Definimos quién es staff (accede al dashboard administrativo)
        es_staff = usuario.rol in ['admin', 'administrativo', 'maestro']
        
        return jsonify({
            "success": True, 
            "es_admin": es_staff, 
            "rol": usuario.rol,
            "mensaje": f"Hola {usuario.username}"
        })
    return jsonify({"success": False, "mensaje": "Datos incorrectos"}), 401

# --- API ENDPOINTS ---
# 1. Usuarios
@app.route('/api/usuarios', methods=['GET', 'POST'])
def gestionar_usuarios():
    if request.method == 'GET':
        return jsonify([{"id": u.id, "username": u.username, "rol": u.rol} for u in Usuario.query.all()])
    if request.method == 'POST':
        data = request.json
        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({"success": False, "mensaje": "Usuario ya existe"}), 400
        hashed = generate_password_hash(data['password'])
        es_admin_flag = (data['rol'] in ['admin', 'administrativo', 'maestro'])
        nuevo = Usuario(username=data['username'], password=hashed, rol=data['rol'], es_admin=es_admin_flag)
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"success": True})

@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def borrar_usuario(id):
    u = Usuario.query.get(id)
    if u and u.username != 'admin': # Proteger admin
        db.session.delete(u); db.session.commit(); return jsonify({"success": True})
    return jsonify({"success": False}), 400

# 2. Asistencia
@app.route('/api/asistencia', methods=['GET', 'POST'])
def gestionar_asistencia():
    if request.method == 'GET':
        fecha = request.args.get('fecha', datetime.now().strftime("%Y-%m-%d"))
        bailarines = Bailarin.query.filter_by(estado=True).all()
        lista = []
        for b in bailarines:
            registro = Asistencia.query.filter_by(fecha=fecha, bailarin_id=b.id).first()
            lista.append({"id_bailarin": b.id, "nombre": b.nombre, "nivel": b.nivel, "presente": registro.presente if registro else False})
        return jsonify(lista)
    if request.method == 'POST':
        data = request.json
        fecha = data['fecha']
        # Registro individual (Alumno)
        if 'id_bailarin' in data:
             existe = Asistencia.query.filter_by(fecha=fecha, bailarin_id=data['id_bailarin']).first()
             if not existe:
                 nuevo = Asistencia(fecha=fecha, bailarin_id=data['id_bailarin'], presente=True)
                 db.session.add(nuevo)
        # Registro masivo (Admin/Maestro)
        elif 'registros' in data:
            Asistencia.query.filter_by(fecha=fecha).delete() # Limpiar día para sobreescribir
            for item in data['registros']:
                nuevo = Asistencia(fecha=fecha, bailarin_id=item['id_bailarin'], presente=item['presente'])
                db.session.add(nuevo)
        db.session.commit()
        return jsonify({"success": True})

# 3. Vestuario
@app.route('/api/vestuario', methods=['GET', 'POST'])
def gestionar_vestuario():
    if request.method == 'GET': return jsonify([{"id": v.id, "nombre": v.nombre, "tipo": v.tipo, "cantidad": v.cantidad, "talla": v.talla, "estado": v.estado_conservacion} for v in Vestuario.query.all()])
    if request.method == 'POST':
        data = request.json
        db.session.add(Vestuario(nombre=data['nombre'], tipo=data['tipo'], cantidad=int(data['cantidad']), talla=data.get('talla','U'), estado_conservacion=data.get('estado','Bueno')))
        db.session.commit()
        return jsonify({"success": True})
@app.route('/api/vestuario/<int:id>', methods=['DELETE'])
def borrar_vestuario(id):
    v = Vestuario.query.get(id)
    if v: db.session.delete(v); db.session.commit(); return jsonify({"success": True})
    return jsonify({"success": False}), 404

# 4. Pagos
@app.route('/api/pagos', methods=['GET', 'POST'])
def gestionar_pagos():
    if request.method == 'GET': return jsonify([{"id": p.id, "bailarin": p.bailarin_nombre, "concepto": p.concepto, "monto": p.monto, "fecha": p.fecha_pago} for p in Pago.query.order_by(Pago.id.desc()).all()])
    if request.method == 'POST':
        data = request.json
        db.session.add(Pago(bailarin_nombre=data['bailarin'], concepto=data['concepto'], monto=float(data['monto']), fecha_pago=datetime.now().strftime("%d/%m/%Y")))
        db.session.commit()
        return jsonify({"success": True})
@app.route('/api/pagos/<int:id>', methods=['DELETE'])
def borrar_pago(id):
    p = Pago.query.get(id)
    if p: db.session.delete(p); db.session.commit(); return jsonify({"success": True})
    return jsonify({"success": False}), 404

# 5. Eventos y Bailarines
@app.route('/api/eventos', methods=['GET', 'POST'])
def gestionar_eventos():
    if request.method == 'GET': return jsonify([{"id": e.id, "titulo": e.titulo, "fecha": e.fecha, "lugar": e.lugar, "hora": e.hora} for e in Evento.query.all()])
    if request.method == 'POST':
        data = request.json
        db.session.add(Evento(titulo=data['titulo'], fecha=data['fecha'], lugar=data.get('lugar',''), hora=data.get('hora','')))
        db.session.commit()
        return jsonify({"success": True})
@app.route('/api/eventos/<int:id>', methods=['DELETE'])
def borrar_evento(id):
    e = Evento.query.get(id)
    if e: db.session.delete(e); db.session.commit(); return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/api/bailarines', methods=['GET', 'POST'])
def gestionar_bailarines():
    if request.method == 'GET': return jsonify([{"id": b.id, "nombre": b.nombre, "nivel": b.nivel, "contacto": b.contacto_emergencia} for b in Bailarin.query.all()])
    if request.method == 'POST': 
        data = request.json
        db.session.add(Bailarin(nombre=data['nombre'], nivel=data['nivel'], contacto_emergencia=data.get('contacto', '')))
        db.session.commit()
        return jsonify({"success": True})
@app.route('/api/bailarines/<int:id>', methods=['DELETE'])
def borrar_bailarin(id):
    b = Bailarin.query.get(id)
    if b: db.session.delete(b); db.session.commit(); return jsonify({"success": True})
    return jsonify({"success": False}), 404

if __name__ == '__main__':
    with app.app_context():
        # Crear carpeta database si no existe
        if not os.path.exists('database'): os.makedirs('database')
        db.create_all()
        # Admin por defecto
        if not Usuario.query.filter_by(username='admin').first():
            hashed = generate_password_hash('1234')
            db.session.add(Usuario(username='admin', password=hashed, rol='admin', es_admin=True))
            db.session.commit()
            print("--- ADMIN CREADO ---")
    app.run(debug=(os.getenv('NODE_ENV') == 'development'), port=int(os.getenv('PORT', 3000)))
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import re
from datetime import datetime

load_dotenv() 

app = Flask(__name__, static_folder='static', template_folder='templates')

basedir = os.path.abspath(os.path.dirname(__file__))
db_file_env = os.getenv('DB_FILE', 'database/mi_app.sqlite')

if db_file_env.startswith("sqlite"):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_file_env
else:
    clean_path = db_file_env.replace('./', '').replace('.\\', '')
    db_abs_path = os.path.join(basedir, clean_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_abs_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'dev_secret_key') 

db = SQLAlchemy(app)

# --- UTILIDADES ---
def validar_password_segura(password):
    if len(password) < 8: return False, "Mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password): return False, "Falta una mayúscula."
    if not re.search(r"\d", password): return False, "Falta un número."
    return True, ""

# --- MODELOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='alumno')
    nombre_completo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    nivel = db.Column(db.String(50))
    es_admin = db.Column(db.Boolean, default=False) 

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    fecha = db.Column(db.String(50))
    lugar = db.Column(db.String(100))
    hora = db.Column(db.String(50))
    imagen_url = db.Column(db.String(500)) # NUEVO CAMPO PARA IMAGEN

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref='pagos')
    concepto = db.Column(db.String(100))
    monto = db.Column(db.Float)
    fecha_pago = db.Column(db.String(20), default=datetime.now().strftime("%Y-%m-%d"))

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(20)) 
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref='asistencias')
    presente = db.Column(db.Boolean, default=False)

class Vestuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    cantidad = db.Column(db.Integer, default=1)
    talla = db.Column(db.String(20))
    estado_conservacion = db.Column(db.String(50), default='Bueno')

# --- RUTAS ---
@app.route('/')
def inicio(): return render_template('index.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u = Usuario.query.filter_by(username=data.get('usuario')).first()
    if u and check_password_hash(u.password, data.get('password')):
        es_staff = u.rol in ['admin', 'administrativo', 'maestro']
        return jsonify({
            "success": True, 
            "es_admin": es_staff, 
            "rol": u.rol,
            "id": u.id,
            "nombre": u.nombre_completo or u.username,
            "mensaje": f"Hola {u.username}"
        })
    return jsonify({"success": False, "mensaje": "Datos incorrectos"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('username') or not data.get('password'): return jsonify({"success": False, "mensaje": "Faltan datos"}), 400
    if not data['username'].endswith('@gmail.com'): return jsonify({"success": False, "mensaje": "Solo gmail.com"}), 400
    if Usuario.query.filter_by(username=data['username']).first(): return jsonify({"success": False, "mensaje": "Usuario existe"}), 400
    
    es_segura, msg = validar_password_segura(data['password'])
    if not es_segura: return jsonify({"success": False, "mensaje": msg}), 400

    nuevo = Usuario(username=data['username'], password=generate_password_hash(data['password']), rol='alumno', es_admin=False, nombre_completo=data.get('nombre', ''), telefono=data.get('telefono', ''), nivel=data.get('nivel', 'Principiante'))
    db.session.add(nuevo); db.session.commit()
    return jsonify({"success": True, "mensaje": "Registro exitoso"})

# APIS CRUD
@app.route('/api/usuarios', methods=['GET', 'POST'])
def gestionar_usuarios():
    if request.method == 'GET':
        q = Usuario.query
        if request.args.get('rol'): q = q.filter_by(rol=request.args.get('rol'))
        return jsonify([{"id": u.id, "username": u.username, "rol": u.rol, "nombre": u.nombre_completo, "telefono": u.telefono, "nivel": u.nivel} for u in q.all()])
    if request.method == 'POST':
        d = request.json
        if Usuario.query.filter_by(username=d['username']).first(): return jsonify({"success": False, "mensaje": "Existe"}), 400
        val, msg = validar_password_segura(d['password'])
        if not val: return jsonify({"success": False, "mensaje": msg}), 400
        n = Usuario(username=d['username'], password=generate_password_hash(d['password']), rol=d['rol'], es_admin=(d['rol'] in ['admin', 'staff']), nombre_completo=d.get('nombre',''), telefono=d.get('telefono',''), nivel=d.get('nivel',''))
        db.session.add(n); db.session.commit(); return jsonify({"success": True})

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'DELETE'])
def usuario_id(id):
    u = Usuario.query.get(id)
    if not u: return jsonify({"success": False}), 404
    if request.method == 'PUT':
        d = request.json
        u.username=d.get('username',u.username); u.rol=d.get('rol',u.rol); u.nombre_completo=d.get('nombre',u.nombre_completo); u.telefono=d.get('telefono',u.telefono); u.nivel=d.get('nivel',u.nivel)
        if d.get('password'): 
            val, msg = validar_password_segura(d['password'])
            if not val: return jsonify({"success": False, "mensaje": msg}), 400
            u.password = generate_password_hash(d['password'])
        db.session.commit(); return jsonify({"success": True})
    if request.method == 'DELETE':
        if u.username == 'admin': return jsonify({"success": False}), 400
        db.session.delete(u); db.session.commit(); return jsonify({"success": True})

# EVENTOS (Actualizado con imagen)
@app.route('/api/eventos', methods=['GET', 'POST'])
def gestionar_eventos():
    if request.method == 'GET': 
        return jsonify([{"id": e.id, "titulo": e.titulo, "fecha": e.fecha, "lugar": e.lugar, "hora": e.hora, "imagen_url": getattr(e, 'imagen_url', '')} for e in Evento.query.all()])
    if request.method == 'POST': 
        d=request.json
        db.session.add(Evento(titulo=d['titulo'], fecha=d['fecha'], lugar=d.get('lugar',''), hora=d.get('hora',''), imagen_url=d.get('imagen_url','')))
        db.session.commit()
        return jsonify({"success": True})

@app.route('/api/eventos/<int:id>', methods=['PUT', 'DELETE'])
def evento_id(id):
    e = Evento.query.get(id)
    if not e: return jsonify({"success": False}), 404
    if request.method == 'DELETE':
        db.session.delete(e); db.session.commit(); return jsonify({"success": True})
    if request.method == 'PUT':
        d = request.json
        e.titulo = d.get('titulo', e.titulo)
        e.fecha = d.get('fecha', e.fecha)
        e.lugar = d.get('lugar', e.lugar)
        e.hora = d.get('hora', e.hora)
        e.imagen_url = d.get('imagen_url', e.imagen_url)
        db.session.commit()
        return jsonify({"success": True})

# OTROS
@app.route('/api/pagos', methods=['GET', 'POST'])
def gestionar_pagos():
    if request.method == 'GET': return jsonify([{"id": p.id, "bailarin": p.usuario.nombre_completo if p.usuario else "Unknown", "concepto": p.concepto, "monto": p.monto, "fecha": p.fecha_pago} for p in Pago.query.order_by(Pago.id.desc()).all()])
    if request.method == 'POST': d=request.json; db.session.add(Pago(usuario_id=d['usuario_id'], concepto=d['concepto'], monto=float(d['monto']), fecha_pago=datetime.now().strftime("%Y-%m-%d"))); db.session.commit(); return jsonify({"success": True})
@app.route('/api/pagos/<int:id>', methods=['DELETE'])
def borrar_pago(id): p=Pago.query.get(id); db.session.delete(p); db.session.commit(); return jsonify({"success": True})

@app.route('/api/vestuario', methods=['GET', 'POST'])
def gestionar_vestuario():
    if request.method == 'GET': return jsonify([{"id": v.id, "nombre": v.nombre, "tipo": v.tipo, "cantidad": v.cantidad, "talla": v.talla, "estado": v.estado_conservacion} for v in Vestuario.query.all()])
    if request.method == 'POST': d=request.json; db.session.add(Vestuario(nombre=d['nombre'], tipo=d['tipo'], cantidad=int(d['cantidad']), talla=d.get('talla','U'), estado_conservacion=d.get('estado','Bueno'))); db.session.commit(); return jsonify({"success": True})
@app.route('/api/vestuario/<int:id>', methods=['DELETE'])
def borrar_vestuario(id): v=Vestuario.query.get(id); db.session.delete(v); db.session.commit(); return jsonify({"success": True})

@app.route('/api/asistencia', methods=['GET', 'POST'])
def gestionar_asistencia():
    if request.method == 'GET':
        fecha = request.args.get('fecha', datetime.now().strftime("%Y-%m-%d"))
        alumnos = Usuario.query.filter_by(rol='alumno').all()
        lista = []
        for a in alumnos:
            registro = Asistencia.query.filter_by(fecha=fecha, usuario_id=a.id).first()
            lista.append({"id_usuario": a.id, "nombre": a.nombre_completo or a.username, "nivel": a.nivel, "presente": registro.presente if registro else False})
        return jsonify(lista)
    if request.method == 'POST':
        data = request.json; fecha = datetime.now().strftime("%Y-%m-%d")
        if 'qr_data' in data:
            if data['qr_data'] != f"NAYAHUARI_ASISTENCIA_{fecha}": return jsonify({"success": False, "mensaje": "QR Inválido"}), 400
            uid = data['id_usuario']
            if not Asistencia.query.filter_by(fecha=fecha, usuario_id=uid).first():
                db.session.add(Asistencia(fecha=fecha, usuario_id=uid, presente=True)); db.session.commit(); return jsonify({"success": True, "mensaje": "Asistencia OK"})
            return jsonify({"success": True, "mensaje": "Ya registrado"})
        elif 'registros' in data:
            fecha = data.get('fecha', fecha)
            Asistencia.query.filter_by(fecha=fecha).delete()
            for item in data['registros']: db.session.add(Asistencia(fecha=fecha, usuario_id=item['id_usuario'], presente=item['presente']))
            db.session.commit(); return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/bailarines', methods=['GET'])
def get_bailarines(): return jsonify([{"id": a.id, "nombre": a.nombre_completo or a.username, "nivel": a.nivel, "contacto": a.telefono} for a in Usuario.query.filter_by(rol='alumno').all()])

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('database'): os.makedirs('database')
        db.create_all()
        if not Usuario.query.filter_by(username='admin').first():
            db.session.add(Usuario(username='admin', password=generate_password_hash('Admin1234'), rol='admin', es_admin=True, nombre_completo="Director General"))
            db.session.commit()
    app.run(host='0.0.0.0', debug=(os.getenv('NODE_ENV') == 'development'), port=int(os.getenv('PORT', 3000)))

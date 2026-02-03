from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import re
from datetime import datetime

load_dotenv() 

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuración BD
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

# --- UTILIDADES DE SEGURIDAD ---
def validar_password_segura(password):
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe incluir al menos una mayúscula."
    if not re.search(r"\d", password):
        return False, "La contraseña debe incluir al menos un número."
    return True, ""

# --- MODELOS (Sin Nivel) ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False) # Email/Login
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='alumno')
    nombre_completo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    # Nivel ELIMINADO
    es_admin = db.Column(db.Boolean, default=False) 

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    fecha = db.Column(db.String(50))
    lugar = db.Column(db.String(100))
    hora = db.Column(db.String(50))

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

@app.route('/registro')
def vista_registro(): return render_template('registro.html')

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
    username = data.get('username')
    password = data.get('password')
    nombre_completo = data.get('nombre')
    
    if not username or not password or not nombre_completo:
        return jsonify({"success": False, "mensaje": "Faltan datos obligatorios"}), 400
    
    # Validación Google
    if not username.endswith('@gmail.com'):
        return jsonify({"success": False, "mensaje": "Solo se permiten correos @gmail.com"}), 400
        
    # Validación Contraseña Segura
    es_segura, msg_pass = validar_password_segura(password)
    if not es_segura:
        return jsonify({"success": False, "mensaje": msg_pass}), 400

    if Usuario.query.filter_by(username=username).first():
        return jsonify({"success": False, "mensaje": "El usuario ya existe"}), 400
        
    hashed = generate_password_hash(password)
    nuevo = Usuario(
        username=username, 
        password=hashed, 
        rol='alumno', 
        es_admin=False,
        nombre_completo=nombre_completo, 
        telefono=data.get('telefono', '')
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"success": True, "mensaje": "Registro exitoso"})

# --- API ASISTENCIA ---
@app.route('/api/asistencia', methods=['GET', 'POST'])
def gestionar_asistencia():
    if request.method == 'GET':
        fecha = request.args.get('fecha', datetime.now().strftime("%Y-%m-%d"))
        alumnos = Usuario.query.filter_by(rol='alumno').all()
        lista = []
        for a in alumnos:
            registro = Asistencia.query.filter_by(fecha=fecha, usuario_id=a.id).first()
            lista.append({
                "id_usuario": a.id, "nombre": a.nombre_completo or a.username, 
                "presente": registro.presente if registro else False
            })
        return jsonify(lista)

    if request.method == 'POST':
        data = request.json
        fecha = datetime.now().strftime("%Y-%m-%d")
        if 'qr_data' in data: # QR
            codigo_esperado = f"NAYAHUARI_ASISTENCIA_{fecha}"
            if data['qr_data'] != codigo_esperado:
                return jsonify({"success": False, "mensaje": "Código QR inválido"}), 400
            uid = data['id_usuario']
            if not Asistencia.query.filter_by(fecha=fecha, usuario_id=uid).first():
                db.session.add(Asistencia(fecha=fecha, usuario_id=uid, presente=True))
                db.session.commit()
                return jsonify({"success": True, "mensaje": "¡Asistencia Registrada!"})
            else:
                return jsonify({"success": True, "mensaje": "Ya registrada."})
        elif 'registros' in data: # Manual
            fecha_manual = data.get('fecha', fecha)
            Asistencia.query.filter_by(fecha=fecha_manual).delete()
            for item in data['registros']:
                db.session.add(Asistencia(fecha=fecha_manual, usuario_id=item['id_usuario'], presente=item['presente']))
            db.session.commit()
            return jsonify({"success": True})
    return jsonify({"success": False}), 400

# --- API USUARIOS ---
@app.route('/api/usuarios', methods=['GET', 'POST'])
def gestionar_usuarios():
    if request.method == 'GET':
        query = Usuario.query
        if request.args.get('rol'): query = query.filter_by(rol=request.args.get('rol'))
        return jsonify([{"id": u.id, "username": u.username, "rol": u.rol, "nombre": u.nombre_completo, "telefono": u.telefono} for u in query.all()])
    
    if request.method == 'POST':
        d = request.json
        if Usuario.query.filter_by(username=d['username']).first(): return jsonify({"success": False, "mensaje": "Usuario ya existe"}), 400
        
        # Validar pass
        es_segura, msg_pass = validar_password_segura(d['password'])
        if not es_segura: return jsonify({"success": False, "mensaje": msg_pass}), 400

        n = Usuario(
            username=d['username'], 
            password=generate_password_hash(d['password']), 
            rol=d['rol'], 
            es_admin=(d['rol'] in ['admin', 'staff']), 
            nombre_completo=d.get('nombre',''), 
            telefono=d.get('telefono','')
        )
        db.session.add(n); db.session.commit(); return jsonify({"success": True})

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'DELETE'])
def usuario_id(id):
    u = Usuario.query.get(id)
    if not u: return jsonify({"success": False}), 404
    if request.method == 'PUT':
        d = request.json
        u.username=d.get('username',u.username); u.rol=d.get('rol',u.rol); u.nombre_completo=d.get('nombre',u.nombre_completo); u.telefono=d.get('telefono',u.telefono)
        if d.get('password'): 
            es_segura, msg = validar_password_segura(d['password'])
            if not es_segura: return jsonify({"success": False, "mensaje": msg}), 400
            u.password = generate_password_hash(d['password'])
        db.session.commit(); return jsonify({"success": True})
    if request.method == 'DELETE':
        if u.username == 'admin': return jsonify({"success": False, "mensaje": "No se puede borrar al superadmin"}), 400
        db.session.delete(u); db.session.commit(); return jsonify({"success": True})

# --- APIS RESTANTES (Pagos, Eventos, Vestuario) ---
@app.route('/api/pagos', methods=['GET', 'POST'])
def gestionar_pagos():
    if request.method == 'GET': return jsonify([{"id": p.id, "bailarin": p.usuario.nombre_completo if p.usuario else "Desconocido", "concepto": p.concepto, "monto": p.monto, "fecha": p.fecha_pago} for p in Pago.query.order_by(Pago.id.desc()).all()])
    if request.method == 'POST':
        data = request.json; db.session.add(Pago(usuario_id=data['usuario_id'], concepto=data['concepto'], monto=float(data['monto']), fecha_pago=datetime.now().strftime("%Y-%m-%d"))); db.session.commit(); return jsonify({"success": True})
@app.route('/api/pagos/<int:id>', methods=['DELETE'])
def borrar_pago(id): p=Pago.query.get(id); db.session.delete(p); db.session.commit(); return jsonify({"success": True})

@app.route('/api/vestuario', methods=['GET', 'POST'])
def gestionar_vestuario():
    if request.method == 'GET': return jsonify([{"id": v.id, "nombre": v.nombre, "tipo": v.tipo, "cantidad": v.cantidad, "talla": v.talla, "estado": v.estado_conservacion} for v in Vestuario.query.all()])
    if request.method == 'POST': d=request.json; db.session.add(Vestuario(nombre=d['nombre'], tipo=d['tipo'], cantidad=int(d['cantidad']), talla=d.get('talla','U'), estado_conservacion=d.get('estado','Bueno'))); db.session.commit(); return jsonify({"success": True})
@app.route('/api/vestuario/<int:id>', methods=['DELETE'])
def borrar_vestuario(id): v=Vestuario.query.get(id); db.session.delete(v); db.session.commit(); return jsonify({"success": True})

@app.route('/api/eventos', methods=['GET', 'POST'])
def gestionar_eventos():
    if request.method == 'GET': return jsonify([{"id": e.id, "titulo": e.titulo, "fecha": e.fecha, "lugar": e.lugar, "hora": e.hora} for e in Evento.query.all()])
    if request.method == 'POST': d=request.json; db.session.add(Evento(titulo=d['titulo'], fecha=d['fecha'], lugar=d.get('lugar',''), hora=d.get('hora',''))); db.session.commit(); return jsonify({"success": True})
@app.route('/api/eventos/<int:id>', methods=['DELETE'])
def borrar_evento(id): e=Evento.query.get(id); db.session.delete(e); db.session.commit(); return jsonify({"success": True})

# Compatibilidad para frontend que busque 'bailarines'
@app.route('/api/bailarines', methods=['GET'])
def get_bailarines():
    return jsonify([{"id": a.id, "nombre": a.nombre_completo or a.username, "contacto": a.telefono} for a in Usuario.query.filter_by(rol='alumno').all()])

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('database'): os.makedirs('database')
        db.create_all()
        if not Usuario.query.filter_by(username='admin').first():
            db.session.add(Usuario(username='admin', password=generate_password_hash('Admin1234'), rol='admin', es_admin=True, nombre_completo="Director General"))
            db.session.commit()
            print("--- ADMIN CREADO ---")
    app.run(host='0.0.0.0', debug=(os.getenv('NODE_ENV') == 'development'), port=int(os.getenv('PORT', 3000)))

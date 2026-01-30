
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
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

# --- MODELOS UNIFICADOS ---

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # Roles permitidos: 'admin', 'staff', 'alumno'
    rol = db.Column(db.String(20), default='alumno')
    
    # Datos de Perfil (Para alumnos y staff)
    nombre_completo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    nivel = db.Column(db.String(50)) # Solo relevante si rol='alumno'
    
    es_admin = db.Column(db.Boolean, default=False) 

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    fecha = db.Column(db.String(50))
    lugar = db.Column(db.String(100))
    hora = db.Column(db.String(50))

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Relación directa con Usuario (Alumno)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref='pagos')
    concepto = db.Column(db.String(100))
    monto = db.Column(db.Float)
    fecha_pago = db.Column(db.String(20), default=datetime.now().strftime("%Y-%m-%d"))

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(20)) 
    # Relación directa con Usuario (Alumno)
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

# --- RUTAS VISTAS ---
@app.route('/')
def inicio(): return render_template('index.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

# --- API LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u = Usuario.query.filter_by(username=data.get('usuario')).first()
    if u and check_password_hash(u.password, data.get('password')):
        # Solo admin y staff entran al panel administrativo
        acceso_panel = u.rol in ['admin', 'staff']
        return jsonify({
            "success": True, 
            "es_admin": acceso_panel, 
            "rol": u.rol,
            "nombre": u.nombre_completo or u.username,
            "mensaje": f"Hola {u.username}"
        })
    return jsonify({"success": False, "mensaje": "Datos incorrectos"}), 401

# --- GESTIÓN DE USUARIOS (CRUD CENTRAL) ---
@app.route('/api/usuarios', methods=['GET', 'POST'])
def gestionar_usuarios():
    if request.method == 'GET':
        rol = request.args.get('rol')
        query = Usuario.query
        if rol: 
            query = query.filter_by(rol=rol)
        usuarios = query.all()
        return jsonify([{
            "id": u.id, "username": u.username, "rol": u.rol, 
            "nombre": u.nombre_completo, "telefono": u.telefono, "nivel": u.nivel
        } for u in usuarios])

    if request.method == 'POST':
        data = request.json
        if Usuario.query.filter_by(username=data['username']).first():
            return jsonify({"success": False, "mensaje": "El usuario ya existe"}), 400
        
        hashed = generate_password_hash(data['password'])
        # Definir si tiene permisos de admin
        es_admin_flag = (data['rol'] in ['admin', 'staff'])
        
        nuevo = Usuario(
            username=data['username'], 
            password=hashed, 
            rol=data['rol'], 
            es_admin=es_admin_flag,
            nombre_completo=data.get('nombre', ''), 
            telefono=data.get('telefono', ''), 
            nivel=data.get('nivel', '') if data['rol'] == 'alumno' else None
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"success": True, "mensaje": "Usuario creado correctamente"})

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'DELETE'])
def usuario_id(id):
    u = Usuario.query.get(id)
    if not u: return jsonify({"success": False}), 404
    
    if request.method == 'PUT':
        data = request.json
        u.username = data.get('username', u.username)
        u.rol = data.get('rol', u.rol)
        u.nombre_completo = data.get('nombre', u.nombre_completo)
        u.telefono = data.get('telefono', u.telefono)
        u.nivel = data.get('nivel', u.nivel)
        
        if data.get('password'): 
            u.password = generate_password_hash(data['password'])
            
        u.es_admin = (u.rol in ['admin', 'staff'])
        db.session.commit()
        return jsonify({"success": True})

    if request.method == 'DELETE':
        if u.username == 'admin': 
            return jsonify({"success": False, "mensaje": "No se puede borrar al Super Admin"}), 400
        db.session.delete(u)
        db.session.commit()
        return jsonify({"success": True})

# --- API ASISTENCIA ---
@app.route('/api/asistencia', methods=['GET', 'POST'])
def gestionar_asistencia():
    if request.method == 'GET':
        fecha = request.args.get('fecha', datetime.now().strftime("%Y-%m-%d"))
        # Traer TODOS los alumnos
        alumnos = Usuario.query.filter_by(rol='alumno').all()
        lista = []
        for a in alumnos:
            registro = Asistencia.query.filter_by(fecha=fecha, usuario_id=a.id).first()
            lista.append({
                "id_usuario": a.id, 
                "nombre": a.nombre_completo or a.username, 
                "nivel": a.nivel, 
                "presente": registro.presente if registro else False
            })
        return jsonify(lista)

    if request.method == 'POST':
        data = request.json
        fecha = data.get('fecha')
        
        # Caso Alumno (Individual)
        if 'id_usuario' in data: 
            uid = data['id_usuario']
            if not Asistencia.query.filter_by(fecha=fecha, usuario_id=uid).first():
                db.session.add(Asistencia(fecha=fecha, usuario_id=uid, presente=True))
                
        # Caso Admin/Staff (Lista completa)
        elif 'registros' in data: 
            Asistencia.query.filter_by(fecha=fecha).delete()
            for item in data['registros']:
                db.session.add(Asistencia(fecha=fecha, usuario_id=item['id_usuario'], presente=item['presente']))
                
        db.session.commit()
        return jsonify({"success": True})

# --- OTRAS APIS (Eventos, Pagos, Vestuario) ---
# Se mantienen igual, pero asegurando que Pagos use usuario_id
@app.route('/api/pagos', methods=['GET', 'POST'])
def gestionar_pagos():
    if request.method == 'GET': 
        pagos = Pago.query.order_by(Pago.id.desc()).all()
        return jsonify([{
            "id": p.id, 
            "bailarin": p.usuario.nombre_completo if p.usuario else "Desconocido", 
            "concepto": p.concepto, 
            "monto": p.monto, 
            "fecha": p.fecha_pago
        } for p in pagos])
    if request.method == 'POST':
        data = request.json
        db.session.add(Pago(
            usuario_id=data['usuario_id'], 
            concepto=data['concepto'], 
            monto=float(data['monto']), 
            fecha_pago=datetime.now().strftime("%Y-%m-%d")
        ))
        db.session.commit()
        return jsonify({"success": True})

@app.route('/api/pagos/<int:id>', methods=['DELETE'])
def borrar_pago(id):
    p = Pago.query.get(id)
    if p: db.session.delete(p); db.session.commit(); return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/api/vestuario', methods=['GET', 'POST'])
def gestionar_vestuario():
    if request.method == 'GET': 
        return jsonify([{"id": v.id, "nombre": v.nombre, "tipo": v.tipo, "cantidad": v.cantidad, "talla": v.talla, "estado": v.estado_conservacion} for v in Vestuario.query.all()])
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

# --- API BAILARINES (COMPATIBILIDAD) ---
# Esta ruta permite que el frontend siga cargando listas de "bailarines" pero leyendo de "usuarios"
@app.route('/api/bailarines', methods=['GET'])
def get_bailarines():
    alumnos = Usuario.query.filter_by(rol='alumno').all()
    return jsonify([{
        "id": a.id, 
        "nombre": a.nombre_completo or a.username, 
        "nivel": a.nivel, 
        "contacto": a.telefono
    } for a in alumnos])

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('database'): os.makedirs('database')
        db.create_all()
        # Admin por defecto si no existe
        if not Usuario.query.filter_by(username='admin').first():
            hashed = generate_password_hash('1234')
            db.session.add(Usuario(username='admin', password=hashed, rol='admin', es_admin=True, nombre_completo="Director General"))
            db.session.commit()
            print("--- ADMIN CREADO ---")
    app.run(debug=(os.getenv('NODE_ENV') == 'development'), port=int(os.getenv('PORT', 3000)))

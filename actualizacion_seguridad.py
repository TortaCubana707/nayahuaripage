import os

print("🚀 APLICANDO RESTAURACIÓN TOTAL: INDEX COMPLETO + SEGURIDAD...")

# ==============================================================================
# 1. APP.PY (Backend)
# ==============================================================================
contenido_app_py = """from flask import Flask, render_template, request, jsonify
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
    clean_path = db_file_env.replace('./', '').replace('.\\\\', '')
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
"""

# ==============================================================================
# 2. CSS COMPLETO (Secciones Restauradas)
# ==============================================================================
contenido_css = """
:root {
    --rosa-mexicano: #E6007E; --rosa-oscuro: #B40062; --azul-talavera: #1338BE; --azul-noche: #081a49;
    --amarillo-cempasuchil: #FFD700; --naranja-barro: #E65100; --verde-agave: #00695C; --verde-claro: #10b981;
    --primary: var(--rosa-mexicano); --primary-dark: var(--rosa-oscuro); --accent: var(--amarillo-cempasuchil);
    --dark-bg: var(--azul-noche); --light-bg: #fffbf0; --card-bg: #ffffff;
    --text-main: #263238; --text-light: #546E7A;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); --shadow-hover: 0 15px 30px -5px rgba(0, 0, 0, 0.15);
    --glass: rgba(8, 26, 73, 0.95); --radius: 16px;
}

* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
body { background-color: var(--light-bg); color: var(--text-main); line-height: 1.6; }
a { text-decoration: none; color: inherit; transition: 0.3s; }
ul { list-style: none; }
button { font-family: inherit; }

.zarape-line { height: 6px; background: linear-gradient(to right, var(--rosa-mexicano), var(--azul-talavera), var(--amarillo-cempasuchil), var(--verde-agave), var(--naranja-barro)); width: 100%; position: relative; z-index: 2000; }
.reveal { opacity: 0; transform: translateY(40px); transition: all 0.8s cubic-bezier(0.5, 0, 0, 1); } .reveal.active { opacity: 1; transform: translateY(0); }
.animate-fade { animation: fadeIn 1s ease-out forwards; } .animate-slide { animation: slideUp 0.8s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } } @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } } @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }

/* NAVBAR */
.navbar { background: var(--glass); color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.1); }
.logo-container { display: flex; align-items: center; gap: 15px; } .logo-img { height: 55px; width: auto; object-fit: contain; }
.logo strong { font-size: 1.5rem; color: var(--accent); letter-spacing: -0.5px; } .logo span { font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; }
.nav-links { display: flex; gap: 20px; align-items: center; } .nav-links a:hover { color: var(--accent); }
.btn-login { background: transparent; border: 2px solid var(--accent); color: var(--accent); padding: 6px 18px; border-radius: 50px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.3s; }
.btn-login:hover { background: var(--accent); color: var(--azul-noche); transform: scale(1.05); }

/* HERO */
.hero { height: 90vh; background: linear-gradient(to bottom, rgba(8, 26, 73, 0.6), rgba(230, 0, 126, 0.4)), url('../img/fondo.jpeg'); background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; text-align: center; color: white; position: relative; }
.hero-content { z-index: 2; max-width: 800px; padding-top: 2rem; padding: 0 20px; }
.hero h3 { font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 1rem; color: var(--accent); font-weight: 600; }
.hero h1 { font-size: 5rem; margin-bottom: 1.5rem; line-height: 1; text-shadow: 2px 2px 0px var(--rosa-mexicano); }
.btn-primary { background: var(--rosa-mexicano); color: white; padding: 12px 30px; border-radius: 50px; border: none; font-weight: 700; cursor: pointer; box-shadow: 0 10px 20px rgba(230, 0, 126, 0.4); text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
.btn-primary:hover { background: var(--azul-talavera); transform: translateY(-3px); }

/* DIRECTOR */
.director-frame { position: relative; padding: 10px; border: 2px dashed var(--rosa-mexicano); border-radius: 20px; transform: rotate(2deg); transition: transform 0.3s; }
.director-frame:hover { transform: rotate(0deg); }
.director-img { height: 500px; width: 100%; border-radius: 15px; background-color: #e2e8f0; background-image: url('../img/directora.jpeg'); background-size: cover; background-position: center; box-shadow: -15px 15px 0 var(--azul-noche); transform: rotate(-2deg); border: 4px solid white; }
.floating-badge { position: absolute; bottom: 40px; right: -20px; z-index: 10; background: var(--amarillo-cempasuchil); color: var(--azul-noche); padding: 12px 30px; border-radius: 12px; font-weight: 800; text-transform: uppercase; box-shadow: 0 10px 20px rgba(0,0,0,0.15); animation: float 4s ease-in-out infinite; }
.director-quote { border-left: 4px solid var(--amarillo-cempasuchil); padding-left: 20px; margin-top: 2rem; font-style: italic; color: var(--text-main); font-size: 1.1rem; }
.subtitle-badge { background: rgba(230, 0, 126, 0.1); color: var(--rosa-mexicano); padding: 5px 15px; border-radius: 20px; font-weight: 700; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 15px; display: inline-block; }

/* LAYOUT & TIMELINE */
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; } .section-padding { padding: 6rem 0; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; } .text-center { text-align: center; }
.section-gray { background-color: #FDF2F8; }
.timeline { position: relative; max-width: 900px; margin: 0 auto; }
.timeline::after { content: ''; position: absolute; width: 6px; background: linear-gradient(to bottom, var(--rosa-mexicano), var(--azul-talavera)); top: 0; bottom: 0; left: 50%; margin-left: -3px; border-radius: 10px; }
.timeline-item { padding: 20px 50px; position: relative; width: 50%; } .timeline-item.left { left: 0; text-align: right; } .timeline-item.right { left: 50%; text-align: left; }
.timeline-icon { position: absolute; width: 50px; height: 50px; top: 20px; z-index: 10; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 4px rgba(255,255,255,0.5), 0 4px 10px rgba(0,0,0,0.2); }
.timeline-item.left .timeline-icon { right: -25px; border: 3px solid var(--rosa-mexicano); color: var(--rosa-mexicano); }
.timeline-item.right .timeline-icon { left: -25px; border: 3px solid var(--azul-talavera); color: var(--azul-talavera); }
.timeline-content { padding: 30px; background: white; border-radius: var(--radius); box-shadow: var(--shadow); position: relative; transition: transform 0.3s; border-top: 5px solid var(--naranja-barro); }

/* GALERIA */
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.gallery-item { height: 300px; border-radius: var(--radius); overflow: hidden; position: relative; box-shadow: var(--shadow); cursor: pointer; }
.gallery-item img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; } .gallery-item:hover img { transform: scale(1.1); }
.gallery-overlay { position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(0,0,0,0.8), transparent); padding: 20px; opacity: 0; transition: opacity 0.3s; } .gallery-item:hover .gallery-overlay { opacity: 1; }

/* AGENDA */
.section-dark { background-color: var(--azul-noche); color: white; position: relative; }
.calendar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
.event-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--radius); padding: 25px; display: flex; align-items: center; gap: 20px; transition: 0.3s; }
.event-card:hover { border-color: var(--rosa-mexicano); background: rgba(255,255,255,0.1); }
.event-card .date { background: var(--amarillo-cempasuchil); color: var(--azul-noche); padding: 15px 10px; border-radius: 12px; text-align: center; min-width: 85px; font-weight: 800; }
.date .day { display: block; font-size: 2rem; }
.map-box { height: 450px; border-radius: var(--radius); overflow: hidden; border: 4px solid white; box-shadow: var(--shadow); }
.schedule-box { background: white; padding: 2.5rem; border-radius: var(--radius); box-shadow: var(--shadow); border-top: 6px solid var(--rosa-mexicano); }
.group-name { font-size: 1.1rem; font-weight: bold; color: var(--azul-talavera); display: block; }

/* DASHBOARD */
.dashboard-layout { display: flex; min-height: 100vh; }
.sidebar { width: 260px; background: var(--dark-bg); color: white; padding: 2rem; display: flex; flex-direction: column; }
.menu-item { padding: 12px 15px; margin-bottom: 8px; border-radius: 8px; color: #94a3b8; display: flex; gap: 10px; transition: 0.2s; cursor: pointer; }
.menu-item:hover { background: rgba(255,255,255,0.1); color: white; } .menu-item.active { background: var(--rosa-mexicano); color: white; }
.main-content { flex: 1; padding: 4rem 3rem; overflow-y: auto; background-color: var(--light-bg); }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 30px; margin-bottom: 4rem; }
.stat-card { background: white; padding: 2rem; border-radius: 16px; display: flex; align-items: center; gap: 20px; box-shadow: var(--shadow); }
.stat-icon { width: 60px; height: 60px; border-radius: 50%; background: #fdf2f8; color: var(--rosa-mexicano); display: flex; justify-content: center; align-items: center; font-size: 1.8rem; }
.card-table { background: white; padding: 3rem; border-radius: 16px; box-shadow: var(--shadow); overflow: visible; margin-bottom: 4rem; }

.form-grid-responsive { display: flex; flex-wrap: wrap; gap: 30px; align-items: flex-end; }
.form-group-item { flex: 1 1 220px; margin-bottom: 15px; } .form-group-item.btn-container { flex: 0 0 auto; margin-bottom: 15px; }
.form-control { width: 100%; padding: 14px 18px; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 1rem; transition: border-color 0.3s; } .form-control:focus { outline: none; border-color: var(--rosa-mexicano); box-shadow: 0 0 0 4px rgba(230, 0, 126, 0.1); }
.btn-success { background: var(--verde-agave); color: white; padding: 12px 25px; border-radius: 12px; border: none; font-weight: bold; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: 0.3s; }
.btn-success:hover { background: #004D40; transform: translateY(-2px); }
.tabla-moderna { width: 100%; border-collapse: separate; border-spacing: 0; }
.tabla-moderna th { text-align: left; padding: 1.5rem; background: #f9f9f9; border-bottom: 2px solid #eee; color: var(--text-light); text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; }
.tabla-moderna td { padding: 1.5rem; border-bottom: 1px solid #eee; }
.btn-delete, .btn-edit { width: 40px; height: 40px; border-radius: 50%; border: none; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; margin-left: 5px; }
.btn-delete { background: #fee2e2; color: #ef4444; } .btn-edit { background: #e0f2fe; color: #0284c7; }
.checkbox-asistencia { width: 25px; height: 25px; cursor: pointer; accent-color: var(--rosa-mexicano); }

/* Modal */
.modal { display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(8, 26, 73, 0.85); backdrop-filter: blur(5px); }
.modal-content { background: white; margin: 10vh auto; padding: 3rem; width: 90%; max-width: 400px; border-radius: 20px; border-top: 8px solid var(--rosa-mexicano); overflow-y: auto; max-height: 90vh; }
.input-group input { width: 100%; padding: 12px 12px 12px 40px; margin-bottom: 15px; border: 2px solid #eee; border-radius: 8px; }
.input-icon { position: absolute; left: 12px; top: 12px; color: #aaa; }
.close-btn { position: absolute; right: 20px; top: 15px; font-size: 1.5rem; cursor: pointer; }
.auth-toggle-text { text-align: center; margin-top: 15px; font-size: 0.9rem; color: var(--text-light); }
.auth-toggle-link { color: var(--rosa-mexicano); font-weight: bold; cursor: pointer; text-decoration: underline; }

/* SOCIAL ICONS */
.social-btn { display: inline-flex; justify-content: center; align-items: center; width: 55px; height: 55px; border-radius: 50%; background-color: rgba(255, 255, 255, 0.1); color: white; font-size: 1.8rem; text-decoration: none; transition: all 0.3s ease; margin: 0 10px; border: 2px solid transparent; position: relative; z-index: 100; cursor: pointer; }
.social-btn:hover { transform: translateY(-5px) scale(1.1); background-color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
.social-btn.whatsapp:hover { color: #25D366; border-color: #25D366; } .social-btn.facebook:hover { color: #1877F2; border-color: #1877F2; } .social-btn.instagram:hover { color: #E4405F; border-color: #E4405F; } .social-btn.youtube:hover { color: #FF0000; border-color: #FF0000; } .social-btn.tiktok:hover { color: #000000; border-color: #00f2ea; background: linear-gradient(45deg, #00f2ea, #ff0050); color:white; border:none; }

/* Dashboard Menu Móvil */
.dashboard-menu-btn { display: none; position: fixed; top: 15px; left: 15px; z-index: 2000; background: var(--rosa-mexicano); color: white; padding: 10px; border-radius: 50%; box-shadow: var(--shadow); border: none; cursor: pointer; }
.sidebar-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 900; }

@media (max-width: 768px) {
    .navbar { padding: 15px; flex-wrap: wrap; }
    .logo-container { width: 100%; justify-content: space-between; }
    .menu-toggle { display: block; font-size: 2rem; color: white; cursor: pointer; }
    .nav-links { display: none; width: 100%; flex-direction: column; background: var(--dark-bg); position: absolute; top: 100%; left: 0; padding: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
    .nav-links.active { display: flex; }
    .grid-2 { grid-template-columns: 1fr; gap: 40px; }
    .sidebar { display: flex; position: fixed; top: 0; left: -100%; width: 80%; height: 100vh; z-index: 1000; }
    .sidebar.active { left: 0; }
    .sidebar-overlay.active { display: block; }
    .dashboard-menu-btn { display: block; }
    .dashboard-layout { display: block; position: relative; }
    .main-content { padding: 5rem 1.5rem 2rem; }
    .form-grid-responsive { gap: 20px; }
    .timeline::after { left: 20px; } .timeline-item { width: 100%; padding-left: 60px; padding-right: 10px; text-align: left; } .timeline-item.right { left: 0; } .timeline-icon { left: 0; } .timeline-item.left .timeline-icon, .timeline-item.right .timeline-icon { left: -4px; right: auto; }
}
"""

# ==============================================================================
# 3. HTML INDEX (Contenido Completo Restaurado)
# ==============================================================================
contenido_index_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nayahuari | Tradición Viva</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}?v=restaurado">
    <style>
        .logo-container { display: flex; align-items: center; gap: 15px; } .logo-img { height: 55px; width: auto; object-fit: contain; } .logo-text { display: flex; flex-direction: column; text-align: left; }
        .social-btn { display: inline-flex; justify-content: center; align-items: center; width: 55px; height: 55px; border-radius: 50%; background-color: rgba(255, 255, 255, 0.1); color: white; font-size: 1.8rem; text-decoration: none; transition: all 0.3s ease; margin: 0 10px; border: 2px solid transparent; position: relative; z-index: 100; cursor: pointer; }
        .social-btn:hover { transform: translateY(-5px) scale(1.1); background-color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .social-btn.whatsapp:hover { color: #25D366; border-color: #25D366; } .social-btn.facebook:hover { color: #1877F2; border-color: #1877F2; } .social-btn.instagram:hover { color: #E4405F; border-color: #E4405F; } .social-btn.youtube:hover { color: #FF0000; border-color: #FF0000; } .social-btn.tiktok:hover { color: #000000; border-color: #00f2ea; background: linear-gradient(45deg, #00f2ea, #ff0050); color:white; border:none; }
        .click-anim { animation: pulsacion 0.3s ease; } @keyframes pulsacion { 0% { transform: scale(0.9); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="zarape-line"></div>
    <nav class="navbar">
      <div class="logo logo-container"><img src="{{ url_for('static', filename='img/logo.jpeg') }}" alt="Nayahuari" class="logo-img" onerror="this.style.display='none'"><div class="logo-text"><span>BALLET FOLKLÓRICO</span><strong>NAYAHUARI</strong></div></div>
      <ul class="nav-links">
        <li><a href="#inicio">Inicio</a></li><li><a href="#directora">Directora</a></li><li><a href="#trayectoria">Historia</a></li><li><a href="#galeria">Galería</a></li><li><a href="#agenda">Agenda</a></li><li><a href="#ubicacion">Ubicación</a></li>
        <li><button id="btnAuth" class="btn-login" onclick="abrirLogin()"><span class="material-icons">account_circle</span> Acceso</button></li>
        <li id="nav-admin-panel" style="display: none;"><a href="/dashboard" class="btn-panel-admin"><span class="material-icons" style="font-size:16px;">dashboard</span> PANEL</a></li>
      </ul>
      <div class="menu-toggle"><span class="material-icons">menu</span></div>
    </nav>
    <header id="inicio" class="hero"><div class="hero-content reveal"><h3>Bajo la dirección de Carmen Servin</h3><h1>NAYAHUARI</h1><p>Orgullo, Tradición y Corazón en cada zapateado.</p><a href="#agenda" class="btn-primary">Ver Próximas Presentaciones</a></div></header>
    
    <!-- SECCIONES COMPLETAS -->
    <section id="directora" class="container section-padding"><div class="grid-2 director-wrapper"><div class="text-content reveal"><span class="subtitle-badge">Dirección General</span><h2>Mtra. Carmen Servin</h2><p>Con años de trayectoria preservando nuestras raíces, la maestra Carmen ha llevado al Ballet Folklórico Nayahuari a representar nuestra cultura con dignidad y excelencia.</p><div class="director-quote"><p>"La danza es el lenguaje oculto del alma mexicana."</p></div></div><div class="image-content reveal"><div class="director-frame"><div class="director-img"></div> <div class="floating-badge">Fundadora</div></div></div></div></section>
    
    <section id="trayectoria" class="section-gray section-padding"><div class="container"><div class="text-center mb-2 reveal"><h2 class="section-title" style="font-size: 2.5rem; color: var(--dark-bg);">Nuestra Historia</h2></div><div class="timeline"><div class="timeline-item left reveal"><div class="timeline-icon"><span class="material-icons">star</span></div><div class="timeline-content"><span class="year-badge">2015</span><h3>El Inicio</h3><p>Nace el sueño con solo 8 bailarines apasionados.</p></div></div><div class="timeline-item right reveal"><div class="timeline-icon"><span class="material-icons">emoji_events</span></div><div class="timeline-content"><span class="year-badge">2018</span><h3>Reconocimiento Nacional</h3><p>Obtuvimos mención honorífica en concurso estatal.</p></div></div><div class="timeline-item left reveal"><div class="timeline-icon"><span class="material-icons">flight_takeoff</span></div><div class="timeline-content"><span class="year-badge">2024</span><h3>Expansión</h3><p>Nayahuari crece, abriendo nuevos grupos infantiles.</p></div></div></div></div></section>
    
    <section id="galeria" class="container section-padding"><div class="text-center mb-2 reveal"><h2 class="section-title" style="font-size: 2.5rem; color: var(--dark-bg); margin-bottom: 1rem;">Nuestra Galería</h2></div><div class="gallery-grid reveal"><div class="gallery-item"><img src="https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=500&auto=format&fit=crop&q=60" alt="Danza 1"><div class="gallery-overlay"></div></div><div class="gallery-item"><img src="https://images.unsplash.com/photo-1547153760-18fc86324498?w=500&auto=format&fit=crop&q=60" alt="Danza 2"><div class="gallery-overlay"></div></div><div class="gallery-item"><img src="https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500&auto=format&fit=crop&q=60" alt="Danza 3"><div class="gallery-overlay"></div></div><div class="gallery-item"><img src="https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=500&auto=format&fit=crop&q=60" alt="Danza 4"><div class="gallery-overlay"></div></div></div></section>
    
    <section id="agenda" class="section-dark section-padding"><div class="container" style="position: relative; z-index: 2;"><div class="agenda-header reveal"><h2>Próximas Presentaciones</h2></div><div class="calendar-grid" id="eventsContainer"><p style="color: #aaa;">Cargando cartelera...</p></div></div></section>
    
    <section id="ubicacion" class="container section-padding"><h2 class="text-center mb-2 reveal" style="font-size: 2.5rem;">Ensaya con Nosotros</h2><div class="grid-2" style="align-items: start;"><div class="map-box reveal"><iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3733.309536863266!2d-103.3957248!3d20.6572559!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMjDCsDM5JzI2LjEiTiAxMDPCsDIzJzQ0LjYiVw!5e0!3m2!1ses!2smx!4v1620000000000!5m2!1ses!2smx" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe></div><div class="schedule-box reveal"><h3 style="color: var(--azul-talavera); display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;"><span class="material-icons">schedule</span> Horarios de Clase</h3><ul class="schedule-list" style="list-style: none; padding: 0;"><li style="margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 1rem;"><span class="group-name" style="display: block; font-weight: bold; color: var(--rosa-oscuro);">Principiantes</span><span class="group-time" style="color: var(--text-light);">Lun y Mié: 4:00 PM - 6:00 PM</span></li><li style="margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 1rem;"><span class="group-name" style="display: block; font-weight: bold; color: var(--naranja-barro);">Intermedios</span><span class="group-time" style="color: var(--text-light);">Mar y Jue: 5:00 PM - 7:00 PM</span></li></ul></div></div></section>
    
    <footer class="section-dark" style="padding: 4rem 0; text-align: center; margin-top: 4rem; border-top: 4px solid var(--amarillo-cempasuchil);"><div class="container"><h2 style="color: var(--amarillo-cempasuchil); margin-bottom: 1rem; letter-spacing: 2px;">NAYAHUARI</h2><p style="opacity: 0.8; font-size: 1.1rem; margin-bottom: 2rem;">Orgullo, Tradición y Pasión.</p><div class="social-links" style="display: flex; justify-content: center; gap: 25px; margin-bottom: 2rem; position: relative; z-index: 10;"><a href="https://wa.me/5211234567890" target="_blank" class="social-btn whatsapp"><i class="fab fa-whatsapp"></i></a><a href="https://www.facebook.com/balletnayahuari" target="_blank" class="social-btn facebook"><i class="fab fa-facebook-f"></i></a><a href="https://www.instagram.com/balletnayahuari" target="_blank" class="social-btn instagram"><i class="fab fa-instagram"></i></a><a href="https://www.tiktok.com/@balletnayahuari" target="_blank" class="social-btn tiktok"><i class="fab fa-tiktok"></i></a><a href="https://www.youtube.com/@balletnayahuari" target="_blank" class="social-btn youtube"><i class="fab fa-youtube"></i></a></div><div style="padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.9rem; opacity: 0.5;"><p>Ballet Folklórico Nayahuari © 2026.</p></div></div></footer>

    <!-- MODAL -->
    <div id="loginModal" class="modal"><div class="modal-content"><span class="close-btn" onclick="document.getElementById('loginModal').style.display='none'">&times;</span><div class="login-header"><h2 style="color: var(--rosa-mexicano);" id="modalTitle">Bienvenido</h2><p>Ingresa al portal</p></div><div id="loginSection"><form id="universalLoginForm" style="margin-top: 20px;"><div class="input-group"><span class="material-icons input-icon">person</span><input type="text" id="loginUser" placeholder="Usuario / Email" required></div><div class="input-group"><span class="material-icons input-icon">lock</span><input type="password" id="loginPass" placeholder="Contraseña" required></div><button type="submit" class="btn-primary full-width">Iniciar Sesión</button></form><p class="auth-toggle-text">¿No tienes cuenta? <span class="auth-toggle-link" onclick="toggleAuthMode('register')">Regístrate como Alumno</span></p></div><div id="registerSection" style="display:none;"><form id="publicRegisterForm" style="margin-top: 20px;"><div class="input-group"><span class="material-icons input-icon">badge</span><input type="text" id="regNombre" placeholder="Nombre Completo" required></div><div class="input-group"><span class="material-icons input-icon">email</span><input type="email" id="regUser" placeholder="Correo (ej: usuario@gmail.com)" required></div><div class="input-group"><span class="material-icons input-icon">phone</span><input type="text" id="regTel" placeholder="Teléfono"></div><div class="input-group"><span class="material-icons input-icon">lock</span><input type="password" id="regPass" placeholder="Contraseña" required></div><button type="submit" class="btn-success full-width">Crear Cuenta</button></form><p class="auth-toggle-text">¿Ya tienes cuenta? <span class="auth-toggle-link" onclick="toggleAuthMode('login')">Inicia Sesión</span></p></div><div id="loginMessage" class="login-message" style="margin-top:15px; font-weight:bold;"></div></div></div>
    <script src="{{ url_for('static', filename='js/main.js') }}?v=restaurado"></script>
    <script>function abrirLogin(){if(localStorage.getItem('usuario_logueado')==='true'){window.location.href='/dashboard'}else{document.getElementById('loginModal').style.display='block';toggleAuthMode('login')}} document.querySelectorAll('.social-btn').forEach(btn=>{btn.addEventListener('click',function(e){this.classList.add('click-anim');setTimeout(()=>this.classList.remove('click-anim'),300)})});</script>
</body>
</html>
"""

# ==============================================================================
# 4. DASHBOARD (Panel de Administración)
# ==============================================================================
contenido_dashboard_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Gestión</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}?v=restaurado">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
</head>
<body>
    <div class="zarape-line"></div>
    <div class="dashboard-layout">
        <aside class="sidebar">
            <div class="logo" style="margin-bottom: 3rem; text-align: center;"><span style="font-size: 0.7rem; letter-spacing: 2px; color: var(--accent);">PANEL</span><br><strong style="color: white; font-size: 1.5rem;">NAYAHUARI</strong></div>
            <nav id="adminMenu" style="display: none;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 10px; font-weight: bold; padding-left: 15px;">ADMINISTRACIÓN</p>
                <a href="#" onclick="mostrarSeccion('usuarios')" id="nav-usuarios" class="menu-item active"><span class="material-icons">group</span> Usuarios</a>
                <a href="#" onclick="mostrarSeccion('eventos')" id="nav-eventos" class="menu-item"><span class="material-icons">event</span> Eventos</a>
                <a href="#" onclick="mostrarSeccion('pagos')" id="nav-pagos" class="menu-item"><span class="material-icons">payments</span> Pagos</a>
                <a href="#" onclick="mostrarSeccion('vestuario')" id="nav-vestuario" class="menu-item"><span class="material-icons">checkroom</span> Vestuario</a>
                <a href="#" onclick="mostrarSeccion('asistencia')" id="nav-asistencia" class="menu-item"><span class="material-icons">checklist</span> Asistencia (QR)</a>
            </nav>
            <nav id="userMenu" style="display: none;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 10px; font-weight: bold; padding-left: 15px;">MI CUENTA</p>
                <a href="#" onclick="mostrarSeccion('alumno-asistencia')" id="nav-alumno-asistencia" class="menu-item active"><span class="material-icons">qr_code_scanner</span> Escanear Asistencia</a>
                <a href="#" onclick="mostrarSeccion('alumno-eventos')" id="nav-alumno-eventos" class="menu-item"><span class="material-icons">event_note</span> Agenda</a>
                <a href="#" onclick="mostrarSeccion('alumno-vestuario')" id="nav-alumno-vestuario" class="menu-item"><span class="material-icons">checkroom</span> Mis Préstamos</a>
            </nav>
            <div style="margin-top: auto;"><hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1rem 0;"><a href="/" class="menu-item"><span class="material-icons">public</span> Ver Web</a><button onclick="cerrarSesion()" class="menu-item" style="width: 100%; background: none; border: none; cursor: pointer; color: #ef4444;"><span class="material-icons">logout</span> Cerrar Sesión</button></div>
        </aside>
        <main class="main-content">
            <header class="header-bar animate-fade"><div><h1 id="pageTitle" style="color: var(--dark-bg);">Bienvenido</h1></div><div style="display: flex; align-items: center; gap: 10px; background: white; padding: 5px 15px; border-radius: 50px; box-shadow: var(--shadow);"><div style="background: var(--amarillo-cempasuchil); width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center;"><span class="material-icons" style="color: var(--azul-noche); font-size: 1.2rem;">person</span></div><div><span id="userNameDisplay" style="display: block; font-weight: bold; font-size: 0.9rem; color: var(--azul-noche);">Usuario</span><span id="userRoleDisplay" style="display: block; font-size: 0.7rem; color: var(--text-light);">Rol</span></div></div></header>
            
            <div id="section-usuarios" class="admin-section animate-slide">
                <div class="card-table">
                    <h3 style="margin-bottom: 1.5rem; color: var(--rosa-mexicano);">Gestión de Usuarios</h3>
                    <form id="formUsuario" class="form-grid-responsive">
                        <input type="hidden" id="usuarioId">
                        <div class="form-group-item"><label>Usuario (Login)</label><input type="text" id="usuarioUsername" class="form-control" required></div>
                        <div class="form-group-item"><label>Nombre Completo</label><input type="text" id="usuarioNombre" class="form-control"></div>
                        <div class="form-group-item"><label>Teléfono</label><input type="text" id="usuarioTelefono" class="form-control"></div>
                        <div class="form-group-item"><label>Contraseña</label><input type="password" id="usuarioPassword" class="form-control" placeholder="Nueva contraseña"></div>
                        <div class="form-group-item"><label>Rol</label><select id="usuarioRol" class="form-control"><option value="alumno">Alumno</option><option value="maestro">Maestro</option><option value="administrativo">Administrativo</option><option value="admin">Administrador</option></select></div>
                        <div class="form-group-item btn-container"><button type="submit" class="btn-success" style="height: 48px; width: 100%;"><span class="material-icons">save</span> Guardar</button></div>
                    </form>
                </div>
                <div class="card-table"><table class="tabla-moderna"><thead><tr><th>Usuario</th><th>Rol</th><th>Nombre</th><th>Acciones</th></tr></thead><tbody id="tablaUsuarios"></tbody></table></div>
            </div>
            
            <div id="section-eventos" class="admin-section animate-slide" style="display:none;"><div class="card-table"><h3>Eventos</h3><form id="formEvento" class="form-grid-responsive"><div class="form-group-item"><input type="text" id="tituloEvento" class="form-control" placeholder="Título" required></div><div class="form-group-item"><input type="text" id="fechaEvento" class="form-control" placeholder="Fecha"></div><div class="form-group-item"><input type="text" id="lugarEvento" class="form-control" placeholder="Lugar"></div><div class="form-group-item"><input type="text" id="horaEvento" class="form-control" placeholder="Hora"></div><div class="btn-container"><button class="btn-success">Crear</button></div></form></div><div class="card-table"><table class="tabla-moderna"><tbody id="tablaEventos"></tbody></table></div></div>
            <div id="section-pagos" class="admin-section animate-slide" style="display:none;"><div class="card-table"><h3>Pagos</h3><form id="formPago" class="form-grid-responsive"><div class="form-group-item"><select id="pagoUsuario" class="form-control" required></select></div><div class="form-group-item"><input type="text" id="pagoConcepto" class="form-control" placeholder="Concepto"></div><div class="form-group-item"><input type="number" id="pagoMonto" class="form-control" placeholder="Monto"></div><div class="btn-container"><button class="btn-success">Registrar</button></div></form></div><div class="card-table"><table class="tabla-moderna"><tbody id="tablaPagos"></tbody></table></div></div>
            <div id="section-vestuario" class="admin-section animate-slide" style="display:none;"><div class="card-table"><h3>Vestuario</h3><form id="formVestuario" class="form-grid-responsive"><div class="form-group-item"><input type="text" id="vestuarioNombre" class="form-control" placeholder="Nombre"></div><div class="form-group-item"><select id="vestuarioTipo" class="form-control"><option>Traje</option><option>Accesorio</option></select></div><div class="form-group-item"><input type="number" id="vestuarioCantidad" class="form-control" value="1"></div><div class="form-group-item"><input type="text" id="vestuarioTalla" class="form-control" placeholder="Talla"></div><div class="form-group-item"><select id="vestuarioEstado" class="form-control"><option>Bueno</option><option>Reparación</option></select></div><div class="btn-container"><button class="btn-success">Agregar</button></div></form></div><div class="card-table"><table class="tabla-moderna"><tbody id="tablaVestuario"></tbody></table></div></div>
            <div id="section-asistencia" class="admin-section animate-slide" style="display:none;"><div class="card-table"><h3>Código QR Asistencia</h3><div style="display:flex;flex-direction:column;align-items:center;"><input type="hidden" id="fechaAsistencia"><div id="qrcode"></div><button onclick="generarQR()" class="btn-success" style="margin-top:20px;">Generar QR Hoy</button></div></div></div>
            
            <div id="section-alumno-asistencia" class="alumno-section animate-slide" style="display:none;"><div class="user-welcome-card" style="background: linear-gradient(135deg, var(--rosa-mexicano), var(--azul-talavera)); color: white; padding: 3rem; border-radius: 20px; text-align: center;"><h2 style="font-size: 2.5rem; margin-bottom: 10px;">¡Hola!</h2><p>Escanea el QR.</p><div style="margin-top: 2rem;"><div id="reader" style="display:none;"></div><button onclick="iniciarEscaner()" id="btnEscanearQR" class="btn-success" style="font-size: 1.2rem; padding: 15px 40px; border: none; background: white; color: var(--azul-talavera);">Escanear</button></div></div></div>
            <div id="section-alumno-eventos" class="alumno-section animate-slide" style="display:none;"><h3>Agenda</h3><div id="alumnoEventosContainer" class="calendar-grid"></div></div>
            <div id="section-alumno-vestuario" class="alumno-section animate-slide" style="display:none;"><h3>Inventario</h3><div class="card-table"><div id="alumnoVestuarioContainer"></div></div></div>
        </main>
    </div>
    <script src="{{ url_for('static', filename='js/main.js') }}?v=restaurado"></script>
</body>
</html>
"""

# ==============================================================================
# 5. JS (Lógica de Roles, QR y Registro Público)
# ==============================================================================
contenido_js = """
const API_URL = '/api';
let usuarioRol = localStorage.getItem('usuario_rol');
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre') || 'Invitado';
let usuarioId = localStorage.getItem('usuario_id');

document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('active'); observer.unobserve(entry.target); }});
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    if (document.querySelector('.dashboard-layout')) configurarDashboard();
    if (document.getElementById('eventsContainer')) {
        actualizarInterfazLanding();
        cargarEventosLanding();
        configurarModalLogin();
    }
});

function configurarDashboard() {
    if (!usuarioLogueado) { window.location.href = '/'; return; }
    document.getElementById('userNameDisplay').textContent = nombreUsuario;
    document.getElementById('userRoleDisplay').textContent = usuarioRol ? usuarioRol.toUpperCase() : 'USUARIO';
    document.querySelectorAll('.admin-section, .alumno-section').forEach(el => el.style.display = 'none');
    document.getElementById('adminMenu').style.display = 'none';
    document.getElementById('userMenu').style.display = 'none';

    if (usuarioRol === 'admin') {
        mostrarMenu('adminMenu');
        ['nav-usuarios', 'nav-eventos', 'nav-pagos', 'nav-vestuario', 'nav-asistencia'].forEach(id => mostrarElemento(id));
        cargarTodoAdmin(); mostrarSeccion('usuarios');
    } else if (usuarioRol === 'administrativo') {
        mostrarMenu('adminMenu'); ocultarElemento('nav-usuarios'); ocultarElemento('nav-eventos');
        cargarPagosAdmin(); cargarVestuarioAdmin(); bindForm('formPago', agregarPago); bindForm('formVestuario', agregarVestuario); mostrarSeccion('pagos');
    } else if (usuarioRol === 'maestro') {
        mostrarMenu('adminMenu'); ocultarElemento('nav-usuarios'); ocultarElemento('nav-eventos'); ocultarElemento('nav-pagos');
        cargarVestuarioAdmin(); bindForm('formVestuario', agregarVestuario); mostrarSeccion('asistencia');
    } else {
        document.getElementById('userMenu').style.display = 'block';
        cargarEventosAlumno(); cargarVestuarioAlumno(); mostrarSeccion('alumno-asistencia');
    }
}
function mostrarMenu(id) { document.getElementById(id).style.display = 'block'; }
function mostrarElemento(id) { document.getElementById(id).style.display = 'flex'; }
function ocultarElemento(id) { document.getElementById(id).style.display = 'none'; }
function bindForm(id, h) { const f = document.getElementById(id); if(f) f.addEventListener('submit', h); }
function cargarTodoAdmin() { cargarUsuariosAdmin(); cargarEventosAdmin(); cargarPagosAdmin(); cargarVestuarioAdmin(); const hoy=new Date().toISOString().split('T')[0]; if(document.getElementById('fechaAsistencia')) document.getElementById('fechaAsistencia').value=hoy; bindForm('formUsuario', agregarUsuario); bindForm('formEvento', agregarEvento); bindForm('formPago', agregarPago); bindForm('formVestuario', agregarVestuario); }
window.mostrarSeccion = function(s) {
    document.querySelectorAll('.admin-section, .alumno-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    const t = document.getElementById(`section-${s}`);
    const n = document.getElementById(`nav-${s}`);
    if(t) { t.style.display = 'block'; setTimeout(() => t.classList.add('active'), 10); }
    if(n) n.classList.add('active');
}
async function cargarUsuariosAdmin() { const r=await fetch(`${API_URL}/usuarios`); const d=await r.json(); const t=document.getElementById('tablaUsuarios'); const s=document.getElementById('pagoUsuario'); if(s){ s.innerHTML='<option value="">Seleccionar...</option>'; d.filter(u=>u.rol==='alumno').forEach(u=>s.innerHTML+=`<option value="${u.id}">${u.nombre||u.username}</option>`);} if(t) t.innerHTML=d.map(u=>`<tr><td>${u.username}</td><td>${u.rol}</td><td>${u.nombre||'-'}</td><td style="text-align:right"><button onclick="borrarUsuario(${u.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarUsuario(e) { e.preventDefault(); const d={username:document.getElementById('usuarioUsername').value, rol:document.getElementById('usuarioRol').value, nombre:document.getElementById('usuarioNombre').value, telefono:document.getElementById('usuarioTelefono').value, password:document.getElementById('usuarioPassword').value}; await fetch(`${API_URL}/usuarios`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}); document.getElementById('formUsuario').reset(); cargarUsuariosAdmin(); }
window.borrarUsuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); cargarUsuariosAdmin(); }};
async function cargarPagosAdmin() { const res = await fetch(`${API_URL}/pagos`); const data = await res.json(); const tbody = document.getElementById('tablaPagos'); if(tbody) tbody.innerHTML = data.map(p => `<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarPago(e) { e.preventDefault(); await fetch(`${API_URL}/pagos`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ usuario_id: document.getElementById('pagoUsuario').value, concepto: document.getElementById('pagoConcepto').value, monto: document.getElementById('pagoMonto').value })}); document.getElementById('formPago').reset(); cargarPagosAdmin(); }
window.borrarPago=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/pagos/${id}`, {method:'DELETE'}); cargarPagosAdmin(); }};
async function cargarEventosAdmin() { const res = await fetch(`${API_URL}/eventos`); const data = await res.json(); const tbody = document.getElementById('tablaEventos'); if(tbody) tbody.innerHTML = data.map(ev => `<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarEvento(e) { e.preventDefault(); await fetch(`${API_URL}/eventos`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ titulo: document.getElementById('tituloEvento').value, fecha: document.getElementById('fechaEvento').value, lugar: document.getElementById('lugarEvento').value, hora: document.getElementById('horaEvento').value })}); document.getElementById('formEvento').reset(); cargarEventosAdmin(); }
window.borrarEvento=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/eventos/${id}`, {method:'DELETE'}); cargarEventosAdmin(); }};
async function cargarVestuarioAdmin() { const res = await fetch(`${API_URL}/vestuario`); const data = await res.json(); const tbody = document.getElementById('tablaVestuario'); if(tbody) tbody.innerHTML = data.map(v => `<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarVestuario(e) { e.preventDefault(); await fetch(`${API_URL}/vestuario`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ nombre: document.getElementById('vestuarioNombre').value, tipo: document.getElementById('vestuarioTipo').value, cantidad: document.getElementById('vestuarioCantidad').value, talla: document.getElementById('vestuarioTalla').value, estado: document.getElementById('vestuarioEstado').value })}); document.getElementById('formVestuario').reset(); cargarVestuarioAdmin(); }
window.borrarVestuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/vestuario/${id}`, {method:'DELETE'}); cargarVestuarioAdmin(); }};

window.buscarAsistencia = async function() { const fecha=document.getElementById('fechaAsistencia').value; const res=await fetch(`${API_URL}/asistencia?fecha=${fecha}`); const data=await res.json(); const tbody=document.getElementById('tablaAsistencia'); tbody.innerHTML = data.map(item => `<tr><td>${item.nombre}</td><td style="text-align:center"><input type="checkbox" class="checkbox-asistencia" data-id="${item.id_usuario}" ${item.presente?'checked':''}></td></tr>`).join(''); }
window.guardarAsistencia = async function() { const fecha=document.getElementById('fechaAsistencia').value; const checkboxes=document.querySelectorAll('.checkbox-asistencia'); const registros=[]; checkboxes.forEach(cb=>{ registros.push({id_usuario:cb.dataset.id, presente:cb.checked}) }); await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ fecha: fecha, registros: registros }) }); alert("Guardado"); }
window.generarQR = function() { const hoy = new Date().toISOString().split('T')[0]; new QRCode(document.getElementById('qrcode'), { text: `NAYAHUARI_ASISTENCIA_${hoy}`, width: 200, height: 200 }); }

let html5QrcodeScanner = null;
window.iniciarEscaner = function() { document.getElementById('reader').style.display = "block"; if (html5QrcodeScanner) html5QrcodeScanner.clear(); html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 }); html5QrcodeScanner.render(async (decodedText) => { html5QrcodeScanner.clear(); document.getElementById('reader').style.display = "none"; try { const res = await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ qr_data: decodedText, id_usuario: usuarioId }) }); const data = await res.json(); alert(data.success ? `✅ ${data.mensaje}` : `❌ ${data.mensaje}`); } catch(e) { alert("Error"); } }); }

async function cargarEventosAlumno(){const r=await fetch(`${API_URL}/eventos`);const d=await r.json();const c=document.getElementById('alumnoEventosContainer');if(c)c.innerHTML=d.map(ev=>`<div class="stat-card"><div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha}</p></div></div>`).join('')}
async function cargarVestuarioAlumno(){const r=await fetch(`${API_URL}/vestuario`);const d=await r.json();const c=document.getElementById('alumnoVestuarioContainer');if(c)c.innerHTML=d.map(v=>`<div class="stat-card"><div><h4>${v.nombre}</h4><p>${v.talla}</p></div></div>`).join('')}

function configurarModalLogin() { 
    const modal = document.getElementById("loginModal");
    window.toggleAuthMode = function(mode) {
        document.getElementById('loginSection').style.display = (mode === 'login') ? 'block' : 'none';
        document.getElementById('registerSection').style.display = (mode === 'register') ? 'block' : 'none';
        document.getElementById('modalTitle').textContent = (mode === 'login') ? 'Bienvenido' : 'Crear Cuenta';
    }
    const loginForm = document.getElementById('universalLoginForm');
    if(loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const res = await fetch(`${API_URL}/login`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ usuario: document.getElementById('loginUser').value, password: document.getElementById('loginPass').value }) });
                const data = await res.json();
                if(data.success) {
                    localStorage.setItem('usuario_logueado', 'true'); localStorage.setItem('usuario_rol', data.rol); localStorage.setItem('es_admin', data.es_admin); localStorage.setItem('usuario_nombre', data.nombre); localStorage.setItem('usuario_id', data.id);
                    setTimeout(() => window.location.href = '/dashboard', 500);
                } else { alert(data.mensaje); }
            } catch(e) { alert("Error"); }
        });
    }
    const regForm = document.getElementById('publicRegisterForm');
    if(regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const user = document.getElementById('regUser').value;
            if (!user.endsWith('@gmail.com')) { alert("Solo correos @gmail.com"); return; }
            const data = { username: user, password: document.getElementById('regPass').value, nombre: document.getElementById('regNombre').value, telefono: document.getElementById('regTel').value };
            try {
                const res = await fetch(`${API_URL}/register`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                const result = await res.json();
                if(result.success) { alert("Cuenta creada"); toggleAuthMode('login'); regForm.reset(); } 
                else { alert(result.mensaje); }
            } catch(e) { alert("Error"); }
        });
    }
}
function actualizarInterfazLanding() {
    if(usuarioLogueado) {
        const btnAuth = document.getElementById('btnAuth');
        if(btnAuth) { btnAuth.innerHTML = '<span class="material-icons">logout</span> Salir'; btnAuth.onclick = cerrarSesion; }
        const btnPanel = document.getElementById('nav-admin-panel');
        if(btnPanel) { btnPanel.style.display = 'block'; btnPanel.querySelector('a').href = '/dashboard'; }
    }
}
async function cargarEventosLanding() {
    const c = document.getElementById('eventsContainer');
    if(!c) return;
    try {
        const res = await fetch(`${API_URL}/eventos`); const data = await res.json();
        c.innerHTML = data.length ? data.map(ev => `<div class="event-card reveal"><div class="date"><span class="day">${ev.fecha.split(' ')[0]}</span></div><div class="details"><h4>${ev.titulo}</h4><p>${ev.lugar}</p></div></div>`).join('') : '<p>Próximamente</p>';
    } catch(e){}
}
window.cerrarSesion = function() { if(confirm("¿Cerrar sesión?")) { localStorage.clear(); window.location.href='/'; } };
"""

# Ejecución
print("🔧 Escribiendo archivos de sistema actualizados...")
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

with open("app.py", "w", encoding="utf-8") as f: f.write(contenido_app_py)
with open("static/css/estilos.css", "w", encoding="utf-8") as f: f.write(contenido_css)
with open("static/js/main.js", "w", encoding="utf-8") as f: f.write(contenido_js)
with open("templates/dashboard.html", "w", encoding="utf-8") as f: f.write(contenido_dashboard_html)
with open("templates/index.html", "w", encoding="utf-8") as f: f.write(contenido_index_html)

print("✅ RESTAURACIÓN COMPLETADA.")
print("1. Detén el servidor (Ctrl+C).")
print("2. IMPORTANTE: Borra 'database/mi_app.sqlite' (o la carpeta database) para aplicar cambios.")
print("3. Ejecuta 'python app.py'.")
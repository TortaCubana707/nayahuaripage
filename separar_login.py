import os

print("🚀 ACTUALIZANDO SISTEMA COMPLETO CON CSS PROFESIONAL Y FUNCIONAL...")

# ==============================================================================
# 1. APP.PY (Backend - Rutas y Lógica)
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

# --- UTILIDADES ---
def validar_password_segura(password):
    if len(password) < 8: return False, "Mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password): return False, "Falta una mayúscula."
    if not re.search(r"\\d", password): return False, "Falta un número."
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
    imagen_url = db.Column(db.String(500))

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

# --- RUTAS VISTAS ---
@app.route('/')
def inicio(): return render_template('index.html')

@app.route('/login')
def vista_login(): return render_template('login.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

# --- APIS ---
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
    
    val, msg = validar_password_segura(data['password'])
    if not val: return jsonify({"success": False, "mensaje": msg}), 400

    nuevo = Usuario(
        username=data['username'], 
        password=generate_password_hash(data['password']), 
        rol='alumno', 
        es_admin=False, 
        nombre_completo=data.get('nombre', ''), 
        telefono=data.get('telefono', ''), 
        nivel='Principiante'
    )
    db.session.add(nuevo); db.session.commit()
    return jsonify({"success": True, "mensaje": "Registro exitoso"})

# CRUDs
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

@app.route('/api/eventos', methods=['GET', 'POST'])
def gestionar_eventos():
    if request.method == 'GET': return jsonify([{"id": e.id, "titulo": e.titulo, "fecha": e.fecha, "lugar": e.lugar, "hora": e.hora, "imagen_url": getattr(e, 'imagen_url', '')} for e in Evento.query.all()])
    if request.method == 'POST': d=request.json; db.session.add(Evento(titulo=d['titulo'], fecha=d['fecha'], lugar=d.get('lugar',''), hora=d.get('hora',''), imagen_url=d.get('imagen_url',''))); db.session.commit(); return jsonify({"success": True})
@app.route('/api/eventos/<int:id>', methods=['PUT', 'DELETE'])
def evento_id(id):
    e = Evento.query.get(id); 
    if not e: return jsonify({"success": False}), 404
    if request.method=='DELETE': db.session.delete(e); db.session.commit(); return jsonify({"success": True})
    if request.method=='PUT': d=request.json; e.titulo=d.get('titulo',e.titulo); e.fecha=d.get('fecha',e.fecha); e.lugar=d.get('lugar',e.lugar); e.hora=d.get('hora',e.hora); e.imagen_url=d.get('imagen_url',e.imagen_url); db.session.commit(); return jsonify({"success": True})

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
def get_bailarines():
    return jsonify([{"id": a.id, "nombre": a.nombre_completo or a.username, "contacto": a.telefono} for a in Usuario.query.filter_by(rol='alumno').all()])

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('database'): os.makedirs('database')
        db.create_all()
        if not Usuario.query.filter_by(username='admin').first():
            db.session.add(Usuario(username='admin', password=generate_password_hash('Admin1234'), rol='admin', es_admin=True, nombre_completo="Director General"))
            db.session.commit()
    app.run(host='0.0.0.0', debug=(os.getenv('NODE_ENV') == 'development'), port=int(os.getenv('PORT', 3000)))
"""

# ==============================================================================
# 2. CSS COMPLETO (Universal, Login y Dashboard)
# ==============================================================================
contenido_css = """
/* =========================================
   1. VARIABLES Y BASE
   ========================================= */
:root {
    --rosa-mexicano: #E6007E;
    --rosa-oscuro: #B40062;
    --azul-talavera: #1338BE;
    --azul-noche: #081a49;
    --amarillo-cempasuchil: #FFD700;
    --naranja-barro: #E65100;
    --verde-agave: #00695C;
    --verde-claro: #10b981;
    --rojo-error: #ef4444;

    /* Semántica */
    --primary: var(--rosa-mexicano);
    --primary-dark: var(--rosa-oscuro);
    --secondary: var(--azul-talavera);
    --accent: var(--amarillo-cempasuchil);
    --bg-dark: var(--azul-noche);
    --bg-light: #f8fafc;
    --bg-card: #ffffff;
    --text-main: #334155;
    --text-light: #64748b;
    
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --glass: rgba(8, 26, 73, 0.95);
    --radius: 12px;
    --nav-height: 80px;
    --sidebar-width: 260px;
}

* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
html, body { height: 100%; width: 100%; }
body { background-color: var(--bg-light); color: var(--text-main); line-height: 1.6; overflow-x: hidden; }
a { text-decoration: none; color: inherit; transition: 0.3s; }
ul { list-style: none; }
button { font-family: inherit; cursor: pointer; }
input, select, textarea { font-family: inherit; font-size: 16px; }

/* Decoración */
.zarape-line {
    height: 6px;
    background: linear-gradient(to right, var(--rosa-mexicano), var(--azul-talavera), var(--amarillo-cempasuchil), var(--verde-agave), var(--naranja-barro));
    width: 100%; position: fixed; top: 0; left: 0; z-index: 3000;
}

/* =========================================
   2. COMPONENTES (Botones, Inputs)
   ========================================= */
.btn {
    display: inline-flex; justify-content: center; align-items: center;
    padding: 10px 24px; border-radius: 50px; font-weight: 700;
    transition: all 0.3s ease; border: none; gap: 8px; font-size: 0.95rem;
    text-decoration: none; /* Vital para <a> que parecen botones */
}
.btn-primary {
    background: var(--primary); color: white;
    box-shadow: 0 4px 10px rgba(230,0,126,0.3);
}
.btn-primary:hover { background: var(--primary-dark); transform: translateY(-2px); box-shadow: var(--shadow-hover); color: white; }

.btn-success {
    background: var(--verde-agave); color: white; border-radius: var(--radius);
}
.btn-success:hover { background: #004d40; transform: translateY(-2px); color: white; }

.btn-login {
    background: transparent; border: 2px solid var(--accent); color: var(--accent);
    padding: 6px 18px; border-radius: 50px; font-weight: 700; display: flex; align-items: center; gap: 8px; transition: 0.3s;
    position: relative; z-index: 1001; /* Asegura click sobre capas */
}
.btn-login:hover { background: var(--accent); color: var(--bg-dark); transform: scale(1.05); }

/* Inputs */
.form-control {
    width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0;
    border-radius: var(--radius); font-size: 1rem; transition: 0.3s;
    background: #fff; height: 50px;
}
.form-control:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(230,0,126,0.1); }
.input-group { position: relative; margin-bottom: 20px; }
.input-icon { position: absolute; left: 15px; top: 13px; color: var(--text-light); }
.input-group input { padding-left: 45px; }

/* =========================================
   3. LANDING PAGE
   ========================================= */
.navbar {
    background: var(--glass); height: var(--nav-height);
    padding: 0 5%; display: flex; justify-content: space-between; align-items: center;
    position: sticky; top: 0; z-index: 1000; backdrop-filter: blur(10px);
    margin-top: 6px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.logo-container { display: flex; align-items: center; gap: 15px; }
.logo-img { height: 50px; width: auto; object-fit: contain; }
.logo-text { display: flex; flex-direction: column; line-height: 1.2; color: white; text-align: left; }
.logo-text strong { font-size: 1.4rem; color: var(--accent); letter-spacing: 1px; }
.logo-text span { font-size: 0.7rem; letter-spacing: 2px; color: rgba(255,255,255,0.8); text-transform: uppercase; }

.nav-links { display: flex; gap: 25px; align-items: center; margin: 0; padding: 0; }
.nav-links a { color: white; font-weight: 500; font-size: 0.95rem; position: relative; }
.nav-links a:not(.btn):hover { color: var(--accent); }
.menu-toggle { display: none; color: white; font-size: 2rem; cursor: pointer; }

/* Hero */
.hero {
    height: 85vh;
    background: linear-gradient(to bottom, rgba(8, 26, 73, 0.7), rgba(230, 0, 126, 0.3)), url('../img/fondo.jpeg');
    background-size: cover; background-position: center; background-attachment: fixed;
    display: flex; align-items: center; justify-content: center;
    text-align: center; color: white; padding: 0 20px;
    margin-top: -6px;
}
.hero h1 { font-size: 4rem; line-height: 1.1; margin-bottom: 1rem; text-shadow: 2px 2px 0 var(--rosa-mexicano); }
.hero h3 { font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 1.5rem; color: var(--accent); }

/* Secciones */
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.section-padding { padding: 6rem 0; }
.text-center { text-align: center; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; }
.section-dark { background-color: var(--bg-dark); color: white; position: relative; }
.section-gray { background-color: var(--bg-light); }

/* Componentes Visuales */
.director-img { height: 450px; width: 100%; border-radius: var(--radius); background: #e2e8f0 url('../img/directora.jpeg') center/cover; box-shadow: -15px 15px 0 var(--bg-dark); transform: rotate(-2deg); border: 4px solid white; }
.director-frame { position: relative; padding: 10px; border: 2px dashed var(--primary); border-radius: var(--radius); transform: rotate(2deg); margin: 20px; }
.subtitle-badge { background: rgba(230,0,126,0.1); color: var(--primary); padding: 5px 15px; border-radius: 50px; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; display: inline-block; margin-bottom: 1rem; }
.director-quote { border-left: 4px solid var(--accent); padding-left: 20px; margin-top: 2rem; font-style: italic; font-size: 1.1rem; }

/* Timeline */
.timeline { position: relative; max-width: 800px; margin: 0 auto; padding: 40px 0; }
.timeline::after { content: ''; position: absolute; width: 4px; background: linear-gradient(to bottom, var(--primary), var(--secondary)); top: 0; bottom: 0; left: 50%; margin-left: -2px; border-radius: 2px; }
.timeline-item { padding: 10px 40px; position: relative; width: 50%; box-sizing: border-box; }
.timeline-item.left { left: 0; text-align: right; } .timeline-item.right { left: 50%; text-align: left; }
.timeline-icon { position: absolute; width: 40px; height: 40px; top: 15px; z-index: 10; background: white; border-radius: 50%; border: 3px solid var(--primary); display: flex; align-items: center; justify-content: center; color: var(--primary); box-shadow: 0 0 0 4px rgba(255,255,255,0.8); }
.timeline-item.left .timeline-icon { right: -20px; left: auto; }
.timeline-item.right .timeline-icon { left: -20px; border-color: var(--secondary); color: var(--secondary); }
.timeline-content { padding: 25px; background: white; border-radius: 12px; box-shadow: var(--shadow); border-top: 4px solid var(--naranja-barro); }
.year-badge { background: var(--bg-dark); color: var(--accent); padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; }

/* Galería */
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
.gallery-item { height: 300px; border-radius: var(--radius); overflow: hidden; position: relative; box-shadow: var(--shadow); cursor: pointer; }
.gallery-item img { width: 100%; height: 100%; object-fit: cover; transition: 0.5s; }
.gallery-item:hover img { transform: scale(1.1); }
.gallery-overlay { position: absolute; bottom: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); opacity: 0; transition: 0.3s; }
.gallery-item:hover .gallery-overlay { opacity: 1; }

/* Agenda Cards */
.calendar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
.event-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--radius); padding: 25px; display: flex; align-items: center; gap: 20px; transition: 0.3s; }
.event-card:hover { border-color: var(--primary); background: rgba(255,255,255,0.1); }
.event-card .date { background: var(--accent); color: var(--bg-dark); padding: 10px; border-radius: 12px; text-align: center; min-width: 75px; font-weight: 800; display: flex; flex-direction: column; justify-content: center; height: 75px; overflow: hidden; }
.date .day { font-size: 1.8rem; line-height: 1; } .date .month { font-size: 0.8rem; text-transform: uppercase; }

/* Footer */
footer { padding: 4rem 0; text-align: center; border-top: 5px solid var(--accent); margin-top: 0; }
.social-links { display: flex; justify-content: center; gap: 20px; margin: 2rem 0; flex-wrap: wrap; }
.social-btn { width: 50px; height: 50px; border-radius: 50%; background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; transition: 0.3s; position: relative; z-index: 10; border: 2px solid transparent; }
.social-btn:hover { background: white; transform: translateY(-5px); color: var(--primary); }
.social-btn.whatsapp:hover { color: #25D366; } .social-btn.facebook:hover { color: #1877F2; } .social-btn.instagram:hover { color: #E4405F; } .social-btn.youtube:hover { color: #FF0000; } .social-btn.tiktok:hover { background: black; color: white; border: none; }

/* =========================================
   4. LOGIN PAGE (Centrado y Limpio)
   ========================================= */
.login-body {
    background: linear-gradient(rgba(8, 26, 73, 0.8), rgba(8, 26, 73, 0.8)), url('../img/fondo.jpeg');
    background-size: cover; background-position: center;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; width: 100%; padding: 20px;
}
.login-card {
    background: white; padding: 2.5rem; border-radius: 20px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.3); text-align: center;
    border-top: 6px solid var(--primary);
    width: 100%; max-width: 450px;
    animation: slideUp 0.5s ease-out;
}
.logo-circle { width: 80px; height: 80px; background: white; border-radius: 50%; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; border: 3px solid var(--primary); }
.logo-circle img { width: 60%; }
.auth-footer { margin-top: 20px; border-top: 1px solid #eee; padding-top: 20px; font-size: 0.9rem; }
.auth-toggle-link { color: var(--primary); font-weight: bold; cursor: pointer; text-decoration: underline; }

/* =========================================
   5. DASHBOARD LAYOUT
   ========================================= */
.dashboard-layout { display: flex; min-height: 100vh; background-color: var(--bg-light); padding-top: 6px; }

.sidebar {
    width: var(--sidebar-width); background: var(--bg-dark); color: white;
    padding: 2rem; position: fixed; top: 6px; left: 0; height: calc(100vh - 6px);
    overflow-y: auto; z-index: 100; transition: transform 0.3s;
    box-shadow: 4px 0 15px rgba(0,0,0,0.1);
}
.sidebar .logo { margin-bottom: 3rem; text-align: center; }

.menu-item {
    padding: 12px 15px; margin-bottom: 8px; border-radius: 10px;
    color: #cbd5e1; display: flex; gap: 10px; cursor: pointer; transition: 0.2s; align-items: center;
}
.menu-item:hover { background: rgba(255,255,255,0.1); color: white; }
.menu-item.active { background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(230,0,126,0.3); }

.main-content {
    margin-left: var(--sidebar-width); width: calc(100% - var(--sidebar-width));
    padding: 3rem 4rem; overflow-y: auto; min-height: calc(100vh - 6px);
    transition: margin 0.3s;
}

.header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 15px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 2rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: var(--radius); display: flex; align-items: center; gap: 15px; box-shadow: var(--shadow); border-left: 5px solid var(--primary); }
.stat-icon { width: 50px; height: 50px; border-radius: 50%; background: #fdf2f8; color: var(--primary); display: flex; justify-content: center; align-items: center; font-size: 1.5rem; }

.card-table { background: white; padding: 2rem; border-radius: var(--radius); box-shadow: var(--shadow); margin-bottom: 2rem; overflow: visible; }
.form-grid-responsive { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; align-items: end; }
.form-group-item { width: 100%; } .form-group-item.btn-container { grid-column: span 1; }
.form-group-item label { display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-light); }

/* Tablas */
.table-responsive { overflow-x: auto; margin-top: 1rem; }
.tabla-moderna { width: 100%; border-collapse: collapse; min-width: 600px; }
.tabla-moderna th { text-align: left; padding: 1rem; background: #f8fafc; border-bottom: 2px solid #e2e8f0; color: var(--text-light); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
.tabla-moderna td { padding: 1rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.btn-icon-action { width: 35px; height: 35px; border-radius: 8px; border: none; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; margin-left: 5px; transition: 0.2s; }
.btn-edit { background: #e0f2fe; color: var(--secondary); }
.btn-delete { background: #fee2e2; color: var(--rojo-error); }

/* QR */
#qrcode-container { background: white; padding: 15px; border-radius: 12px; display: inline-block; border: 2px dashed var(--secondary); margin: 20px 0; }
#reader { width: 100%; max-width: 350px; margin: 0 auto; border-radius: 12px; overflow: hidden; border: 4px solid white; box-shadow: var(--shadow); }

/* Mobile Menu Button */
.dashboard-menu-btn { display: none; position: fixed; top: 15px; left: 15px; z-index: 2000; background: var(--primary); color: white; width: 45px; height: 45px; border-radius: 50%; border: none; align-items: center; justify-content: center; box-shadow: var(--shadow-lg); cursor: pointer; }
.sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1050; backdrop-filter: blur(2px); }

/* =========================================
   6. RESPONSIVO (MÓVIL TOTAL)
   ========================================= */
@media (max-width: 968px) {
    /* Navbar */
    .navbar { padding: 0.8rem 1.5rem; }
    .nav-links { display: none; width: 100%; flex-direction: column; background: var(--bg-dark); position: absolute; top: 100%; left: 0; padding: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.5); gap: 15px; }
    .nav-links.active { display: flex; animation: fadeIn 0.3s; }
    .menu-toggle { display: block; }
    
    /* Landing */
    .hero h1 { font-size: 3rem; }
    .grid-2 { grid-template-columns: 1fr; gap: 40px; }
    .gallery-grid { grid-template-columns: 1fr; }
    .timeline::after { left: 20px; margin-left: 0; }
    .timeline-item { width: 100%; padding-left: 60px; padding-right: 0; text-align: left; }
    .timeline-item.right { left: 0; }
    .timeline-icon { left: 0; }
    .timeline-item.left .timeline-icon, .timeline-item.right .timeline-icon { left: -4px; right: auto; }
    .director-img { height: 350px; }
    
    /* Dashboard Mobile */
    .sidebar { transform: translateX(-100%); width: 280px; box-shadow: none; z-index: 2000; }
    .sidebar.active { transform: translateX(0); box-shadow: 4px 0 20px rgba(0,0,0,0.3); }
    .sidebar-overlay.active { display: block; }
    .dashboard-menu-btn { display: flex; }
    .main-content { margin-left: 0; width: 100%; padding: 5rem 1.2rem 2rem; }
    .stats-grid { grid-template-columns: 1fr; }
    .form-grid-responsive { grid-template-columns: 1fr; gap: 15px; }
    .card-table { padding: 1.5rem; }
    
    /* Botones */
    .btn-login { width: 100%; justify-content: center; }
}
"""

# ==============================================================================
# 3. JS (Lógica Completa)
# ==============================================================================
contenido_js = """
const API_URL = '/api';
let usuarioRol = localStorage.getItem('usuario_rol');
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre') || 'Invitado';
let usuarioId = localStorage.getItem('usuario_id');

document.addEventListener('DOMContentLoaded', () => {
    // Menú móvil Landing
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => { navLinks.classList.toggle('active'); });
    }

    // Menú móvil Dashboard
    const dashBtn = document.querySelector('.dashboard-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if(dashBtn && sidebar) {
        dashBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            if(overlay) overlay.classList.toggle('active');
        });
    }
    if(overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    // Animaciones
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // Router
    if (document.querySelector('.dashboard-layout')) configurarDashboard();
    if (document.getElementById('eventsContainer')) {
        actualizarInterfazLanding();
        cargarEventosLanding();
    }
    
    // Login Logic if present
    const loginForm = document.getElementById('universalLoginForm');
    if(loginForm) configurarModalLogin();
});

function configurarModalLogin() { 
    // Toggle
    window.toggleAuthMode = function(mode) {
        document.getElementById('loginSection').style.display = (mode === 'login') ? 'block' : 'none';
        document.getElementById('registerSection').style.display = (mode === 'register') ? 'block' : 'none';
        document.getElementById('modalTitle').textContent = (mode === 'login') ? 'Bienvenido' : 'Crear Cuenta';
        document.getElementById('loginMessage').textContent = '';
    }

    const loginForm = document.getElementById('universalLoginForm');
    const registerForm = document.getElementById('publicRegisterForm');

    if(loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('loginMessage');
            try {
                const res = await fetch(`${API_URL}/login`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ usuario: document.getElementById('loginUser').value, password: document.getElementById('loginPass').value }) });
                const data = await res.json();
                if(data.success) {
                    localStorage.setItem('usuario_logueado', 'true'); localStorage.setItem('usuario_rol', data.rol); localStorage.setItem('es_admin', data.es_admin); localStorage.setItem('usuario_nombre', data.nombre); localStorage.setItem('usuario_id', data.id);
                    setTimeout(() => window.location.href = '/dashboard', 500);
                } else { msg.textContent = data.mensaje; msg.style.color = 'red'; }
            } catch(e) { msg.textContent = "Error de conexión"; }
        });
    }

    if(registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('loginMessage');
            const user = document.getElementById('regUser').value;
            if (!user.endsWith('@gmail.com')) { msg.textContent = "Solo correos @gmail.com"; msg.style.color = 'red'; return; }

            const data = { username: user, password: document.getElementById('regPass').value, nombre: document.getElementById('regNombre').value, telefono: document.getElementById('regTel').value };
            try {
                msg.textContent = "Registrando..."; msg.style.color = '#555';
                const res = await fetch(`${API_URL}/register`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                const result = await res.json();
                if(result.success) {
                    msg.textContent = "¡Cuenta creada! Inicia sesión."; msg.style.color = 'var(--verde-agave)';
                    setTimeout(() => toggleAuthMode('login'), 2000); registerForm.reset();
                } else { msg.textContent = result.mensaje; msg.style.color = 'red'; }
            } catch(e) { msg.textContent = "Error"; }
        });
    }
}

function configurarDashboard() {
    if (!usuarioLogueado) { window.location.href = '/'; return; }
    const nameDisplay = document.getElementById('userNameDisplay');
    if(nameDisplay) nameDisplay.textContent = nombreUsuario;
    const roleDisplay = document.getElementById('userRoleDisplay');
    if(roleDisplay) roleDisplay.textContent = usuarioRol ? usuarioRol.toUpperCase() : 'USUARIO';

    document.querySelectorAll('.admin-section, .alumno-section').forEach(el => el.style.display = 'none');
    document.getElementById('adminMenu').style.display = 'none';
    document.getElementById('userMenu').style.display = 'none';

    if (usuarioRol === 'admin') {
        mostrarMenu('adminMenu');
        ['nav-usuarios', 'nav-eventos', 'nav-pagos', 'nav-vestuario', 'nav-asistencia'].forEach(id => mostrarElemento(id));
        cargarTodoAdmin();
        mostrarSeccion('usuarios');
    } 
    else if (usuarioRol === 'administrativo' || usuarioRol === 'staff') {
        mostrarMenu('adminMenu');
        ocultarElemento('nav-usuarios'); ocultarElemento('nav-eventos');
        mostrarElemento('nav-pagos'); mostrarElemento('nav-vestuario'); mostrarElemento('nav-asistencia');
        cargarPagosAdmin(); cargarVestuarioAdmin();
        bindForm('formPago', agregarPago); bindForm('formVestuario', agregarVestuario);
        mostrarSeccion('pagos');
    }
    else if (usuarioRol === 'maestro') {
        mostrarMenu('adminMenu');
        ocultarElemento('nav-usuarios'); ocultarElemento('nav-eventos'); ocultarElemento('nav-pagos');
        mostrarElemento('nav-vestuario'); mostrarElemento('nav-asistencia');
        cargarVestuarioAdmin(); bindForm('formVestuario', agregarVestuario);
        mostrarSeccion('asistencia');
    }
    else {
        document.getElementById('userMenu').style.display = 'block';
        cargarEventosAlumno(); cargarVestuarioAlumno(); 
        mostrarSeccion('alumno-asistencia');
    }
}

function mostrarMenu(id) { document.getElementById(id).style.display = 'block'; }
function mostrarElemento(id) { document.getElementById(id).style.display = 'flex'; }
function ocultarElemento(id) { document.getElementById(id).style.display = 'none'; }
function bindForm(id, h) { const f = document.getElementById(id); if(f) f.addEventListener('submit', h); }
function cargarTodoAdmin() { cargarUsuariosAdmin(); cargarEventosAdmin(); cargarPagosAdmin(); cargarVestuarioAdmin(); const hoy=new Date().toISOString().split('T')[0]; if(document.getElementById('fechaAsistencia'))document.getElementById('fechaAsistencia').value=hoy; bindForm('formUsuario', agregarUsuario); bindForm('formEvento', agregarEvento); bindForm('formPago', agregarPago); bindForm('formVestuario', agregarVestuario); }
window.mostrarSeccion = function(s) {
    document.querySelectorAll('.admin-section, .alumno-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    const t = document.getElementById(`section-${s}`);
    const n = document.getElementById(`nav-${s}`);
    if(t) { t.style.display = 'block'; setTimeout(() => t.classList.add('active'), 10); }
    if(n) n.classList.add('active');
    const title = document.getElementById('pageTitle');
    if(title) title.textContent = s.toUpperCase().replace('ALUMNO-', '');
}

async function cargarUsuariosAdmin() { const r=await fetch(`${API_URL}/usuarios`); const d=await r.json(); const t=document.getElementById('tablaUsuarios'); const s=document.getElementById('pagoUsuario'); if(s){ s.innerHTML='<option value="">Seleccionar...</option>'; d.filter(u=>u.rol==='alumno').forEach(u=>s.innerHTML+=`<option value="${u.id}">${u.nombre||u.username}</option>`);} if(t) t.innerHTML=d.map(u=>`<tr><td><strong>${u.username}</strong></td><td>${u.rol}</td><td style="text-align:right"><button onclick="borrarUsuario(${u.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarUsuario(e) { e.preventDefault(); const d={username:document.getElementById('usuarioUsername').value, rol:document.getElementById('usuarioRol').value, nombre:document.getElementById('usuarioNombre').value, telefono:document.getElementById('usuarioTelefono').value, password:document.getElementById('usuarioPassword').value}; await fetch(`${API_URL}/usuarios`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}); document.getElementById('formUsuario').reset(); cargarUsuariosAdmin(); }
window.borrarUsuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); cargarUsuariosAdmin(); }};

async function cargarPagosAdmin() { const res = await fetch(`${API_URL}/pagos`); const data = await res.json(); const tbody = document.getElementById('tablaPagos'); if(tbody) tbody.innerHTML = data.map(p => `<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarPago(e) { e.preventDefault(); await genericPost(`${API_URL}/pagos`, { usuario_id: document.getElementById('pagoUsuario').value, concepto: document.getElementById('pagoConcepto').value, monto: document.getElementById('pagoMonto').value }); document.getElementById('formPago').reset(); cargarPagosAdmin(); }
window.borrarPago=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/pagos/${id}`, {method:'DELETE'}); cargarPagosAdmin(); }};
async function cargarEventosAdmin() { const res = await fetch(`${API_URL}/eventos`); const data = await res.json(); const tbody = document.getElementById('tablaEventos'); if(tbody) tbody.innerHTML = data.map(ev => `<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarEvento(e) { e.preventDefault(); await genericPost(`${API_URL}/eventos`, { titulo: document.getElementById('tituloEvento').value, fecha: document.getElementById('fechaEvento').value, lugar: document.getElementById('lugarEvento').value, hora: document.getElementById('horaEvento').value }); document.getElementById('formEvento').reset(); cargarEventosAdmin(); }
window.borrarEvento=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/eventos/${id}`, {method:'DELETE'}); cargarEventosAdmin(); }};
async function cargarVestuarioAdmin() { const res = await fetch(`${API_URL}/vestuario`); const data = await res.json(); const tbody = document.getElementById('tablaVestuario'); if(tbody) tbody.innerHTML = data.map(v => `<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarVestuario(e) { e.preventDefault(); await genericPost(`${API_URL}/vestuario`, { nombre: document.getElementById('vestuarioNombre').value, tipo: document.getElementById('vestuarioTipo').value, cantidad: document.getElementById('vestuarioCantidad').value, talla: document.getElementById('vestuarioTalla').value, estado: document.getElementById('vestuarioEstado').value }); document.getElementById('formVestuario').reset(); cargarVestuarioAdmin(); }
window.borrarVestuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/vestuario/${id}`, {method:'DELETE'}); cargarVestuarioAdmin(); }};
async function genericPost(url, data) { try { await fetch(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); return true; } catch(e){ return false; } }

// --- ASISTENCIA & QR ---
window.buscarAsistencia = async function() { const fecha=document.getElementById('fechaAsistencia').value; const res=await fetch(`${API_URL}/asistencia?fecha=${fecha}`); const data=await res.json(); const tbody=document.getElementById('tablaAsistencia'); tbody.innerHTML = data.map(item => `<tr><td>${item.nombre}</td><td style="text-align:center"><input type="checkbox" class="checkbox-asistencia" data-id="${item.id_usuario}" ${item.presente?'checked':''}></td></tr>`).join(''); }
window.guardarAsistencia = async function() { const fecha=document.getElementById('fechaAsistencia').value; const checkboxes=document.querySelectorAll('.checkbox-asistencia'); const registros=[]; checkboxes.forEach(cb=>{ registros.push({id_usuario:cb.dataset.id, presente:cb.checked}) }); await genericPost(`${API_URL}/asistencia`, {fecha:fecha, registros:registros}); alert("Guardado"); }

window.generarQR = function() {
    const container = document.getElementById('qrcode');
    const hoy = new Date().toISOString().split('T')[0];
    const codigo = `NAYAHUARI_ASISTENCIA_${hoy}`;
    container.innerHTML = "";
    new QRCode(container, { text: codigo, width: 200, height: 200, colorDark : "#081a49", colorLight : "#ffffff", correctLevel : QRCode.CorrectLevel.H });
    document.getElementById('qr-date-label').textContent = `Código para: ${hoy}`;
}

let html5QrcodeScanner = null;
window.iniciarEscaner = function() {
    document.getElementById('reader').style.display = "block";
    if (html5QrcodeScanner) html5QrcodeScanner.clear();
    html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(onScanSuccess, (e)=>{});
}
async function onScanSuccess(decodedText) {
    html5QrcodeScanner.clear(); document.getElementById('reader').style.display = "none";
    try {
        const res = await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ qr_data: decodedText, id_usuario: usuarioId }) });
        const data = await res.json();
        alert(data.success ? `✅ ${data.mensaje}` : `❌ ${data.mensaje}`);
        if(data.success) { 
            const btn = document.getElementById('btnEscanearQR');
            btn.innerText = "¡Registrado!"; btn.style.backgroundColor = "var(--verde-agave)"; btn.disabled = true;
        }
    } catch(e) { alert("Error de conexión"); }
}

async function cargarEventosAlumno(){const r=await fetch(`${API_URL}/eventos`);const d=await r.json();const c=document.getElementById('alumnoEventosContainer');if(c)c.innerHTML=d.map(ev=>`<div class="stat-card"><div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha}</p></div></div>`).join('')}
async function cargarVestuarioAlumno(){const r=await fetch(`${API_URL}/vestuario`);const d=await r.json();const c=document.getElementById('alumnoVestuarioContainer');if(c)c.innerHTML=d.map(v=>`<div class="stat-card" style="border-left:5px solid var(--accent)"><div><h4 style="margin:0">${v.nombre}</h4><p>${v.talla}</p></div></div>`).join('')}

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
        c.innerHTML = data.length ? data.map(ev => `<div class="event-card reveal"><div class="date"><span class="day">${ev.fecha.split(' ')[0]}</span></div><div class="details"><h4>${ev.titulo}</h4><p>${ev.lugar}</p></div></div>`).join('') : '<p>Próximamente...</p>';
    } catch(e){}
}
window.cerrarSesion = function() { if(confirm("¿Cerrar sesión?")) { localStorage.clear(); window.location.href='/'; } };
"""

# ==============================================================================
# 4. HTML INDEX (Landing Page Correcta)
# ==============================================================================
contenido_index_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nayahuari | Tradición Viva</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}?v=final_fix">
    <style>
        .logo-container { display: flex; align-items: center; gap: 15px; }
        .logo-img { height: 55px; width: auto; object-fit: contain; }
        .logo-text { display: flex; flex-direction: column; text-align: left; }
        .social-btn { display: inline-flex; justify-content: center; align-items: center; width: 55px; height: 55px; border-radius: 50%; background-color: rgba(255, 255, 255, 0.1); color: white; font-size: 1.8rem; text-decoration: none; transition: all 0.3s ease; margin: 0 10px; border: 2px solid transparent; position: relative; z-index: 100; cursor: pointer; }
        .social-btn:hover { transform: translateY(-5px) scale(1.1); background-color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .social-btn.whatsapp:hover { color: #25D366; border-color: #25D366; }
        .social-btn.facebook:hover { color: #1877F2; border-color: #1877F2; }
        .social-btn.instagram:hover { color: #E4405F; border-color: #E4405F; }
        .social-btn.youtube:hover { color: #FF0000; border-color: #FF0000; }
        .social-btn.tiktok:hover { color: #000000; border-color: #00f2ea; background: linear-gradient(45deg, #00f2ea, #ff0050); color:white; border:none; }
        .click-anim { animation: pulsacion 0.3s ease; } @keyframes pulsacion { 0% { transform: scale(0.9); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
    </style>
</head>
<body>
    <div class="zarape-line"></div>
    <nav class="navbar">
      <div class="logo logo-container">
        <img src="{{ url_for('static', filename='img/logo.jpeg') }}" alt="Nayahuari" class="logo-img" onerror="this.style.display='none'">
        <div class="logo-text"><span>BALLET FOLKLÓRICO</span><strong>NAYAHUARI</strong></div>
      </div>
      <ul class="nav-links">
        <li><a href="#inicio">Inicio</a></li><li><a href="#directora">Directora</a></li><li><a href="#trayectoria">Historia</a></li><li><a href="#galeria">Galería</a></li><li><a href="#agenda">Agenda</a></li><li><a href="#ubicacion">Ubicación</a></li>
        <li><button id="btnAuth" class="btn-login" onclick="abrirLogin()"><span class="material-icons">account_circle</span> Acceso</button></li>
        <li id="nav-admin-panel" style="display: none;"><a href="/dashboard" class="btn-panel-admin"><span class="material-icons" style="font-size:16px;">dashboard</span> PANEL</a></li>
      </ul>
      <div class="menu-toggle"><span class="material-icons">menu</span></div>
    </nav>
    <header id="inicio" class="hero"><div class="hero-content reveal"><h3>Bajo la dirección de Carmen Servin</h3><h1>NAYAHUARI</h1><p>Orgullo, Tradición y Corazón en cada zapateado.</p><a href="#agenda" class="btn-primary">Ver Próximas Presentaciones</a></div></header>
    <section id="directora" class="container section-padding"><div class="grid-2 director-wrapper"><div class="text-content reveal"><span class="subtitle-badge">Dirección General</span><h2>Mtra. Carmen Servin</h2><p>Con años de trayectoria preservando nuestras raíces, la maestra Carmen ha llevado al Ballet Folklórico Nayahuari a representar nuestra cultura con dignidad y excelencia. Nayahuari no es solo un grupo, es una familia unida por la danza y el amor a México.</p><div class="director-quote"><p>"La danza es el lenguaje oculto del alma mexicana, donde cada paso cuenta una historia."</p></div></div><div class="image-content reveal"><div class="director-frame"><div class="director-img"></div> <div class="floating-badge">Fundadora</div></div></div></div></section>
    <section id="trayectoria" class="section-gray section-padding"><div class="container"><div class="text-center mb-2 reveal"><h2 class="section-title" style="font-size: 2.5rem; color: var(--dark-bg);">Nuestra Historia</h2><p class="section-subtitle" style="color: var(--text-light);">Un viaje lleno de pasión y logros.</p></div><div class="timeline"><div class="timeline-item left reveal"><div class="timeline-icon"><span class="material-icons">star</span></div><div class="timeline-content"><span class="year-badge">2015</span><h3>El Inicio</h3><p>Nace el sueño. La maestra Carmen Servin funda el grupo con solo 8 bailarines apasionados por el folklore.</p></div></div><div class="timeline-item right reveal"><div class="timeline-icon"><span class="material-icons">emoji_events</span></div><div class="timeline-content"><span class="year-badge">2018</span><h3>Reconocimiento Nacional</h3><p>Obtuvimos mención honorífica por vestuario y ejecución en el concurso estatal.</p></div></div><div class="timeline-item left reveal"><div class="timeline-icon"><span class="material-icons">flight_takeoff</span></div><div class="timeline-content"><span class="year-badge">2024</span><h3>Expansión</h3><p>Nayahuari crece, abriendo nuevos grupos infantiles y juveniles.</p></div></div></div></div></section>
    <section id="galeria" class="container section-padding"><div class="text-center mb-2 reveal"><h2 class="section-title" style="font-size: 2.5rem; color: var(--dark-bg); margin-bottom: 1rem;">Nuestra Galería</h2><p class="section-subtitle" style="color: var(--text-light); margin-bottom: 3rem;">Momentos inolvidables en el escenario.</p></div><div class="gallery-grid reveal"><div class="gallery-item"><img src="https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=500&auto=format&fit=crop&q=60" alt="Danza 1"><div class="gallery-overlay"></div></div><div class="gallery-item"><img src="https://images.unsplash.com/photo-1547153760-18fc86324498?w=500&auto=format&fit=crop&q=60" alt="Danza 2"><div class="gallery-overlay"></div></div><div class="gallery-item"><img src="https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500&auto=format&fit=crop&q=60" alt="Danza 3"><div class="gallery-overlay"></div></div><div class="gallery-item"><img src="https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=500&auto=format&fit=crop&q=60" alt="Danza 4"><div class="gallery-overlay"></div></div></div></section>
    <section id="agenda" class="section-dark section-padding"><div class="container" style="position: relative; z-index: 2;"><div class="agenda-header reveal"><h2>Próximas Presentaciones</h2></div><div class="calendar-grid" id="eventsContainer"><p style="color: #aaa;">Cargando cartelera...</p></div></div></section>
    <section id="ubicacion" class="container section-padding"><h2 class="text-center mb-2 reveal" style="font-size: 2.5rem;">Ensaya con Nosotros</h2><div class="grid-2" style="align-items: start;"><div class="map-box reveal"><iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3733.309536863266!2d-103.3957248!3d20.6572559!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMjDCsDM5JzI2LjEiTiAxMDPCsDIzJzQ0LjYiVw!5e0!3m2!1ses!2smx!4v1620000000000!5m2!1ses!2smx" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe></div><div class="schedule-box reveal"><h3 style="color: var(--azul-talavera); display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;"><span class="material-icons">schedule</span> Horarios de Clase</h3><ul class="schedule-list" style="list-style: none; padding: 0;"><li style="margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 1rem;"><span class="group-name" style="display: block; font-weight: bold; color: var(--rosa-oscuro);">Principiantes</span><span class="group-time" style="color: var(--text-light);">Lun y Mié: 4:00 PM - 6:00 PM</span></li><li style="margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 1rem;"><span class="group-name" style="display: block; font-weight: bold; color: var(--naranja-barro);">Intermedios</span><span class="group-time" style="color: var(--text-light);">Mar y Jue: 5:00 PM - 7:00 PM</span></li><li><span class="group-name" style="display: block; font-weight: bold; color: var(--verde-agave);">Compañía Titular</span><span class="group-time" style="color: var(--text-light);">Sábados: 9:00 AM - 2:00 PM</span></li></ul></div></div></section>
    <footer class="section-dark" style="padding: 4rem 0; text-align: center; margin-top: 4rem; border-top: 4px solid var(--amarillo-cempasuchil);"><div class="container"><h2 style="color: var(--amarillo-cempasuchil);">NAYAHUARI</h2><p style="opacity: 0.8; font-size: 1.1rem; margin-bottom: 2rem;">Orgullo, Tradición y Pasión.</p><div class="social-links" style="display: flex; justify-content: center; gap: 25px; margin-bottom: 2rem; position: relative; z-index: 10;"><a href="https://wa.me/5211234567890" target="_blank" rel="noopener noreferrer" class="social-btn whatsapp" title="Enviar WhatsApp"><i class="fab fa-whatsapp"></i></a><a href="https://www.facebook.com/balletnayahuari" target="_blank" rel="noopener noreferrer" class="social-btn facebook" title="Síguenos en Facebook"><i class="fab fa-facebook-f"></i></a><a href="https://www.instagram.com/balletnayahuari" target="_blank" rel="noopener noreferrer" class="social-btn instagram" title="Síguenos en Instagram"><i class="fab fa-instagram"></i></a><a href="https://www.tiktok.com/@balletnayahuari" target="_blank" rel="noopener noreferrer" class="social-btn tiktok" title="Síguenos en TikTok"><i class="fab fa-tiktok"></i></a><a href="https://www.youtube.com/@balletnayahuari" target="_blank" rel="noopener noreferrer" class="social-btn youtube" title="Suscríbete en YouTube"><i class="fab fa-youtube"></i></a></div><div style="padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.9rem; opacity: 0.5;"><p>Ballet Folklórico Nayahuari © 2026. Todos los derechos reservados.</p></div></div></footer>

    <!-- MODAL DUAL -->
    <div id="loginModal" class="modal">
      <div class="modal-content">
        <span class="close-btn" onclick="document.getElementById('loginModal').style.display='none'">&times;</span>
        <div class="login-header">
          <h2 style="color: var(--rosa-mexicano);" id="modalTitle">Bienvenido</h2>
          <p>Ingresa al portal</p>
        </div>
        
        <!-- LOGIN FORM -->
        <div id="loginSection">
            <form id="universalLoginForm" style="margin-top: 20px;">
              <div class="input-group"><span class="material-icons input-icon">person</span><input type="text" id="loginUser" placeholder="Usuario / Email" required></div>
              <div class="input-group"><span class="material-icons input-icon">lock</span><input type="password" id="loginPass" placeholder="Contraseña" required></div>
              <button type="submit" class="btn-primary full-width">Iniciar Sesión</button>
            </form>
            <p class="auth-toggle-text">¿No tienes cuenta? <span class="auth-toggle-link" onclick="toggleAuthMode('register')">Regístrate como Alumno</span></p>
        </div>

        <!-- REGISTER FORM -->
        <div id="registerSection" style="display:none;">
            <form id="publicRegisterForm" style="margin-top: 20px;">
                <div class="input-group"><span class="material-icons input-icon">badge</span><input type="text" id="regNombre" placeholder="Nombre Completo" required></div>
                <div class="input-group"><span class="material-icons input-icon">email</span><input type="email" id="regUser" placeholder="Correo (ej: usuario@gmail.com)" required></div>
                <div class="input-group"><span class="material-icons input-icon">phone</span><input type="text" id="regTel" placeholder="Teléfono"></div>
                <div class="input-group"><span class="material-icons input-icon">lock</span><input type="password" id="regPass" placeholder="Contraseña" required></div>
                <button type="submit" class="btn-success full-width">Crear Cuenta</button>
            </form>
            <p class="auth-toggle-text">¿Ya tienes cuenta? <span class="auth-toggle-link" onclick="toggleAuthMode('login')">Inicia Sesión</span></p>
        </div>
        
        <div id="loginMessage" class="login-message" style="margin-top:15px; font-weight:bold;"></div>
      </div>
    </div>

    <script src="{{ url_for('static', filename='js/main.js') }}?v=public_reg_final"></script>
    <script>function abrirLogin() { if (localStorage.getItem('usuario_logueado') === 'true') { window.location.href = '/dashboard'; } else { document.getElementById('loginModal').style.display = 'block'; toggleAuthMode('login'); } }</script>
</body>
</html>
"""

# ==========================================
# 5. HTML DASHBOARD (Incluye librerías QR)
# ==========================================
contenido_dashboard_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Gestión | Nayahuari</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}?v=23">
    
    <!-- LIBRERÍAS QR -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
</head>
<body>
    <div class="zarape-line"></div>
    <div class="dashboard-layout">
        <aside class="sidebar">
            <div class="logo" style="margin-bottom: 3rem; text-align: center;">
                <span style="font-size: 0.7rem; letter-spacing: 2px; color: var(--accent);">PANEL</span><br>
                <strong style="color: white; font-size: 1.5rem;">NAYAHUARI</strong>
            </div>
            
            <nav id="adminMenu" style="display: none;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 10px; font-weight: bold; padding-left: 15px;">ADMINISTRACIÓN</p>
                <a href="#" onclick="mostrarSeccion('usuarios')" id="nav-usuarios" class="menu-item active"><span class="material-icons">group</span> Usuarios / Alumnos</a>
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
            
            <div style="margin-top: auto;">
                <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 1rem 0;">
                <a href="/" class="menu-item"><span class="material-icons">public</span> Ver Web</a>
                <button onclick="cerrarSesion()" class="menu-item" style="width: 100%; background: none; border: none; cursor: pointer; color: #ef4444;"><span class="material-icons">logout</span> Cerrar Sesión</button>
            </div>
        </aside>
        
        <main class="main-content">
            <header class="header-bar animate-fade">
                <div><h1 id="pageTitle" style="color: var(--dark-bg);">Bienvenido</h1><p id="welcomeTitle" style="color: var(--text-light); font-size: 0.9rem;">Panel de Control</p></div>
                <div style="display: flex; align-items: center; gap: 10px; background: white; padding: 5px 15px; border-radius: 50px; box-shadow: var(--shadow);"><div style="background: var(--amarillo-cempasuchil); width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center;"><span class="material-icons" style="color: var(--azul-noche); font-size: 1.2rem;">person</span></div><div><span id="userNameDisplay" style="display: block; font-weight: bold; font-size: 0.9rem; color: var(--azul-noche);">Usuario</span><span id="userRoleDisplay" style="display: block; font-size: 0.7rem; color: var(--text-light);">Rol</span></div></div>
            </header>
            
            <div id="section-usuarios" class="admin-section animate-slide"><div class="card-table"><h3 style="margin-bottom: 1.5rem; color: var(--rosa-mexicano);">Gestión de Usuarios</h3><form id="formUsuario" class="form-grid-responsive"><input type="hidden" id="usuarioId"><div class="form-group-item"><label>Usuario</label><input type="text" id="usuarioUsername" class="form-control" required></div><div class="form-group-item"><label>Contraseña</label><input type="password" id="usuarioPassword" class="form-control"></div><div class="form-group-item"><label>Rol</label><select id="usuarioRol" class="form-control" onchange="toggleCamposAlumno()"><option value="alumno">Alumno</option><option value="maestro">Maestro</option><option value="administrativo">Administrativo</option><option value="admin">Administrador</option></select></div><div class="form-group-item campo-alumno"><label>Nombre</label><input type="text" id="usuarioNombre" class="form-control"></div><div class="form-group-item campo-alumno"><label>Teléfono</label><input type="text" id="usuarioTelefono" class="form-control"></div><div class="form-group-item campo-alumno"><label>Nivel</label><select id="usuarioNivel" class="form-control"><option value="Principiante">Principiante</option><option value="Intermedio">Intermedio</option><option value="Avanzado">Avanzado</option></select></div><div class="form-group-item btn-container"><button type="submit" class="btn-success" style="height: 48px; width: 100%;"><span class="material-icons">save</span> Guardar</button></div></form></div><div class="card-table"><table class="tabla-moderna"><thead><tr><th>Usuario / Nombre</th><th>Rol</th><th>Acciones</th></tr></thead><tbody id="tablaUsuarios"></tbody></table></div></div>
            
            <!-- OTROS SECCIONES ADMIN -->
            <div id="section-eventos" class="admin-section animate-slide" style="display:none;"><div class="card-table"><h3>Crear Evento</h3><form id="formEvento" class="form-grid-responsive"><div class="form-group-item"><input type="text" id="tituloEvento" class="form-control" placeholder="Título" required></div><div class="form-group-item"><input type="text" id="fechaEvento" class="form-control" placeholder="Fecha"></div><div class="form-group-item"><input type="text" id="lugarEvento" class="form-control" placeholder="Lugar"></div><div class="form-group-item"><input type="text" id="horaEvento" class="form-control" placeholder="Hora"></div><div class="btn-container"><button class="btn-success">Crear</button></div></form></div><div class="card-table"><table class="tabla-moderna"><tbody id="tablaEventos"></tbody></table></div></div>
            <div id="section-pagos" class="admin-section animate-slide" style="display:none;"><div class="card-table"><h3>Registrar Pago</h3><form id="formPago" class="form-grid-responsive"><div class="form-group-item"><select id="pagoUsuario" class="form-control" required></select></div><div class="form-group-item"><input type="text" id="pagoConcepto" class="form-control" placeholder="Concepto"></div><div class="form-group-item"><input type="number" id="pagoMonto" class="form-control" placeholder="Monto"></div><div class="btn-container"><button class="btn-success">Registrar</button></div></form></div><div class="card-table"><table class="tabla-moderna"><tbody id="tablaPagos"></tbody></table></div></div>
            <div id="section-vestuario" class="admin-section animate-slide" style="display:none;"><div class="card-table"><h3>Vestuario</h3><form id="formVestuario" class="form-grid-responsive"><div class="form-group-item"><input type="text" id="vestuarioNombre" class="form-control" placeholder="Nombre"></div><div class="form-group-item"><select id="vestuarioTipo" class="form-control"><option>Traje</option><option>Accesorio</option></select></div><div class="form-group-item"><input type="number" id="vestuarioCantidad" class="form-control" value="1"></div><div class="form-group-item"><input type="text" id="vestuarioTalla" class="form-control" placeholder="Talla"></div><div class="form-group-item"><select id="vestuarioEstado" class="form-control"><option>Bueno</option><option>Reparación</option></select></div><div class="btn-container"><button class="btn-success">Agregar</button></div></form></div><div class="card-table"><table class="tabla-moderna"><tbody id="tablaVestuario"></tbody></table></div></div>
            
            <!-- SECCIÓN ASISTENCIA ADMIN (Generador QR) -->
            <div id="section-asistencia" class="admin-section animate-slide" style="display:none;">
                <div class="card-table">
                    <h3 style="color:var(--primary); text-align:center; margin-bottom:20px;">Código QR para Asistencia</h3>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <input type="hidden" id="fechaAsistencia">
                        <div id="qrcode-container">
                            <div id="qrcode"></div>
                            <p id="qr-date-label" style="margin-top:10px; font-weight:bold; color:var(--dark-bg);"></p>
                        </div>
                        <button onclick="generarQR()" class="btn-success" style="margin-top:20px; font-size:1.1rem;">
                            <span class="material-icons">qr_code</span> Generar QR de Hoy
                        </button>
                    </div>
                </div>
            </div>

            <!-- SECCIONES ALUMNO -->
            <div id="section-alumno-asistencia" class="alumno-section animate-slide" style="display:none;">
                <div class="user-welcome-card" style="background: linear-gradient(135deg, var(--rosa-mexicano), var(--azul-talavera)); color: white; padding: 3rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;">
                    <h2 style="font-size: 2.5rem; margin-bottom: 10px;">¡Hola!</h2>
                    <p>Escanea el código QR del salón para marcar tu asistencia.</p>
                    
                    <div style="margin-top: 2rem; max-width: 400px; margin-left: auto; margin-right: auto;">
                        <div id="reader" style="display:none; width: 100%;"></div>
                        
                        <button onclick="iniciarEscaner()" id="btnEscanearQR" class="btn-success" style="font-size: 1.2rem; padding: 15px 40px; border: none; background: white; color: var(--azul-talavera); margin-top: 20px;">
                            <span class="material-icons" style="vertical-align: middle; margin-right: 10px;">photo_camera</span>
                            Escanear QR
                        </button>
                    </div>
                </div>
            </div>

            <div id="section-alumno-eventos" class="alumno-section animate-slide" style="display:none;">
                <h3 style="color: var(--dark-bg); margin-bottom: 1.5rem;">Agenda de Eventos</h3>
                <div id="alumnoEventosContainer" class="calendar-grid"></div>
            </div>
            <div id="section-alumno-vestuario" class="alumno-section animate-slide" style="display:none;">
                <h3 style="color: var(--dark-bg); margin-bottom: 1.5rem;">Inventario Disponible</h3>
                <div class="card-table"><div id="alumnoVestuarioContainer"></div></div>
            </div>

        </main>
    </div>
    <script src="{{ url_for('static', filename='js/main.js') }}?v=23"></script>
    <script>function toggleCamposAlumno() { const rol = document.getElementById('usuarioRol').value; const campos = document.querySelectorAll('.campo-alumno'); campos.forEach(c => c.style.display = (rol === 'alumno') ? 'block' : 'none'); } toggleCamposAlumno();</script>
</body>
</html>
"""

# Ejecución
print("🔧 Reparando estructura y unificando Usuarios...")
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

with open("app.py", "w", encoding="utf-8") as f: f.write(contenido_app_py)
with open("static/css/estilos.css", "w", encoding="utf-8") as f: f.write(contenido_css)
with open("static/js/main.js", "w", encoding="utf-8") as f: f.write(contenido_js)
with open("templates/dashboard.html", "w", encoding="utf-8") as f: f.write(contenido_dashboard_html)
with open("templates/index.html", "w", encoding="utf-8") as f: f.write(contenido_index_html)

print("✅ ¡REPARACIÓN COMPLETADA!")
print("1. Detén el servidor (Ctrl+C).")
print("2. IMPORTANTE: Borra 'database/mi_app.sqlite' (o la carpeta database) para aplicar la nueva estructura.")
print("3. Ejecuta 'python app.py'.")
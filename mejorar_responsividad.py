import os

print("🚀 RESTAURANDO ESTILOS Y LÓGICA VISUAL...")

# ==============================================================================
# CSS FINAL (Diseño Mexicano, Galería, Dashboard, Login)
# ==============================================================================
contenido_css = """
/* =========================================
   1. VARIABLES Y CONFIGURACIÓN GLOBAL
   ========================================= */
:root {
    /* Paleta Mexicana */
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
    
    /* Dimensiones y Efectos */
    --sidebar-width: 280px;
    --nav-height: 80px;
    --radius: 16px;
    --shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    --shadow-hover: 0 15px 30px -5px rgba(0, 0, 0, 0.15);
    --glass: rgba(8, 26, 73, 0.98);
}

* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
html, body { height: 100%; width: 100%; }
body { background-color: var(--bg-light); color: var(--text-main); line-height: 1.6; overflow-x: hidden; }
a { text-decoration: none; color: inherit; transition: 0.3s; }
ul { list-style: none; padding: 0; margin: 0; }
button { font-family: inherit; cursor: pointer; }
input, select, textarea { font-family: inherit; font-size: 16px; }

/* Decoración Superior (Zarape) */
.zarape-line {
    height: 6px;
    background: linear-gradient(to right, var(--rosa-mexicano), var(--azul-talavera), var(--amarillo-cempasuchil), var(--verde-agave), var(--naranja-barro));
    width: 100%; position: fixed; top: 0; left: 0; z-index: 3000;
}

/* Animaciones */
.reveal { opacity: 0; transform: translateY(40px); transition: all 0.8s cubic-bezier(0.5, 0, 0, 1); }
.reveal.active { opacity: 1; transform: translateY(0); }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade { animation: fadeIn 0.6s ease-out; }
.animate-slide { animation: slideUp 0.5s ease-out; }
.click-anim { animation: pulsacion 0.3s ease; }
@keyframes pulsacion { 0% { transform: scale(0.9); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }

/* =========================================
   2. NAVBAR & HEADER (Index)
   ========================================= */
.navbar {
    background: var(--glass);
    height: var(--nav-height);
    padding: 0 5%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 2000;
    margin-top: 6px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.logo-container { display: flex; align-items: center; gap: 15px; }
.logo-img { height: 50px; width: auto; object-fit: contain; }
.logo-text { display: flex; flex-direction: column; line-height: 1.2; color: white; text-align: left; }
.logo-text span { font-size: 0.7rem; letter-spacing: 2px; color: rgba(255,255,255,0.8); text-transform: uppercase; }
.logo-text strong { font-size: 1.4rem; color: var(--accent); letter-spacing: 1px; }

.nav-links { display: flex; gap: 25px; align-items: center; margin: 0; padding: 0; }
.nav-links a { color: white; font-weight: 500; font-size: 0.95rem; position: relative; }
.nav-links a:not(.btn):hover { color: var(--accent); }

.btn-login {
    background: transparent; border: 2px solid var(--accent); color: var(--accent);
    padding: 8px 24px; border-radius: 50px; font-weight: 700; display: flex; align-items: center; gap: 8px;
    transition: 0.3s; white-space: nowrap;
}
.btn-login:hover { background: var(--accent); color: var(--bg-dark); transform: translateY(-2px); }
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
.hero h1 { font-size: 4.5rem; margin-bottom: 1rem; line-height: 1.1; text-shadow: 2px 2px 0 var(--rosa-mexicano); }
.hero h3 { font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 1.5rem; color: var(--accent); font-weight: 600; }

/* Botones RGB / Gradiente */
.btn-primary {
    background-image: linear-gradient(45deg, var(--rosa-mexicano), #ff0080);
    background-size: 200% auto; color: white; padding: 12px 30px;
    border-radius: 50px; border: none; font-weight: 700; cursor: pointer;
    box-shadow: 0 10px 20px rgba(230, 0, 126, 0.4); text-transform: uppercase; letter-spacing: 1px;
    transition: 0.5s; display: inline-flex; align-items: center; justify-content: center; gap: 8px;
    text-decoration: none;
}
.btn-primary:hover { background-position: right center; transform: translateY(-3px); color: white; }

.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.section-padding { padding: 6rem 0; }
.text-center { text-align: center; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; }

/* Directora */
.director-frame { position: relative; padding: 15px; border: 2px dashed var(--primary); border-radius: var(--radius); transform: rotate(2deg); transition: 0.3s; margin: 20px; }
.director-frame:hover { transform: rotate(0deg); }
.director-img { height: 500px; width: 100%; border-radius: var(--radius); background: #e2e8f0 url('../img/directora.jpeg') center/cover; box-shadow: -15px 15px 0 var(--bg-dark); transform: rotate(-2deg); border: 4px solid white; }
.floating-badge { position: absolute; bottom: 40px; left: -20px; background: var(--accent); color: var(--bg-dark); padding: 10px 25px; border-radius: 50px; font-weight: 800; text-transform: uppercase; box-shadow: var(--shadow-lg); z-index: 10; }
.subtitle-badge { background: rgba(230, 0, 126, 0.1); color: var(--primary); padding: 6px 16px; border-radius: 50px; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 1rem; display: inline-block; }
.director-quote { border-left: 4px solid var(--accent); padding-left: 20px; margin-top: 2rem; font-style: italic; color: var(--text-main); font-size: 1.1rem; }

/* Timeline */
.section-gray { background-color: #F8FAFC; }
.timeline { position: relative; max-width: 900px; margin: 0 auto; padding: 40px 0; }
.timeline::after { content: ''; position: absolute; width: 4px; background: linear-gradient(to bottom, var(--primary), var(--secondary)); top: 0; bottom: 0; left: 50%; margin-left: -2px; border-radius: 2px; }
.timeline-item { padding: 10px 40px; position: relative; width: 50%; box-sizing: border-box; }
.timeline-item.left { left: 0; text-align: right; }
.timeline-item.right { left: 50%; text-align: left; }
.timeline-icon { position: absolute; width: 40px; height: 40px; top: 15px; z-index: 10; background: white; border-radius: 50%; border: 3px solid var(--primary); display: flex; align-items: center; justify-content: center; color: var(--primary); box-shadow: 0 0 0 4px rgba(255,255,255,0.8); }
.timeline-item.left .timeline-icon { right: -20px; left: auto; }
.timeline-item.right .timeline-icon { left: -20px; border-color: var(--secondary); color: var(--secondary); }
.timeline-content { padding: 25px; background: white; border-radius: 12px; box-shadow: var(--shadow); border-top: 4px solid var(--naranja-barro); }
.timeline-content:hover { transform: translateY(-5px); box-shadow: var(--shadow-hover); }
.year-badge { background: var(--bg-dark); color: var(--accent); padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; }

/* Galería */
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
.gallery-item { height: 300px; border-radius: var(--radius); overflow: hidden; position: relative; box-shadow: var(--shadow); cursor: pointer; }
.gallery-item img { width: 100%; height: 100%; object-fit: cover; transition: 0.5s; }
.gallery-item:hover img { transform: scale(1.1); }
.gallery-overlay { position: absolute; bottom: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.3); opacity: 0; transition: 0.3s; display: flex; align-items: center; justify-content: center; }
.gallery-item:hover .gallery-overlay { opacity: 1; }

/* Agenda */
.section-dark { background-color: var(--bg-dark); color: white; position: relative; }
.calendar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
.event-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--radius); padding: 25px; display: flex; align-items: center; gap: 20px; transition: 0.3s; }
.event-card:hover { border-color: var(--primary); background: rgba(255,255,255,0.1); }
.event-card .date { background: var(--accent); color: var(--bg-dark); padding: 10px; border-radius: 12px; text-align: center; min-width: 75px; font-weight: 800; display: flex; flex-direction: column; justify-content: center; height: 75px; overflow: hidden; }
.date .day { font-size: 1.8rem; line-height: 1; } .date .month { font-size: 0.8rem; text-transform: uppercase; }

/* Ubicación */
.map-box { height: 450px; border-radius: var(--radius); overflow: hidden; border: 4px solid white; box-shadow: var(--shadow-lg); }
.schedule-box { background: white; padding: 2.5rem; border-radius: var(--radius); box-shadow: var(--shadow-lg); border-top: 6px solid var(--primary); }
.group-name { font-size: 1.1rem; font-weight: bold; color: var(--secondary); display: block; margin-bottom: 5px; }

/* Footer */
footer { padding: 4rem 0; text-align: center; border-top: 4px solid var(--accent); margin-top: 0; }
.social-links { display: flex; justify-content: center; gap: 20px; margin: 2rem 0; flex-wrap: wrap; }
.social-btn { width: 50px; height: 50px; border-radius: 50%; background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; transition: 0.3s; position: relative; z-index: 10; border: 2px solid transparent; }
.social-btn:hover { background: white; transform: translateY(-5px); box-shadow: 0 5px 15px rgba(255,255,255,0.2); }
.social-btn.whatsapp:hover { color: #25D366; } .social-btn.facebook:hover { color: #1877F2; } .social-btn.instagram:hover { color: #E4405F; } .social-btn.youtube:hover { color: #FF0000; } .social-btn.tiktok:hover { color: #000000; background: linear-gradient(45deg, #00f2ea, #ff0050); color: white; border: none; }

/* =========================================
   4. DASHBOARD & LOGIN
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
.auth-toggle-link { color: var(--primary); font-weight: bold; cursor: pointer; }

/* Dashboard Layout */
.dashboard-layout { display: flex; min-height: 100vh; background-color: var(--bg-light); padding-top: 6px; }

.sidebar {
    width: var(--sidebar-width); background: var(--bg-dark); color: white;
    padding: 2rem; display: flex; flex-direction: column;
    position: fixed; top: 6px; left: 0; height: calc(100vh - 6px);
    overflow-y: auto; z-index: 100;
    box-shadow: 4px 0 15px rgba(0,0,0,0.1);
}
.sidebar .logo { margin-bottom: 3rem; text-align: center; }

.main-content {
    margin-left: var(--sidebar-width); width: calc(100% - var(--sidebar-width));
    padding: 3rem 4rem; overflow-y: auto; min-height: calc(100vh - 6px);
}

.menu-item { padding: 12px 15px; margin-bottom: 8px; border-radius: 10px; color: #cbd5e1; display: flex; gap: 10px; cursor: pointer; transition: 0.2s; align-items: center; }
.menu-item:hover { background: rgba(255,255,255,0.1); color: white; transform: translateX(5px); }
.menu-item.active { background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(230,0,126,0.3); }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin-bottom: 3rem; }
.stat-card { background: white; padding: 2rem; border-radius: 12px; display: flex; align-items: center; gap: 20px; box-shadow: var(--shadow-sm); border-left: 5px solid var(--primary); }
.stat-icon { width: 64px; height: 64px; border-radius: 50%; background: #fdf2f8; color: var(--primary); display: flex; justify-content: center; align-items: center; font-size: 2rem; }

.card-table { background: white; padding: 3rem; border-radius: 12px; box-shadow: var(--shadow-sm); margin-bottom: 3rem; overflow: visible; }
.form-grid-responsive { display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; align-items: end; }
.form-group-item { width: 100%; } .form-group-item.btn-container { grid-column: span 1; }
.form-group-item label { display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-light); }
.form-control { width: 100%; height: 48px; padding: 10px 15px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; background: #fff; transition: 0.3s; }
.form-control:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(230,0,126,0.1); }

.btn-success {
    height: 48px; padding: 0 30px;
    background-image: linear-gradient(45deg, #00695C, #10b981);
    background-size: 200% auto; color: white; border: none; border-radius: 8px;
    font-weight: 700; cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center; gap: 10px;
    transition: 0.5s; min-width: 140px;
}
.btn-success:hover { background-position: right center; transform: translateY(-2px); }

/* QR */
#qrcode-container { background: white; padding: 20px; border-radius: 20px; display: inline-block; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px 0; border: 2px dashed var(--secondary); }
#reader { width: 100%; max-width: 400px; margin: 0 auto; border-radius: 16px; overflow: hidden; border: 4px solid white; box-shadow: var(--shadow-lg); }

/* Botón Móvil Dashboard */
.dashboard-menu-btn { display: none; position: fixed; top: 15px; left: 15px; z-index: 2000; background: var(--primary); color: white; width: 45px; height: 45px; border-radius: 50%; border: none; align-items: center; justify-content: center; box-shadow: var(--shadow-lg); cursor: pointer; }
.sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1050; backdrop-filter: blur(2px); }

/* =========================================
   6. RESPONSIVIDAD (MÓVIL TOTAL)
   ========================================= */
@media (max-width: 968px) {
    /* Navbar */
    .navbar { padding: 1rem; }
    .nav-links { display: none; width: 100%; flex-direction: column; background: var(--bg-dark); position: absolute; top: 100%; left: 0; padding: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.5); gap: 15px; }
    .nav-links.active { display: flex; animation: fadeIn 0.3s; }
    .menu-toggle { display: block; color: white; font-size: 2rem; cursor: pointer; }
    
    /* Landing */
    .hero h1 { font-size: 3rem; }
    .grid-2 { grid-template-columns: 1fr; gap: 40px; }
    .section-padding { padding: 4rem 0; }
    .gallery-grid { grid-template-columns: 1fr; }
    .timeline::after { left: 20px; margin-left: 0; }
    .timeline-item { width: 100%; padding-left: 60px; padding-right: 0; text-align: left; }
    .timeline-item.right { left: 0; }
    .timeline-icon { left: 0; }
    .timeline-item.left .timeline-icon, .timeline-item.right .timeline-icon { left: -4px; right: auto; }
    
    /* Dashboard Mobile */
    .sidebar { transform: translateX(-100%); width: 280px; z-index: 2000; box-shadow: none; position: fixed; }
    .sidebar.active { transform: translateX(0); box-shadow: 4px 0 20px rgba(0,0,0,0.3); }
    .sidebar-overlay.active { display: block; }
    .dashboard-menu-btn { display: flex; }
    .main-content { margin-left: 0; width: 100%; padding: 5rem 1.5rem 2rem; }
    .stats-grid { grid-template-columns: 1fr; }
    .form-grid-responsive { grid-template-columns: 1fr; gap: 15px; }
    .card-table { padding: 1.5rem; }
    .btn-login { width: 100%; justify-content: center; }
}
"""

# ==============================================================================
# 2. JS (Lógica Completa)
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
    
    // Login Logic
    const loginForm = document.getElementById('universalLoginForm');
    if(loginForm) configurarModalLogin();
});

function configurarModalLogin() { 
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
                    window.location.href = '/dashboard';
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
    if (!usuarioLogueado) { window.location.href = '/login'; return; }
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
function cargarTodoAdmin() { cargarUsuariosAdmin(); cargarEventosAdmin(); cargarPagosAdmin(); cargarVestuarioAdmin(); const hoy=new Date().toISOString().split('T')[0]; if(document.getElementById('fechaAsistencia'))document.getElementById('fechaAsistencia').value=hoy; bindForm('formUsuario', agregarUsuario); bindForm('formEvento', agregarEvento); bindForm('formPago', agregarPago); bindForm('formVestuario', agregarVestuario); }
window.mostrarSeccion = function(s) {
    document.querySelectorAll('.admin-section, .alumno-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
    const t = document.getElementById(`section-${s}`);
    const n = document.getElementById(`nav-${s}`);
    if(t) { t.style.display = 'block'; setTimeout(() => t.classList.add('active'), 10); }
    if(n) n.classList.add('active');
}

async function cargarUsuariosAdmin() { const r=await fetch(`${API_URL}/usuarios`); const d=await r.json(); const t=document.getElementById('tablaUsuarios'); const s=document.getElementById('pagoUsuario'); if(s){ s.innerHTML='<option value="">Seleccionar...</option>'; d.filter(u=>u.rol==='alumno').forEach(u=>s.innerHTML+=`<option value="${u.id}">${u.nombre||u.username}</option>`);} if(t) t.innerHTML=d.map(u=>`<tr><td><strong>${u.username}</strong></td><td>${u.rol}</td><td style="text-align:right"><button onclick="borrarUsuario(${u.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarUsuario(e) { e.preventDefault(); const d={username:document.getElementById('usuarioUsername').value, rol:document.getElementById('usuarioRol').value, nombre:document.getElementById('usuarioNombre').value, telefono:document.getElementById('usuarioTelefono').value, password:document.getElementById('usuarioPassword').value}; await fetch(`${API_URL}/usuarios`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}); document.getElementById('formUsuario').reset(); cargarUsuariosAdmin(); }
window.borrarUsuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); cargarUsuariosAdmin(); }};

async function cargarPagosAdmin() { const r=await fetch(`${API_URL}/pagos`); const d=await r.json(); const t=document.getElementById('tablaPagos'); if(t) t.innerHTML=d.map(p=>`<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarPago(e) { e.preventDefault(); await genericPost(`${API_URL}/pagos`, { usuario_id: document.getElementById('pagoUsuario').value, concepto: document.getElementById('pagoConcepto').value, monto: document.getElementById('pagoMonto').value }); document.getElementById('formPago').reset(); cargarPagosAdmin(); }
window.borrarPago=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/pagos/${id}`, {method:'DELETE'}); cargarPagosAdmin(); }};
async function cargarEventosAdmin() { const res = await fetch(`${API_URL}/eventos`); const data = await res.json(); const tbody = document.getElementById('tablaEventos'); if(tbody) tbody.innerHTML = data.map(ev => `<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarEvento(e) { e.preventDefault(); await genericPost(`${API_URL}/eventos`, { titulo: document.getElementById('tituloEvento').value, fecha: document.getElementById('fechaEvento').value, lugar: document.getElementById('lugarEvento').value, hora: document.getElementById('horaEvento').value }); document.getElementById('formEvento').reset(); cargarEventosAdmin(); }
window.borrarEvento=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/eventos/${id}`, {method:'DELETE'}); cargarEventosAdmin(); }};
async function cargarVestuarioAdmin() { const res = await fetch(`${API_URL}/vestuario`); const data = await res.json(); const tbody = document.getElementById('tablaVestuario'); if(tbody) tbody.innerHTML = data.map(v => `<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete">x</button></td></tr>`).join(''); }
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
    document.getElementById('qr-date-label').textContent = `Código: ${hoy}`;
}

let html5QrcodeScanner = null;
window.iniciarEscaner = function() {
    document.getElementById('reader').style.display = "block";
    if (html5QrcodeScanner) html5QrcodeScanner.clear();
    html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(async (decodedText) => {
        html5QrcodeScanner.clear();
        document.getElementById('reader').style.display = "none";
        try {
            const res = await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ qr_data: decodedText, id_usuario: usuarioId }) });
            const data = await res.json();
            alert(data.success ? `✅ ${data.mensaje}` : `❌ ${data.mensaje}`);
        } catch(e) { alert("Error de conexión"); }
    });
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
        c.innerHTML = data.length ? data.map(ev => `<div class="event-card reveal"><div class="date"><span class="day">${ev.fecha.split(' ')[0]}</span></div><div class="details"><h4>${ev.titulo}</h4><p>${ev.lugar}</p></div></div>`).join('') : '<p>Próximamente</p>';
    } catch(e){}
}
window.cerrarSesion = function() { if(confirm("¿Cerrar sesión?")) { localStorage.clear(); window.location.href='/'; } };
"""

# Ejecución
with open("static/css/estilos.css", "w", encoding="utf-8") as f:
    f.write(contenido_css)
with open("static/js/main.js", "w", encoding="utf-8") as f:
    f.write(contenido_js)

print("✅ ESTILOS Y LÓGICA RESTAURADOS.")
print("1. Recarga la página (Ctrl+F5).")
print("2. El index tendrá su diseño original y el dashboard será funcional.")
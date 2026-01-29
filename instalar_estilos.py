import os

# 1. Definimos el contenido del CSS y JS
contenido_css = """
/* =========================================
   VARIABLES Y RESET
   ========================================= */
:root {
    --primary: #2563eb;
    --primary-dark: #1e40af;
    --gold: #FBCA03;
    --gold-dark: #e0b500;
    --dark-bg: #1e293b;
    --light-bg: #f8fafc;
    --text-main: #334155;
    --text-light: #94a3b8;
    --white: #ffffff;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
body { background-color: var(--light-bg); color: var(--text-main); line-height: 1.6; }
a { text-decoration: none; color: inherit; }
ul { list-style: none; }

/* =========================================
   NAVBAR
   ========================================= */
.navbar {
    background: var(--dark-bg);
    color: var(--white);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: var(--shadow);
}
.logo span { display: block; font-size: 0.8rem; letter-spacing: 2px; }
.logo strong { font-size: 1.5rem; color: var(--gold); }

.nav-links { display: flex; gap: 20px; align-items: center; }
.nav-links a:hover { color: var(--gold); }

.btn-login {
    background: transparent;
    border: 1px solid var(--white);
    color: var(--white);
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    display: flex; align-items: center; gap: 5px;
}
.btn-login:hover { background: rgba(255,255,255,0.1); }

/* Botón Panel Admin (Dorado) */
.btn-panel-admin {
    background-color: var(--gold) !important;
    color: black !important;
    font-weight: bold;
    border: none;
    padding: 8px 15px;
    border-radius: 5px;
    display: inline-flex; align-items: center; gap: 5px;
}
.btn-panel-admin:hover { background-color: var(--gold-dark) !important; }

/* =========================================
   HERO & SECTIONS
   ========================================= */
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.section-padding { padding: 4rem 0; }
.text-center { text-align: center; }
.mb-2 { margin-bottom: 2rem; }

.hero {
    height: 80vh;
    background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&q=80');
    background-size: cover;
    background-position: center;
    display: flex; align-items: center; justify-content: center;
    text-align: center; color: white;
}
.hero h1 { font-size: 4rem; color: var(--gold); margin: 10px 0; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center; }
.placeholder-img {
    background: #ddd; height: 300px; display: flex;
    flex-direction: column; align-items: center; justify-content: center;
    border-radius: 10px;
}

/* =========================================
   TIMELINE (Trayectoria)
   ========================================= */
.section-gray { background-color: #e2e8f0; }
.timeline { position: relative; max-width: 800px; margin: 0 auto; }
.timeline::after {
    content: ''; position: absolute; width: 4px; background-color: var(--primary);
    top: 0; bottom: 0; left: 50%; margin-left: -2px;
}
.timeline-item { padding: 10px 40px; position: relative; width: 50%; }
.timeline-item.left { left: 0; text-align: right; }
.timeline-item.right { left: 50%; }
.timeline-content {
    padding: 20px; background: white; border-radius: 6px; box-shadow: var(--shadow);
}
.year { font-weight: bold; color: var(--primary); display: block; margin-bottom: 5px; }

/* =========================================
   AGENDA (Eventos)
   ========================================= */
.section-dark { background-color: var(--dark-bg); color: white; }
.agenda-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }

.calendar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.event-card {
    background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px;
    display: flex; align-items: center; gap: 15px; position: relative;
}
.event-card .date {
    background: var(--gold); color: black; padding: 10px; border-radius: 5px;
    text-align: center; min-width: 70px;
}
.date .day { display: block; font-size: 1.5rem; font-weight: bold; line-height: 1; }
.date .month { font-size: 0.8rem; text-transform: uppercase; }

.btn-admin-add {
    background: var(--gold); border: none; padding: 8px 15px; border-radius: 5px;
    cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 5px;
}
.btn-delete-event {
    position: absolute; top: 10px; right: 10px;
    background: #ef4444; color: white; border: none; border-radius: 50%;
    width: 30px; height: 30px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}

/* =========================================
   MODAL LOGIN
   ========================================= */
.modal {
    display: none; position: fixed; z-index: 2000; left: 0; top: 0;
    width: 100%; height: 100%; background-color: rgba(0,0,0,0.6);
}
.modal-content {
    background-color: white; margin: 10% auto; padding: 2rem;
    width: 90%; max-width: 400px; border-radius: 10px; position: relative;
}
.close-btn { position: absolute; right: 20px; top: 10px; font-size: 2rem; cursor: pointer; }

.input-group { position: relative; margin-bottom: 15px; }
.input-icon { position: absolute; left: 10px; top: 10px; color: #aaa; }
.input-group input {
    width: 100%; padding: 10px 10px 10px 40px;
    border: 1px solid #ccc; border-radius: 5px;
}
.btn-primary.full-width { width: 100%; background-color: var(--primary); color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-size: 1rem; }
.btn-primary.full-width:hover { background-color: var(--primary-dark); }

/* =========================================
   DASHBOARD UTILS
   ========================================= */
.dashboard-layout { display: flex; min-height: 100vh; }
.sidebar { width: 250px; background: var(--dark-bg); color: white; padding: 2rem; }
.main-content { flex: 1; padding: 2rem; }
.tabla-moderna { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: var(--shadow); }
.tabla-moderna th, .tabla-moderna td { padding: 1rem; text-align: left; border-bottom: 1px solid #eee; }
.badge { padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; color: white; }
.badge-principiante { background: #10b981; }
.badge-intermedio { background: #f59e0b; }
.badge-avanzado { background: #6366f1; }
.btn-danger-sm { color: #ef4444; border: 1px solid #ef4444; background: none; padding: 2px 8px; border-radius: 4px; cursor: pointer; }
.btn-danger-sm:hover { background: #ef4444; color: white; }

/* Responsive Timeline */
@media (max-width: 768px) {
    .timeline::after { left: 31px; }
    .timeline-item { width: 100%; padding-left: 70px; padding-right: 25px; }
    .timeline-item.left, .timeline-item.right { left: 0; text-align: left; }
    .nav-links { display: none; } /* En móvil necesitaría JS para el toggle */
    .menu-toggle { display: block; cursor: pointer; }
    .grid-2 { grid-template-columns: 1fr; }
}
@media (min-width: 769px) { .menu-toggle { display: none; } }
"""

contenido_js = """
/* ======================================================
   MAIN.JS - Controla Landing, Login, Agenda y Dashboard
   ====================================================== */

const API_URL = '/api';

// Variables de estado global
let esAdmin = localStorage.getItem('es_admin') === 'true';
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre');

document.addEventListener('DOMContentLoaded', () => {
    actualizarInterfaz();
    
    // Si estamos en la Landing Page (tiene sección de eventos)
    if (document.getElementById('eventsContainer')) {
        cargarEventosLanding();
        configurarModalLogin();
    }

    // Si estamos en el Dashboard (tiene tabla de bailarines)
    if (document.getElementById('tablaBailarines')) {
        verificarAccesoDashboard();
        cargarBailarines();
        
        // Listener para agregar bailarín
        const formBailarin = document.getElementById('formBailarin');
        if(formBailarin) formBailarin.addEventListener('submit', agregarBailarin);
    }
});

// ==========================================
// 1. GESTIÓN DE INTERFAZ Y SESIÓN
// ==========================================

function actualizarInterfaz() {
    // Elementos de la Landing Page
    const btnPanel = document.getElementById('nav-admin-panel');
    const btnAdd = document.getElementById('btnAddEvent'); // Botón flotante de agenda
    const btnAuth = document.getElementById('btnAuth'); // Botón del menú

    // Si el usuario es ADMIN
    if (esAdmin) {
        if(btnPanel) btnPanel.style.display = 'block';
        if(btnAdd) btnAdd.style.display = 'flex';
        
        if(btnAuth) {
            btnAuth.innerHTML = '<span class="material-icons">logout</span> Salir';
            btnAuth.onclick = cerrarSesion;
        }
    } 
    // Si es USUARIO NORMAL
    else if (usuarioLogueado) {
        if(btnPanel) btnPanel.style.display = 'none';
        if(btnAdd) btnAdd.style.display = 'none';
        
        if(btnAuth) {
            btnAuth.innerHTML = '<span class="material-icons">logout</span> Salir';
            btnAuth.onclick = cerrarSesion;
        }
    } 
    // Si es INVITADO (Nadie logueado)
    else {
        if(btnPanel) btnPanel.style.display = 'none';
        if(btnAdd) btnAdd.style.display = 'none';
        
        if(btnAuth) {
            btnAuth.innerHTML = '<span class="material-icons">account_circle</span> Acceso';
            btnAuth.onclick = abrirModalLogin;
        }
    }
}

function cerrarSesion() {
    if(confirm("¿Deseas cerrar sesión?")) {
        localStorage.removeItem('es_admin');
        localStorage.removeItem('usuario_logueado');
        localStorage.removeItem('usuario_nombre');
        window.location.href = '/'; // Redirigir a inicio al salir
    }
}

// ==========================================
// 2. LÓGICA DE LA LANDING PAGE (Eventos y Modal)
// ==========================================

function configurarModalLogin() {
    const modal = document.getElementById("loginModal");
    const closeBtn = document.querySelector(".close-btn");
    const loginForm = document.getElementById('universalLoginForm');

    if(closeBtn) closeBtn.onclick = () => modal.style.display = "none";
    window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; };

    if(loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const usuario = document.getElementById('loginUser').value;
            const pass = document.getElementById('loginPass').value;
            const msgDiv = document.getElementById('loginMessage');

            try {
                const res = await fetch(`${API_URL}/login`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ usuario, password: pass })
                });
                const data = await res.json();

                if(data.success) {
                    msgDiv.style.color = 'green';
                    msgDiv.textContent = "¡Bienvenido!";
                    
                    // Guardar sesión
                    localStorage.setItem('usuario_logueado', 'true');
                    localStorage.setItem('es_admin', data.es_admin);
                    localStorage.setItem('usuario_nombre', usuario);

                    setTimeout(() => {
                        window.location.reload(); // Recargar para actualizar UI
                    }, 1000);
                } else {
                    msgDiv.style.color = 'red';
                    msgDiv.textContent = data.mensaje;
                }
            } catch (error) {
                console.error(error);
                msgDiv.style.color = 'red';
                msgDiv.textContent = "Error de conexión";
            }
        });
    }

    // Agregar evento nuevo (Solo Admin Landing)
    const btnAddEvent = document.getElementById('btnAddEvent');
    if (btnAddEvent) {
        btnAddEvent.onclick = async () => {
            const titulo = prompt("Título del Evento:");
            if (!titulo) return;
            const fecha = prompt("Fecha (ej: 20 SEP):");
            
            try {
                await fetch(`${API_URL}/eventos`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ titulo, fecha })
                });
                cargarEventosLanding();
            } catch(e) { console.error(e); }
        };
    }
}

async function cargarEventosLanding() {
    const container = document.getElementById('eventsContainer');
    if(!container) return;

    try {
        const res = await fetch(`${API_URL}/eventos`);
        const eventos = await res.json();

        container.innerHTML = '';
        if (eventos.length === 0) {
            container.innerHTML = '<p style="color:#aaa">No hay eventos próximos.</p>';
            return;
        }

        eventos.forEach(ev => {
            const card = document.createElement('div');
            card.className = 'event-card';
            
            let btnBorrar = '';
            if (esAdmin) {
                btnBorrar = `<button class="btn-delete-event" onclick="borrarEvento(${ev.id})">
                                <span class="material-icons">delete</span>
                             </button>`;
            }

            // Parsear fecha simple (si viene "20 SEP")
            const partesFecha = ev.fecha.split(' ');
            const dia = partesFecha[0] || '';
            const mes = partesFecha[1] || '';

            card.innerHTML = `
                <div class="date">
                    <span class="day">${dia}</span>
                    <span class="month">${mes}</span>
                </div>
                <div class="details">
                    <h4>${ev.titulo}</h4>
                    <p><span class="material-icons">place</span> ${ev.lugar || 'Por definir'}</p>
                    <p><span class="material-icons">schedule</span> ${ev.hora || 'Por definir'}</p>
                </div>
                ${btnBorrar}
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error(error);
        container.innerHTML = '<p>Error cargando eventos.</p>';
    }
}

window.abrirModalLogin = function() {
    document.getElementById("loginModal").style.display = "block";
};

window.borrarEvento = async (id) => {
    if(!confirm("¿Borrar evento?")) return;
    await fetch(`${API_URL}/eventos/${id}`, { method: 'DELETE' });
    cargarEventosLanding();
};


// ==========================================
// 3. LÓGICA DEL DASHBOARD (Bailarines)
// ==========================================

function verificarAccesoDashboard() {
    if (!esAdmin) {
        alert("Acceso restringido. Solo administradores.");
        window.location.href = '/';
    }
}

async function cargarBailarines() {
    try {
        const res = await fetch(`${API_URL}/bailarines`);
        const data = await res.json();
        const tbody = document.getElementById('tablaBailarines');
        tbody.innerHTML = '';

        data.forEach(b => {
            tbody.innerHTML += `
                <tr>
                    <td><strong>${b.nombre}</strong></td>
                    <td><span class="badge badge-${b.nivel ? b.nivel.toLowerCase() : 'default'}">${b.nivel || 'N/A'}</span></td>
                    <td>${b.contacto || '<span style="color:#ccc">--</span>'}</td>
                    <td>
                        <button onclick="borrarBailarin(${b.id})" class="btn-danger-sm">
                           <span class="material-icons" style="font-size:1rem; vertical-align:middle;">delete</span> Eliminar
                        </button>
                    </td>
                </tr>`;
        });
    } catch (e) { console.error(e); }
}

async function agregarBailarin(e) {
    e.preventDefault();
    const nombre = document.getElementById('nombreBailarin').value;
    const nivel = document.getElementById('nivelBailarin').value;
    // NUEVO: Capturamos el contacto que faltaba
    const contacto = document.getElementById('contactoBailarin').value;

    await fetch(`${API_URL}/bailarines`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ nombre, nivel, contacto }) // Se envía también el contacto
    });
    
    document.getElementById('formBailarin').reset();
    cargarBailarines();
}

window.borrarBailarin = async (id) => {
    if(!confirm("¿Eliminar bailarín?")) return;
    await fetch(`${API_URL}/bailarines/${id}`, { method: 'DELETE' });
    cargarBailarines();
};
"""

# 2. Creamos las carpetas si no existen
print("📂 Creando carpetas necesarias...")
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# 3. Escribimos los archivos
print("📝 Escribiendo estilos.css...")
with open("static/css/estilos.css", "w", encoding="utf-8") as f:
    f.write(contenido_css)

print("📝 Escribiendo main.js...")
with open("static/js/main.js", "w", encoding="utf-8") as f:
    f.write(contenido_js)

print("\n✨ ¡LISTO! Estructura creada con éxito:")
print("   - static/css/estilos.css")
print("   - static/js/main.js")
print("\n👉 Ahora recarga tu página web (Ctrl + F5).")
import os

print("🚀 REPARANDO LÓGICA COMPLETA (QR + REGISTRO + ALERTAS)...")

contenido_js = """
const API_URL = '/api';
let usuarioRol = localStorage.getItem('usuario_rol');
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre') || 'Invitado';
let usuarioId = localStorage.getItem('usuario_id');

// ==========================================
// 1. SISTEMA DE ALERTAS (Personalizadas)
// ==========================================
function showToast(message, type = 'success') {
    // Eliminar toasts previos para no encimar
    const existing = document.querySelector('.custom-toast');
    if (existing) existing.remove();

    const div = document.createElement('div');
    div.className = `custom-toast ${type}`;
    // Estilos inyectados para asegurar visibilidad
    div.style.cssText = "position: fixed; top: 20px; right: 20px; background: white; padding: 15px 25px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); z-index: 11000; border-left: 5px solid " + (type === 'success' ? '#00695C' : '#ef4444') + "; animation: slideInRight 0.4s ease-out; display: flex; align-items: center;";
    
    const icon = type === 'success' ? 'check_circle' : 'error';
    const color = type === 'success' ? '#00695C' : '#ef4444';
    
    div.innerHTML = `<span class="material-icons" style="color:${color}; margin-right: 10px;">${icon}</span> <div style="font-weight: 500; color: #333;">${message}</div>`;
    document.body.appendChild(div);
    
    setTimeout(() => { 
        div.style.transition = "opacity 0.5s, transform 0.5s";
        div.style.opacity = "0";
        div.style.transform = "translateX(100%)";
        setTimeout(() => div.remove(), 500);
    }, 3500);
}

function showConfirm(message, onYes) {
    // Eliminar overlays previos
    const existing = document.querySelector('.custom-confirm-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.className = 'custom-confirm-overlay';
    overlay.style.cssText = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(8, 26, 73, 0.8); z-index: 12000; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(4px); animation: fadeIn 0.2s;";
    
    overlay.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 20px; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.3); animation: scaleUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);">
            <span class="material-icons" style="font-size: 3rem; color: #E6007E; margin-bottom: 10px;">help_outline</span>
            <h3 style="margin: 0; color: #081a49;">Confirmación</h3>
            <p style="color: #64748b; margin-top: 10px; margin-bottom: 25px;">${message}</p>
            <div style="display: flex; justify-content: center; gap: 15px;">
                <button id="btnNo" style="background: #f1f5f9; color: #64748b; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-weight: bold;">Cancelar</button>
                <button id="btnYes" style="background: #E6007E; color: white; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-weight: bold;">Sí, continuar</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    
    document.getElementById('btnNo').onclick = () => overlay.remove();
    document.getElementById('btnYes').onclick = () => { overlay.remove(); onYes(); };
}

// ==========================================
// 2. INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Menú móvil
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (menuToggle && navLinks) menuToggle.addEventListener('click', () => navLinks.classList.toggle('active'));

    // Sidebar Dashboard
    const dashBtn = document.querySelector('.dashboard-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if(dashBtn && sidebar) {
        dashBtn.addEventListener('click', () => { 
            sidebar.classList.toggle('active'); 
            if(overlay) overlay.classList.toggle('active'); 
        });
    }
    if(overlay) overlay.addEventListener('click', () => { 
        sidebar.classList.remove('active'); 
        overlay.classList.remove('active'); 
    });

    // Animaciones
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('active'); observer.unobserve(entry.target); }});
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // Cargas según página
    if (document.querySelector('.dashboard-layout')) configurarDashboard();
    if (document.getElementById('eventsContainer')) {
        actualizarInterfazLanding();
        cargarEventosLanding();
        configurarModalLogin();
    }
});

// ==========================================
// 3. LOGIN Y REGISTRO (ARREGLADO)
// ==========================================
function validarPasswordFrontend(password) {
    if (password.length < 8) return "Mínimo 8 caracteres.";
    if (!/\\d/.test(password)) return "Debe incluir al menos un número.";
    if (!/[A-Z]/.test(password)) return "Debe incluir al menos una mayúscula.";
    return null;
}

function configurarModalLogin() { 
    const modal = document.getElementById("loginModal");
    if(modal) {
        // Toggle Global
        window.toggleAuthMode = function(mode) {
            document.getElementById('loginSection').style.display = (mode === 'login') ? 'block' : 'none';
            document.getElementById('registerSection').style.display = (mode === 'register') ? 'block' : 'none';
            const title = document.getElementById('modalTitle');
            if(title) title.textContent = (mode === 'login') ? 'Bienvenido' : 'Crear Cuenta';
            const msg = document.getElementById('loginMessage');
            if(msg) msg.textContent = '';
        }

        const loginForm = document.getElementById('universalLoginForm');
        const registerForm = document.getElementById('publicRegisterForm');

        // LOGIN
        if(loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const msg = document.getElementById('loginMessage');
                try {
                    const res = await fetch(`${API_URL}/login`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ usuario: document.getElementById('loginUser').value, password: document.getElementById('loginPass').value }) });
                    const data = await res.json();
                    if(data.success) {
                        showToast(`¡Hola ${data.nombre}!`);
                        localStorage.setItem('usuario_logueado', 'true'); 
                        localStorage.setItem('usuario_rol', data.rol); 
                        localStorage.setItem('es_admin', data.es_admin); 
                        localStorage.setItem('usuario_nombre', data.nombre); 
                        localStorage.setItem('usuario_id', data.id);
                        setTimeout(() => window.location.href = '/dashboard', 1000);
                    } else { 
                        if(msg) { msg.textContent = data.mensaje; msg.style.color = 'red'; }
                        showToast(data.mensaje, "error");
                    }
                } catch(e) { showToast("Error de conexión", "error"); }
            });
        }

        // REGISTRO
        if(registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const msg = document.getElementById('loginMessage');
                const user = document.getElementById('regUser').value;
                const pass = document.getElementById('regPass').value;
                const btn = registerForm.querySelector('button[type="submit"]');

                if (!user.endsWith('@gmail.com')) { 
                    showToast("Solo se permiten correos @gmail.com", "error");
                    return; 
                }
                const errorPass = validarPasswordFrontend(pass);
                if (errorPass) {
                    showToast(errorPass, "error");
                    return;
                }

                const data = { 
                    username: user, 
                    password: pass, 
                    nombre: document.getElementById('regNombre').value, 
                    telefono: document.getElementById('regTel').value,
                    nivel: document.getElementById('regNivel') ? document.getElementById('regNivel').value : 'Principiante'
                };

                try {
                    btn.disabled = true; btn.innerText = "Creando...";
                    const res = await fetch(`${API_URL}/register`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                    const result = await res.json();
                    
                    if(result.success) {
                        showToast("¡Cuenta creada! Inicia sesión.", "success");
                        toggleAuthMode('login');
                        registerForm.reset();
                        document.getElementById('loginUser').value = user; // Prellenar
                    } else {
                        showToast(result.mensaje, "error");
                        if(msg) { msg.textContent = result.mensaje; msg.style.color = 'red'; }
                    }
                } catch(e) { showToast("Error al registrar", "error"); }
                finally { btn.disabled = false; btn.innerText = "Crear Cuenta"; }
            });
        }
    }
}

// ==========================================
// 4. LÓGICA DASHBOARD Y ROLES
// ==========================================
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

// Utilidades
function mostrarMenu(id) { document.getElementById(id).style.display = 'block'; }
function mostrarElemento(id) { const el = document.getElementById(id); if(el) el.style.display = 'flex'; }
function ocultarElemento(id) { const el = document.getElementById(id); if(el) el.style.display = 'none'; }
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

// --- CRUD USUARIOS ---
async function cargarUsuariosAdmin() { const r=await fetch(`${API_URL}/usuarios`); const d=await r.json(); const t=document.getElementById('tablaUsuarios'); const s=document.getElementById('pagoUsuario'); if(s){ s.innerHTML='<option value="">Seleccionar...</option>'; d.filter(u=>u.rol==='alumno').forEach(u=>s.innerHTML+=`<option value="${u.id}">${u.nombre||u.username}</option>`);} if(t) t.innerHTML=d.map(u=>`<tr><td><strong>${u.username}</strong></td><td>${u.rol}</td><td style="text-align:right"><button onclick="borrarUsuario(${u.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarUsuario(e) { 
    e.preventDefault(); 
    const pass = document.getElementById('usuarioPassword').value;
    if(pass) {
         const err = validarPasswordFrontend(pass);
         if(err) { showToast(err, "error"); return; }
    }
    const d={username:document.getElementById('usuarioUsername').value, rol:document.getElementById('usuarioRol').value, nombre:document.getElementById('usuarioNombre').value, telefono:document.getElementById('usuarioTelefono').value, nivel:document.getElementById('usuarioNivel')?document.getElementById('usuarioNivel').value:'', password:pass}; 
    await fetch(`${API_URL}/usuarios`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}); 
    document.getElementById('formUsuario').reset(); cargarUsuariosAdmin(); showToast("Usuario agregado");
}
window.borrarUsuario=async(id)=>{ showConfirm("¿Borrar usuario?", async () => { await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); cargarUsuariosAdmin(); showToast("Usuario borrado"); }); };
window.toggleCamposAlumno = function() { const r=document.getElementById('usuarioRol').value; document.querySelectorAll('.campo-alumno').forEach(c=>c.style.display=(r==='alumno')?'block':'none'); }

// --- OTROS CRUD ---
async function cargarPagosAdmin() { const res = await fetch(`${API_URL}/pagos`); const data = await res.json(); const tbody = document.getElementById('tablaPagos'); if(tbody) tbody.innerHTML = data.map(p => `<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarPago(e) { e.preventDefault(); await genericPost(`${API_URL}/pagos`, { usuario_id: document.getElementById('pagoUsuario').value, concepto: document.getElementById('pagoConcepto').value, monto: document.getElementById('pagoMonto').value }); document.getElementById('formPago').reset(); cargarPagosAdmin(); showToast("Pago guardado"); }
window.borrarPago=async(id)=>{ showConfirm("¿Borrar pago?", async () => { await fetch(`${API_URL}/pagos/${id}`, {method:'DELETE'}); cargarPagosAdmin(); showToast("Pago eliminado"); }); };

async function cargarEventosAdmin() { const res = await fetch(`${API_URL}/eventos`); const data = await res.json(); const tbody = document.getElementById('tablaEventos'); if(tbody) tbody.innerHTML = data.map(ev => `<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarEvento(e) { e.preventDefault(); await genericPost(`${API_URL}/eventos`, { titulo: document.getElementById('tituloEvento').value, fecha: document.getElementById('fechaEvento').value, lugar: document.getElementById('lugarEvento').value, hora: document.getElementById('horaEvento').value }); document.getElementById('formEvento').reset(); cargarEventosAdmin(); showToast("Evento creado"); }
window.borrarEvento=async(id)=>{ showConfirm("¿Borrar evento?", async () => { await fetch(`${API_URL}/eventos/${id}`, {method:'DELETE'}); cargarEventosAdmin(); showToast("Evento eliminado"); }); };

async function cargarVestuarioAdmin() { const r=await fetch(`${API_URL}/vestuario`); const d=await r.json(); const t=document.getElementById('tablaVestuario'); if(t) t.innerHTML=d.map(v=>`<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarVestuario(e) { e.preventDefault(); await genericPost(`${API_URL}/vestuario`, { nombre: document.getElementById('vestuarioNombre').value, tipo: document.getElementById('vestuarioTipo').value, cantidad: document.getElementById('vestuarioCantidad').value, talla: document.getElementById('vestuarioTalla').value, estado: document.getElementById('vestuarioEstado').value }); document.getElementById('formVestuario').reset(); cargarVestuarioAdmin(); showToast("Ítem guardado"); }
window.borrarVestuario=async(id)=>{ showConfirm("¿Borrar ítem?", async () => { await fetch(`${API_URL}/vestuario/${id}`, {method:'DELETE'}); cargarVestuarioAdmin(); showToast("Ítem eliminado"); }); };

async function genericPost(url, data) { try { await fetch(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); return true; } catch(e){ return false; } }

// --- QR & ASISTENCIA (REPARADO) ---
window.generarQR = function() {
    const container = document.getElementById('qrcode');
    if(!container) return;
    const hoy = new Date().toISOString().split('T')[0];
    container.innerHTML = "";
    new QRCode(container, { text: `NAYAHUARI_ASISTENCIA_${hoy}`, width: 200, height: 200 });
    document.getElementById('qr-date-label').textContent = `Código: ${hoy}`;
}

let html5QrcodeScanner = null;
window.iniciarEscaner = function() {
    const reader = document.getElementById('reader');
    if(!reader) return;
    reader.style.display = "block";
    
    if (html5QrcodeScanner) html5QrcodeScanner.clear();
    
    html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(async (decodedText) => {
        html5QrcodeScanner.clear();
        reader.style.display = "none";
        try {
            const res = await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ qr_data: decodedText, id_usuario: usuarioId }) });
            const data = await res.json();
            if(data.success) { showToast(data.mensaje, "success"); }
            else { showToast(data.mensaje, "error"); }
        } catch(e) { showToast("Error de conexión", "error"); }
    });
}

// Alumno vistas
async function cargarEventosAlumno(){const r=await fetch(`${API_URL}/eventos`);const d=await r.json();const c=document.getElementById('alumnoEventosContainer');if(c)c.innerHTML=d.map(ev=>`<div class="stat-card"><div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha}</p></div></div>`).join('')}
async function cargarVestuarioAlumno(){const r=await fetch(`${API_URL}/vestuario`);const d=await r.json();const c=document.getElementById('alumnoVestuarioContainer');if(c)c.innerHTML=d.map(v=>`<div class="stat-card" style="border-left:5px solid var(--accent)"><div><h4 style="margin:0">${v.nombre}</h4><p>${v.talla}</p></div></div>`).join('')}

function actualizarInterfazLanding() {
    if(usuarioLogueado) {
        const btnAuth = document.getElementById('btnAuth');
        if(btnAuth) { 
            btnAuth.innerHTML = '<span class="material-icons">logout</span> Salir'; 
            btnAuth.onclick = window.cerrarSesion; // Usar la función global
        }
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

// Cierre de Sesión Global
window.cerrarSesion = function() {
    showConfirm("¿Cerrar sesión?", () => {
        localStorage.clear();
        window.location.href = '/';
    });
};
"""

with open("static/js/main.js", "w", encoding="utf-8") as f:
    f.write(contenido_js)

print("✅ REPARADO: Botón Registro, Alertas y QR.")
print("1. Recarga con Ctrl+F5")
print("2. Prueba crear cuenta y luego iniciar sesión.")
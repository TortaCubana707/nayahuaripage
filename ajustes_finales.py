import os

print("🚀 APLICANDO AJUSTES FINALES: REGISTRO Y ALERTAS FUNCIONALES...")

# ==============================================================================
# 1. JS (Alertas Globales + Registro Reparado + QR)
# ==============================================================================
contenido_js = """
const API_URL = '/api';
let usuarioRol = localStorage.getItem('usuario_rol');
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre') || 'Invitado';
let usuarioId = localStorage.getItem('usuario_id');

// --- SISTEMA DE ALERTAS (GLOBAL) ---
// Definidas fuera para que todos puedan usarlas
function showToast(message, type = 'success') {
    const div = document.createElement('div');
    div.className = `custom-toast ${type}`;
    const icon = type === 'success' ? 'check_circle' : 'error';
    div.innerHTML = `<span class="material-icons">${icon}</span> <div>${message}</div>`;
    document.body.appendChild(div);
    setTimeout(() => {
        div.style.animation = 'fadeOutToast 0.5s forwards';
        setTimeout(() => div.remove(), 500);
    }, 3000);
}

function showConfirm(message, onYes) {
    const overlay = document.createElement('div');
    overlay.className = 'custom-confirm-overlay';
    overlay.innerHTML = `
        <div class="custom-confirm-box">
            <span class="material-icons" style="font-size: 3rem; color: #E6007E; margin-bottom: 10px;">help_outline</span>
            <h3 style="margin: 0; color: #081a49;">¿Estás seguro?</h3>
            <p style="color: #64748b; margin-top: 10px;">${message}</p>
            <div class="custom-confirm-btns">
                <button class="btn-confirm-no" id="btnNo">Cancelar</button>
                <button class="btn-confirm-yes" id="btnYes">Sí, confirmar</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById('btnNo').onclick = () => overlay.remove();
    document.getElementById('btnYes').onclick = () => { overlay.remove(); onYes(); };
}

// --- VALIDACIÓN DE CONTRASEÑA ---
function validarPasswordFrontend(password) {
    if (password.length < 8) return "Mínimo 8 caracteres.";
    if (!/\d/.test(password)) return "Debe incluir al menos un número.";
    if (!/[A-Z]/.test(password)) return "Debe incluir al menos una mayúscula.";
    return null;
}

document.addEventListener('DOMContentLoaded', () => {
    // Inyectar estilos de alertas
    const style = document.createElement('style');
    style.innerHTML = `
        .custom-toast { position: fixed; top: 20px; right: 20px; background: white; padding: 15px 25px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); z-index: 10000; display: flex; align-items: center; gap: 12px; animation: slideInRight 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); border-left: 5px solid #333; font-family: 'Segoe UI', sans-serif; }
        .custom-toast.success { border-left-color: #00695C; } .custom-toast.success span { color: #00695C; }
        .custom-toast.error { border-left-color: #ef4444; } .custom-toast.error span { color: #ef4444; }
        .custom-confirm-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(8, 26, 73, 0.8); z-index: 10001; display: flex; justify-content: center; align-items: center; animation: fadeIn 0.2s; backdrop-filter: blur(4px); }
        .custom-confirm-box { background: white; padding: 30px; border-radius: 20px; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.3); animation: scaleUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .custom-confirm-btns { display: flex; justify-content: center; gap: 15px; margin-top: 25px; }
        .btn-confirm-yes { background: #E6007E; color: white; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        .btn-confirm-yes:hover { transform: scale(1.05); background: #B40062; }
        .btn-confirm-no { background: #f1f5f9; color: #64748b; border: none; padding: 12px 25px; border-radius: 50px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        .btn-confirm-no:hover { background: #e2e8f0; }
        @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes fadeOutToast { to { transform: translateX(100%); opacity: 0; } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes scaleUp { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
    `;
    document.head.appendChild(style);

    // Menú móvil
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (menuToggle && navLinks) menuToggle.addEventListener('click', () => navLinks.classList.toggle('active'));
    
    // Sidebar Dashboard
    const dashBtn = document.querySelector('.dashboard-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if(dashBtn && sidebar) {
        dashBtn.addEventListener('click', () => { sidebar.classList.toggle('active'); if(overlay) overlay.classList.toggle('active'); });
    }
    if(overlay) overlay.addEventListener('click', () => { sidebar.classList.remove('active'); overlay.classList.remove('active'); });

    // Animaciones
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('active'); observer.unobserve(entry.target); }});
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // Inicializadores
    if (document.querySelector('.dashboard-layout')) configurarDashboard();
    if (document.getElementById('eventsContainer')) {
        actualizarInterfazLanding();
        cargarEventosLanding();
        configurarModalLogin();
        configurarRegistroPublico(); // ¡ESTA FALTABA!
    }
});

// --- LÓGICA DE REGISTRO (ARREGLADA) ---
function configurarRegistroPublico() {
    const form = document.getElementById('publicRegisterForm');
    if(!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = document.getElementById('loginMessage'); // Usamos el mensaje del modal
        const user = document.getElementById('regUser').value;
        const pass = document.getElementById('regPass').value;
        const btn = form.querySelector('button[type="submit"]');
        
        // 1. Validaciones
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
            nivel: document.getElementById('regNivel').value
        };

        try {
            btn.disabled = true; btn.innerText = "Registrando...";
            
            const res = await fetch(`${API_URL}/register`, { 
                method: 'POST', 
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify(data) 
            });
            const result = await res.json();
            
            if(result.success) {
                showToast("¡Cuenta creada con éxito!", "success");
                form.reset();
                // Volver al login automáticamente
                if(window.toggleAuthMode) {
                    window.toggleAuthMode('login');
                    // Rellenar usuario para facilitar
                    document.getElementById('loginUser').value = user;
                }
            } else { 
                showToast(result.mensaje, "error");
            }
        } catch(e) { 
            showToast("Error de conexión con el servidor", "error");
        } finally {
            btn.disabled = false; btn.innerText = "Crear Cuenta";
        }
    });
}

// --- GENERAR QR ÚNICO ---
window.generarQR = function() {
    const container = document.getElementById('qrcode');
    const label = document.getElementById('qr-date-label');
    const btn = document.querySelector("button[onclick='generarQR()']");
    
    const fechaObj = new Date();
    const isoDate = fechaObj.toISOString().split('T')[0]; 
    const fechaBonita = `${String(fechaObj.getDate()).padStart(2,'0')}/${String(fechaObj.getMonth()+1).padStart(2,'0')}/${fechaObj.getFullYear()}`;
    const codigo = `NAYAHUARI_ASISTENCIA_${isoDate}`;

    container.innerHTML = "";
    new QRCode(container, { text: codigo, width: 200, height: 200, colorDark : "#081a49", colorLight : "#ffffff", correctLevel : QRCode.CorrectLevel.H });
    
    label.textContent = `QR del día ${fechaBonita}`;
    label.style.display = "block";
    
    if(btn) {
        btn.innerHTML = '<span class="material-icons">check_circle</span> QR Activo';
        btn.style.background = "#ccc";
        btn.disabled = true;
    }
}

// --- EVENTOS EN INDEX ---
async function cargarEventosLanding() {
    const c = document.getElementById('eventsContainer');
    if(!c) return;
    try {
        const res = await fetch(`${API_URL}/eventos`);
        const data = await res.json();
        c.innerHTML = '';
        if (data.length === 0) {
            c.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #888;">No hay eventos próximos.</p>';
            return;
        }
        data.forEach(ev => {
            let dia="•", mes="";
            if(ev.fecha) { const p=ev.fecha.split('-'); if(p.length===3){ dia=p[2]; const m=["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]; mes=m[parseInt(p[1])-1]||""; } }
            let dateBox = `<div class="date"><span class="day">${dia}</span><span class="month">${mes}</span></div>`;
            if(ev.imagen_url && ev.imagen_url.length > 5) { dateBox = `<div class="date" style="background: url('${ev.imagen_url}') center/cover no-repeat; text-indent: -9999px; border: 2px solid white;">IMG</div>`; }
            c.innerHTML += `<div class="event-card reveal active">${dateBox}<div class="details"><h4 style="margin:0 0 5px 0;font-size:1.2rem;">${ev.titulo}</h4><p style="font-size:0.9rem;color:#666;margin:0;"><span class="material-icons" style="font-size:14px;vertical-align:middle;">place</span> ${ev.lugar}</p><p style="font-size:0.85rem;color:var(--azul-talavera);margin-top:5px;font-weight:bold;">${ev.fecha} - ${ev.hora}</p></div></div>`;
        });
    } catch(e) { console.error(e); }
}

// --- DASHBOARD ---
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
    } else if (usuarioRol === 'administrativo' || usuarioRol === 'staff') {
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

// CRUDs con ALERTAS NUEVAS
async function cargarUsuariosAdmin() { const r=await fetch(`${API_URL}/usuarios`); const d=await r.json(); const t=document.getElementById('tablaUsuarios'); const s=document.getElementById('pagoUsuario'); if(s){ s.innerHTML='<option value="">Seleccionar...</option>'; d.filter(u=>u.rol==='alumno').forEach(u=>s.innerHTML+=`<option value="${u.id}">${u.nombre||u.username}</option>`);} if(t) t.innerHTML=d.map(u=>`<tr><td><strong>${u.username}</strong></td><td>${u.rol}</td><td>${u.nombre||'-'}</td><td style="text-align:right"><button onclick="borrarUsuario(${u.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }

async function agregarUsuario(e) {
    e.preventDefault(); const id = document.getElementById('usuarioId').value;
    const data = { username: document.getElementById('usuarioUsername').value, rol: document.getElementById('usuarioRol').value, nombre: document.getElementById('usuarioNombre').value, telefono: document.getElementById('usuarioTelefono').value, nivel: document.getElementById('usuarioNivel').value };
    const pass = document.getElementById('usuarioPassword').value; if(pass) data.password = pass;
    showToast("Guardando usuario...", "success");
    let res;
    if(id) res = await fetch(`${API_URL}/usuarios/${id}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
    else res = await fetch(`${API_URL}/usuarios`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
    if(res.ok) { showToast("Usuario guardado con éxito"); limpiarFormUsuario(); cargarUsuariosAdmin(); }
    else { showToast("Error al guardar", "error"); }
}
window.borrarUsuario=(id)=>{ showConfirm("¿Eliminar este usuario permanentemente?", async()=>{ await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); showToast("Usuario eliminado"); cargarUsuariosAdmin(); }); };

window.limpiarFormUsuario = function() { document.getElementById('formUsuario').reset(); document.getElementById('usuarioId').value=''; document.querySelector('#formUsuario button').innerHTML='<span class="material-icons">save</span> Guardar'; }
window.toggleCamposAlumno = function() { const r=document.getElementById('usuarioRol').value; document.querySelectorAll('.campo-alumno').forEach(c=>c.style.display=(r==='alumno')?'block':'none'); }

async function cargarPagosAdmin() { const r=await fetch(`${API_URL}/pagos`); const d=await r.json(); const t=document.getElementById('tablaPagos'); if(t) t.innerHTML=d.map(p=>`<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarPago(e) { e.preventDefault(); await fetch(`${API_URL}/pagos`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ usuario_id: document.getElementById('pagoUsuario').value, concepto: document.getElementById('pagoConcepto').value, monto: document.getElementById('pagoMonto').value })}); document.getElementById('formPago').reset(); showToast("Pago registrado"); cargarPagosAdmin(); }
window.borrarPago=(id)=>{ showConfirm("¿Borrar pago?", async()=>{ await fetch(`${API_URL}/pagos/${id}`, {method:'DELETE'}); showToast("Pago eliminado"); cargarPagosAdmin(); }); };

async function cargarEventosAdmin() { const r=await fetch(`${API_URL}/eventos`); const d=await r.json(); const t=document.getElementById('tablaEventos'); if(t) t.innerHTML=d.map(ev=>`<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarEvento(e) { e.preventDefault(); await fetch(`${API_URL}/eventos`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ titulo: document.getElementById('tituloEvento').value, fecha: document.getElementById('fechaEvento').value, lugar: document.getElementById('lugarEvento').value, hora: document.getElementById('horaEvento').value })}); document.getElementById('formEvento').reset(); showToast("Evento creado"); cargarEventosAdmin(); }
window.borrarEvento=(id)=>{ showConfirm("¿Borrar evento?", async()=>{ await fetch(`${API_URL}/eventos/${id}`, {method:'DELETE'}); showToast("Evento eliminado"); cargarEventosAdmin(); }); };

async function cargarVestuarioAdmin() { const r=await fetch(`${API_URL}/vestuario`); const d=await r.json(); const t=document.getElementById('tablaVestuario'); if(t) t.innerHTML=d.map(v=>`<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarVestuario(e) { e.preventDefault(); await fetch(`${API_URL}/vestuario`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ nombre: document.getElementById('vestuarioNombre').value, tipo: document.getElementById('vestuarioTipo').value, cantidad: document.getElementById('vestuarioCantidad').value, talla: document.getElementById('vestuarioTalla').value, estado: document.getElementById('vestuarioEstado').value })}); document.getElementById('formVestuario').reset(); showToast("Ítem agregado"); cargarVestuarioAdmin(); }
window.borrarVestuario=(id)=>{ showConfirm("¿Borrar ítem?", async()=>{ await fetch(`${API_URL}/vestuario/${id}`, {method:'DELETE'}); showToast("Ítem eliminado"); cargarVestuarioAdmin(); }); };

// ALUMNO
let html5QrcodeScanner = null;
window.iniciarEscaner = function() { document.getElementById('reader').style.display = "block"; if (html5QrcodeScanner) html5QrcodeScanner.clear(); html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 }); html5QrcodeScanner.render(async (decodedText) => { html5QrcodeScanner.clear(); document.getElementById('reader').style.display = "none"; try { const res = await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ qr_data: decodedText, id_usuario: usuarioId }) }); const data = await res.json(); showToast(data.mensaje, data.success ? 'success' : 'error'); } catch(e) { showToast("Error", "error"); } }); }
async function cargarEventosAlumno(){const r=await fetch(`${API_URL}/eventos`);const d=await r.json();const c=document.getElementById('alumnoEventosContainer');if(c)c.innerHTML=d.map(ev=>`<div class="stat-card"><div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha}</p></div></div>`).join('')}
async function cargarVestuarioAlumno(){const r=await fetch(`${API_URL}/vestuario`);const d=await r.json();const c=document.getElementById('alumnoVestuarioContainer');if(c)c.innerHTML=d.map(v=>`<div class="stat-card" style="border-left:5px solid var(--accent)"><div><h4 style="margin:0">${v.nombre}</h4><p>${v.talla}</p></div></div>`).join('')}

// LOGIN
function configurarModalLogin() { 
    const modal = document.getElementById("loginModal");
    if(modal) {
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
                        showToast(`¡Bienvenido ${data.nombre}!`);
                        localStorage.setItem('usuario_logueado', 'true'); localStorage.setItem('usuario_rol', data.rol); localStorage.setItem('es_admin', data.es_admin); localStorage.setItem('usuario_nombre', data.nombre); localStorage.setItem('usuario_id', data.id);
                        setTimeout(() => window.location.href = '/dashboard', 1000);
                    } else { showToast(data.mensaje, "error"); }
                } catch(e) { showToast("Error de conexión", "error"); }
            });
        }
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
window.cerrarSesion = function() { 
    showConfirm("¿Deseas cerrar sesión?", () => { 
        localStorage.clear(); 
        window.location.href = '/'; 
    }); 
};
"""

# Ejecución
print("🔧 Escribiendo main.js con alertas personalizadas y arreglos finales...")
with open("static/js/main.js", "w", encoding="utf-8") as f:
    f.write(contenido_js)

print("✅ ¡LISTO! Alertas y Registro de Alumnos funcionando.")
print("1. Recarga la página (Ctrl+F5).")
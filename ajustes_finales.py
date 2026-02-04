import os

print("🚀 APLICANDO CORRECCIONES VISUALES AL INDEX Y MANTENIENDO QR...")

# ==============================================================================
# 1. JS (Mantiene tu lógica de QR Único + Fotos en Eventos)
# ==============================================================================
contenido_js = """
const API_URL = '/api';
let usuarioRol = localStorage.getItem('usuario_rol');
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre') || 'Invitado';
let usuarioId = localStorage.getItem('usuario_id');

document.addEventListener('DOMContentLoaded', () => {
    // 1. Menú móvil (Index y Dashboard)
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => { navLinks.classList.toggle('active'); });
    }
    
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

    // 2. Animaciones Scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    // 3. Inicializadores por página
    if (document.querySelector('.dashboard-layout')) configurarDashboard();
    
    if (document.getElementById('eventsContainer')) {
        actualizarInterfazLanding();
        cargarEventosLanding(); // Carga eventos con fotos si existen
        configurarModalLogin();
    }
});

// --- QR ÚNICO Y CON FECHA ---
window.generarQR = function() {
    const container = document.getElementById('qrcode');
    const label = document.getElementById('qr-date-label');
    const btn = document.querySelector("button[onclick='generarQR()']");
    
    const fechaObj = new Date();
    const isoDate = fechaObj.toISOString().split('T')[0]; 
    const dia = String(fechaObj.getDate()).padStart(2, '0');
    const mes = String(fechaObj.getMonth() + 1).padStart(2, '0');
    const anio = fechaObj.getFullYear();
    const fechaBonita = `${dia}/${mes}/${anio}`;

    const codigo = `NAYAHUARI_ASISTENCIA_${isoDate}`;

    container.innerHTML = "";
    new QRCode(container, { 
        text: codigo, 
        width: 200, 
        height: 200, 
        colorDark : "#081a49", 
        colorLight : "#ffffff", 
        correctLevel : QRCode.CorrectLevel.H 
    });
    
    label.textContent = `Qr del dia ${fechaBonita}`;
    label.style.display = "block";
    label.style.color = "var(--azul-talavera)";
    
    // Bloquear botón tras generar
    if(btn) {
        btn.innerHTML = '<span class="material-icons">check_circle</span> QR Activo';
        btn.classList.remove('btn-success');
        btn.style.backgroundColor = "#ccc";
        btn.style.cursor = "default";
        btn.disabled = true;
    }
}

// --- EVENTOS EN INDEX (CON IMAGEN DE FONDO) ---
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
            let dia = "•", mes = "";
            if (ev.fecha) {
                const partes = ev.fecha.split('-');
                if(partes.length === 3) {
                    dia = partes[2];
                    const meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"];
                    mes = meses[parseInt(partes[1]) - 1] || "";
                }
            }
            
            // Si hay URL de imagen, la usamos de fondo
            let dateBox = `<div class="date"><span class="day">${dia}</span><span class="month">${mes}</span></div>`;
            if(ev.imagen_url && ev.imagen_url.length > 5) {
                dateBox = `<div class="date" style="background: url('${ev.imagen_url}') center/cover no-repeat; text-indent: -9999px; border: 2px solid white;">IMG</div>`;
            }

            c.innerHTML += `
            <div class="event-card reveal active">
                ${dateBox}
                <div class="details">
                    <h4 style="margin: 0 0 5px 0; font-size: 1.2rem;">${ev.titulo}</h4>
                    <p style="font-size: 0.9rem; color: #666; margin: 0;">
                        <span class="material-icons" style="font-size: 14px; vertical-align: middle;">place</span> ${ev.lugar}
                    </p>
                    <p style="font-size: 0.85rem; color: var(--azul-talavera); margin-top: 5px; font-weight: bold;">
                        ${ev.fecha} - ${ev.hora}
                    </p>
                </div>
            </div>`;
        });
    } catch(e) {
        console.error("Error eventos:", e);
    }
}

// ... (Resto de lógica Dashboard y Login se mantiene igual) ...

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

async function cargarUsuariosAdmin() { const r=await fetch(`${API_URL}/usuarios`); const d=await r.json(); const t=document.getElementById('tablaUsuarios'); const s=document.getElementById('pagoUsuario'); if(s){ s.innerHTML='<option value="">Seleccionar...</option>'; d.filter(u=>u.rol==='alumno').forEach(u=>s.innerHTML+=`<option value="${u.id}">${u.nombre||u.username}</option>`);} if(t) t.innerHTML=d.map(u=>`<tr><td>${u.username}</td><td>${u.rol}</td><td style="text-align:right"><button onclick="borrarUsuario(${u.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarUsuario(e) { e.preventDefault(); const d={username:document.getElementById('usuarioUsername').value, rol:document.getElementById('usuarioRol').value, nombre:document.getElementById('usuarioNombre').value, telefono:document.getElementById('usuarioTelefono').value, nivel:document.getElementById('usuarioNivel').value, password:document.getElementById('usuarioPassword').value}; await fetch(`${API_URL}/usuarios`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}); document.getElementById('formUsuario').reset(); cargarUsuariosAdmin(); }
window.borrarUsuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); cargarUsuariosAdmin(); }};
window.editarUsuario = function(id, user, rol, nombre, tel, nivel) { document.getElementById('usuarioId').value=id; document.getElementById('usuarioUsername').value=user; document.getElementById('usuarioRol').value=rol; document.getElementById('usuarioNombre').value=nombre; document.getElementById('usuarioTelefono').value=tel; document.getElementById('usuarioNivel').value=nivel; toggleCamposAlumno(); document.querySelector('#formUsuario button').innerHTML='Actualizar'; }
window.limpiarFormUsuario = function() { document.getElementById('formUsuario').reset(); document.getElementById('usuarioId').value=''; document.querySelector('#formUsuario button').innerHTML='Crear'; toggleCamposAlumno(); }
window.toggleCamposAlumno = function() { const r=document.getElementById('usuarioRol').value; document.querySelectorAll('.campo-alumno').forEach(c=>c.style.display=(r==='alumno')?'block':'none'); }

async function cargarPagosAdmin() { const res = await fetch(`${API_URL}/pagos`); const data = await res.json(); const tbody = document.getElementById('tablaPagos'); if(tbody) tbody.innerHTML = data.map(p => `<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarPago(e) { e.preventDefault(); await genericPost(`${API_URL}/pagos`, { usuario_id: document.getElementById('pagoUsuario').value, concepto: document.getElementById('pagoConcepto').value, monto: document.getElementById('pagoMonto').value }); document.getElementById('formPago').reset(); cargarPagosAdmin(); }
window.borrarPago=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/pagos/${id}`, {method:'DELETE'}); cargarPagosAdmin(); }};

async function cargarEventosAdmin() { const res = await fetch(`${API_URL}/eventos`); const data = await res.json(); const tbody = document.getElementById('tablaEventos'); if(tbody) tbody.innerHTML = data.map(ev => `<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarEvento(e) {
    e.preventDefault();
    const id = document.getElementById('eventoId').value;
    const data = {
        titulo: document.getElementById('tituloEvento').value,
        fecha: document.getElementById('fechaEvento').value,
        lugar: document.getElementById('lugarEvento').value,
        hora: document.getElementById('horaEvento').value,
        imagen_url: document.getElementById('imagenEvento').value
    };
    if(id) await fetch(`${API_URL}/eventos/${id}`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    else await fetch(`${API_URL}/eventos`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    window.limpiarFormEvento();
    cargarEventosAdmin();
}
window.editarEvento = function(id, tit, fec, lug, hor, img) {
    document.getElementById('eventoId').value = id;
    document.getElementById('tituloEvento').value = tit;
    document.getElementById('fechaEvento').value = fec;
    document.getElementById('lugarEvento').value = lug;
    document.getElementById('horaEvento').value = hor;
    document.getElementById('imagenEvento').value = (img === 'null' || img === 'undefined') ? '' : img;
    document.querySelector('#formEvento button').innerHTML = '<span class="material-icons">save</span> Actualizar';
}
window.limpiarFormEvento = function() {
    document.getElementById('formEvento').reset();
    document.getElementById('eventoId').value = '';
    document.querySelector('#formEvento button').innerHTML = '<span class="material-icons">add_circle</span> Crear';
}
window.borrarEvento=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/eventos/${id}`, {method:'DELETE'}); cargarEventosAdmin(); }};

async function cargarVestuarioAdmin() { const res = await fetch(`${API_URL}/vestuario`); const data = await res.json(); const tbody = document.getElementById('tablaVestuario'); if(tbody) tbody.innerHTML = data.map(v => `<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete">x</button></td></tr>`).join(''); }
async function agregarVestuario(e) { e.preventDefault(); await genericPost(`${API_URL}/vestuario`, { nombre: document.getElementById('vestuarioNombre').value, tipo: document.getElementById('vestuarioTipo').value, cantidad: document.getElementById('vestuarioCantidad').value, talla: document.getElementById('vestuarioTalla').value, estado: document.getElementById('vestuarioEstado').value }); document.getElementById('formVestuario').reset(); cargarVestuarioAdmin(); }
window.borrarVestuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/vestuario/${id}`, {method:'DELETE'}); cargarVestuarioAdmin(); }};
async function genericPost(url, data) { try { await fetch(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); return true; } catch(e){ return false; } }

window.buscarAsistencia = async function() { const fecha=document.getElementById('fechaAsistencia').value; const res=await fetch(`${API_URL}/asistencia?fecha=${fecha}`); const data=await res.json(); const tbody=document.getElementById('tablaAsistencia'); tbody.innerHTML = data.map(item => `<tr><td>${item.nombre}</td><td style="text-align:center"><input type="checkbox" class="checkbox-asistencia" data-id="${item.id_usuario}" ${item.presente?'checked':''}></td></tr>`).join(''); }
window.guardarAsistencia = async function() { const fecha=document.getElementById('fechaAsistencia').value; const checkboxes=document.querySelectorAll('.checkbox-asistencia'); const registros=[]; checkboxes.forEach(cb=>{ registros.push({id_usuario:cb.dataset.id, presente:cb.checked}) }); await genericPost(`${API_URL}/asistencia`, {fecha:fecha, registros:registros}); alert("Guardado"); }

let html5QrcodeScanner = null;
window.iniciarEscaner = function() { document.getElementById('reader').style.display = "block"; if (html5QrcodeScanner) html5QrcodeScanner.clear(); html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 }); html5QrcodeScanner.render(async (decodedText) => { html5QrcodeScanner.clear(); document.getElementById('reader').style.display = "none"; try { const res = await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ qr_data: decodedText, id_usuario: usuarioId }) }); const data = await res.json(); alert(data.success ? `✅ ${data.mensaje}` : `❌ ${data.mensaje}`); } catch(e) { alert("Error"); } }); }

async function cargarEventosAlumno(){const r=await fetch(`${API_URL}/eventos`);const d=await r.json();const c=document.getElementById('alumnoEventosContainer');if(c)c.innerHTML=d.map(ev=>`<div class="stat-card"><div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha}</p></div></div>`).join('')}
async function cargarVestuarioAlumno(){const r=await fetch(`${API_URL}/vestuario`);const d=await r.json();const c=document.getElementById('alumnoVestuarioContainer');if(c)c.innerHTML=d.map(v=>`<div class="stat-card" style="border-left:5px solid var(--accent)"><div><h4 style="margin:0">${v.nombre}</h4><p>${v.talla}</p></div></div>`).join('')}

function configurarModalLogin() { 
    const form = document.getElementById('universalLoginForm');
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('loginMessage');
            try {
                const res = await fetch(`${API_URL}/login`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ usuario: document.getElementById('loginUser').value, password: document.getElementById('loginPass').value }) });
                const data = await res.json();
                if(data.success) {
                    localStorage.setItem('usuario_logueado', 'true'); localStorage.setItem('usuario_rol', data.rol); localStorage.setItem('es_admin', data.es_admin); localStorage.setItem('usuario_nombre', data.nombre); localStorage.setItem('usuario_id', data.id);
                    setTimeout(() => window.location.href = '/dashboard', 500);
                } else { msg.textContent = data.mensaje; }
            } catch(e) { msg.textContent = "Error"; }
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
window.cerrarSesion = function() { if(confirm("¿Cerrar sesión?")) { localStorage.clear(); window.location.href='/'; } };
"""

# ==============================================================================
# 2. CSS (Ajuste para Galería Controlada y Espaciado Index)
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
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } } @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

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
.year-badge { background: var(--dark-bg); color: var(--amarillo-cempasuchil); padding: 5px 15px; border-radius: 20px; font-weight: bold; }

/* GALERIA CONTROLADA (FIX: NO MÁS IMÁGENES GIGANTES) */
.gallery-grid { 
    display: grid; 
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
    gap: 25px; 
}
.gallery-item { 
    height: 350px; /* Altura fija para uniformidad */
    border-radius: var(--radius); 
    overflow: hidden; 
    position: relative; 
    box-shadow: var(--shadow); 
    cursor: pointer; 
}
.gallery-item img { 
    width: 100%; 
    height: 100%; 
    object-fit: cover; /* Recorta la imagen para llenar el espacio sin deformar */
    transition: transform 0.5s ease; 
}
.gallery-item:hover img { transform: scale(1.1); }
.gallery-overlay { position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(0,0,0,0.8), transparent); padding: 20px; opacity: 0; transition: opacity 0.3s; } 
.gallery-item:hover .gallery-overlay { opacity: 1; }

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
.user-welcome-card { background: linear-gradient(135deg, var(--rosa-mexicano), var(--azul-talavera)); color: white; padding: 3rem; border-radius: 20px; text-align: center; margin-bottom: 2rem; box-shadow: 0 15px 30px rgba(37, 99, 235, 0.25); }

/* QR */
#qrcode-container { padding: 20px; background: #f8fafc; border-radius: 16px; margin: 20px 0; border: 2px dashed var(--azul-talavera); display: flex; flex-direction: column; align-items: center; }
#qrcode img { display: block; margin: 0 auto; }

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
.click-anim { animation: pulsacion 0.3s ease; } @keyframes pulsacion { 0% { transform: scale(0.9); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }

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
    .sidebar { display: flex; position: fixed; top: 0; left: -100%; width: 80%; height: 100vh; z-index: 1000; transition: left 0.3s; }
    .sidebar.active { left: 0; }
    .sidebar-overlay.active { display: block; }
    .dashboard-menu-btn { display: block; }
    .dashboard-layout { display: block; position: relative; }
    .main-content { padding: 5rem 1.5rem 2rem; }
    .form-grid-responsive { gap: 20px; }
    .timeline::after { left: 20px; } .timeline-item { width: 100%; padding-left: 60px; padding-right: 10px; text-align: left; } .timeline-item.right { left: 0; } .timeline-icon { left: 0; } .timeline-item.left .timeline-icon, .timeline-item.right .timeline-icon { left: -4px; right: auto; }
}
"""

# Ejecución
print("🔧 Reparando JS (QR Único + Eventos) y CSS (Espaciado)...")
with open("static/js/main.js", "w", encoding="utf-8") as f: f.write(contenido_js)
with open("static/css/estilos.css", "w", encoding="utf-8") as f: f.write(contenido_css)

print("✅ AJUSTES APLICADOS:")
print("- QR: Se bloquea tras generar y muestra la fecha bonita.")
print("- Index: Los eventos ahora se fuerzan a 'active' para que se vean siempre.")
print("- Dashboard: Se aumentó el 'padding' en las celdas de la tabla para dar aire a los nombres.")
print("- Galería: Se forzó el grid para que las imágenes tengan un tamaño fijo y no se vean enormes.")
print("1. Reinicia el servidor: python app.py")
print("2. Recarga con Ctrl+F5")
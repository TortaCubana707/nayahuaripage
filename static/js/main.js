
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
    // Cerrar sidebar al hacer clic en un item
    document.querySelectorAll('.sidebar .menu-item').forEach(item => {
        item.addEventListener('click', () => {
             if(window.innerWidth <= 768) {
                 if(sidebar) sidebar.classList.remove('active');
                 if(overlay) overlay.classList.remove('active');
             }
        });
    });

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
        configurarModalLogin();
    }
});

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
        cargarVestuarioAdmin();
        bindForm('formVestuario', agregarVestuario);
        mostrarSeccion('asistencia');
    }
    else {
        document.getElementById('userMenu').style.display = 'block';
        document.getElementById('userWelcomeName').textContent = `¡Hola, ${nombreUsuario}!`;
        cargarEventosAlumno(); cargarVestuarioAlumno();
        mostrarSeccion('alumno-asistencia');
    }
}

function mostrarMenu(id) { document.getElementById(id).style.display = 'block'; }
function mostrarElemento(id) { document.getElementById(id).style.display = 'flex'; }
function ocultarElemento(id) { document.getElementById(id).style.display = 'none'; }
function bindForm(id, h) { const f = document.getElementById(id); if(f) f.addEventListener('submit', h); }

function cargarTodoAdmin() {
    cargarUsuariosAdmin(); cargarEventosAdmin(); cargarPagosAdmin(); cargarVestuarioAdmin();
    const hoy = new Date().toISOString().split('T')[0]; document.getElementById('fechaAsistencia').value = hoy;
    bindForm('formUsuario', agregarUsuario); bindForm('formEvento', agregarEvento); bindForm('formPago', agregarPago); bindForm('formVestuario', agregarVestuario);
}

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

// --- CRUD USUARIOS ---
async function cargarUsuariosAdmin() {
    const res = await fetch(`${API_URL}/usuarios`); const data = await res.json();
    const tbody = document.getElementById('tablaUsuarios');
    const selectPago = document.getElementById('pagoUsuario');
    if(selectPago) {
        selectPago.innerHTML = '<option value="">Seleccionar Alumno...</option>';
        data.filter(u => u.rol === 'alumno').forEach(u => selectPago.innerHTML += `<option value="${u.id}">${u.nombre || u.username}</option>`);
    }
    if(tbody) {
        tbody.innerHTML = '';
        data.forEach((u, i) => {
            let detalles = u.rol;
            if(u.rol === 'alumno') detalles = `${u.nombre || ''} <br> <small>${u.nivel || ''}</small>`;
            tbody.innerHTML += `<tr class="animate-fade"><td><strong>${u.username}</strong></td><td>${u.rol}</td><td>${detalles}</td><td style="text-align:right"><button onclick="editarUsuario(${u.id}, '${u.username}', '${u.rol}', '${u.nombre||''}', '${u.telefono||''}', '${u.nivel||''}')" class="btn-edit"><span class="material-icons">edit</span></button><button onclick="borrarUsuario(${u.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`;
        });
    }
}
async function agregarUsuario(e) {
    e.preventDefault(); const id = document.getElementById('usuarioId').value;
    const data = { username: document.getElementById('usuarioUsername').value, rol: document.getElementById('usuarioRol').value, nombre: document.getElementById('usuarioNombre').value, telefono: document.getElementById('usuarioTelefono').value, nivel: document.getElementById('usuarioNivel').value };
    const pass = document.getElementById('usuarioPassword').value; if(pass) data.password = pass;
    if(id) await fetch(`${API_URL}/usuarios/${id}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
    else await genericPost(`${API_URL}/usuarios`, data);
    limpiarFormUsuario(); cargarUsuariosAdmin();
}
window.borrarUsuario=async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); cargarUsuariosAdmin(); }};
window.editarUsuario = function(id, user, rol, nombre, tel, nivel) { document.getElementById('usuarioId').value=id; document.getElementById('usuarioUsername').value=user; document.getElementById('usuarioRol').value=rol; document.getElementById('usuarioNombre').value=nombre; document.getElementById('usuarioTelefono').value=tel; document.getElementById('usuarioNivel').value=nivel; toggleCamposAlumno(); document.querySelector('#formUsuario button').innerHTML='Actualizar'; }
window.limpiarFormUsuario = function() { document.getElementById('formUsuario').reset(); document.getElementById('usuarioId').value=''; document.querySelector('#formUsuario button').innerHTML='Crear'; toggleCamposAlumno(); }
window.toggleCamposAlumno = function() { const r=document.getElementById('usuarioRol').value; document.querySelectorAll('.campo-alumno').forEach(c=>c.style.display=(r==='alumno')?'block':'none'); }

// --- OTROS CRUD ---
async function cargarPagosAdmin() { const res = await fetch(`${API_URL}/pagos`); const data = await res.json(); const tbody = document.getElementById('tablaPagos'); if(tbody) tbody.innerHTML = data.map(p => `<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
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
window.buscarAsistencia = async function() { const fecha=document.getElementById('fechaAsistencia').value; const res=await fetch(`${API_URL}/asistencia?fecha=${fecha}`); const data=await res.json(); const tbody=document.getElementById('tablaAsistencia'); tbody.innerHTML = data.map(item => `<tr><td>${item.nombre}</td><td>${item.nivel}</td><td style="text-align:center"><input type="checkbox" class="checkbox-asistencia" data-id="${item.id_usuario}" ${item.presente?'checked':''}></td></tr>`).join(''); }
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

async function cargarEventosAlumno(){ const c=document.getElementById('alumnoEventosContainer'); if(c){ const r=await fetch(`${API_URL}/eventos`); const d=await r.json(); c.innerHTML=d.map(ev=>`<div class="stat-card"><div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha}</p></div></div>`).join(''); } }
async function cargarVestuarioAlumno(){ const c=document.getElementById('alumnoVestuarioContainer'); if(c){ const r=await fetch(`${API_URL}/vestuario`); const d=await r.json(); c.innerHTML=d.map(v=>`<div class="stat-card" style="border-left:5px solid var(--accent)"><div><h4 style="margin:0">${v.nombre}</h4><p>${v.talla}</p></div></div>`).join(''); } }

// --- LOGIN & LANDING ---
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
        c.innerHTML = data.length ? data.map(ev => `<div class="event-card reveal"><div class="date"><span class="day">${ev.fecha.split(' ')[0]}</span></div><div class="details"><h4>${ev.titulo}</h4><p>${ev.lugar}</p></div></div>`).join('') : '<p>Próximamente...</p>';
    } catch(e){}
}
window.cerrarSesion = function() { if(confirm("¿Cerrar sesión?")) { localStorage.clear(); window.location.href='/'; } };

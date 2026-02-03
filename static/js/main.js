
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

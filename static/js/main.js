
const API_URL = '/api';
let usuarioRol = localStorage.getItem('usuario_rol');
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre') || 'Invitado';

document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
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
    const nameDisplay = document.getElementById('userNameDisplay');
    if(nameDisplay) nameDisplay.textContent = nombreUsuario;
    const roleDisplay = document.getElementById('userRoleDisplay');
    if(roleDisplay) roleDisplay.textContent = usuarioRol ? usuarioRol.toUpperCase() : 'USUARIO';

    // Ocultar todo
    document.querySelectorAll('.admin-section, .alumno-section').forEach(el => el.style.display = 'none');
    document.getElementById('adminMenu').style.display = 'none';
    document.getElementById('userMenu').style.display = 'none';

    // -- ADMIN --
    if (usuarioRol === 'admin') {
        mostrarMenu('adminMenu');
        // Admin ve todo
        ['nav-usuarios', 'nav-eventos', 'nav-pagos', 'nav-vestuario', 'nav-asistencia'].forEach(id => mostrarElemento(id));
        cargarTodoAdmin();
        mostrarSeccion('usuarios');
    } 
    // -- STAFF --
    else if (usuarioRol === 'staff' || usuarioRol === 'administrativo') {
        mostrarMenu('adminMenu');
        ocultarElemento('nav-usuarios'); ocultarElemento('nav-eventos');
        mostrarElemento('nav-pagos'); mostrarElemento('nav-vestuario'); mostrarElemento('nav-asistencia');
        
        cargarPagosAdmin(); cargarVestuarioAdmin();
        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('fechaAsistencia').value = hoy;
        
        bindForm('formPago', agregarPago); bindForm('formVestuario', agregarVestuario);
        mostrarSeccion('pagos');
    }
    // -- MAESTRO --
    else if (usuarioRol === 'maestro') {
        mostrarMenu('adminMenu');
        ocultarElemento('nav-usuarios'); ocultarElemento('nav-eventos'); ocultarElemento('nav-pagos');
        mostrarElemento('nav-vestuario'); mostrarElemento('nav-asistencia');
        cargarVestuarioAdmin();
        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('fechaAsistencia').value = hoy;
        bindForm('formVestuario', agregarVestuario);
        mostrarSeccion('asistencia');
    }
    // -- ALUMNO --
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
    
    // Llenar select de pagos solo con alumnos
    if(selectPago) {
        selectPago.innerHTML = '<option value="">Seleccionar Alumno...</option>';
        data.filter(u => u.rol === 'alumno').forEach(u => {
            selectPago.innerHTML += `<option value="${u.id}">${u.nombre || u.username}</option>`;
        });
    }

    if(tbody) {
        tbody.innerHTML = '';
        data.forEach((u, i) => {
            let detalles = u.rol;
            if(u.rol === 'alumno') detalles = `${u.nombre || ''} <br> <small>${u.nivel || ''}</small>`;
            tbody.innerHTML += `
            <tr class="animate-fade" style="animation-delay:${i*0.05}s">
                <td><strong>${u.username}</strong></td>
                <td><span class="badge badge-principiante" style="background:var(--azul-talavera)">${u.rol}</span></td>
                <td>${detalles}</td>
                <td style="text-align:right">
                    <button onclick="editarUsuario(${u.id}, '${u.username}', '${u.rol}', '${u.nombre||''}', '${u.telefono||''}', '${u.nivel||''}')" class="btn-edit"><span class="material-icons">edit</span></button>
                    <button onclick="borrarUsuario(${u.id})" class="btn-delete"><span class="material-icons">delete</span></button>
                </td>
            </tr>`;
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
window.borrarUsuario = async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/usuarios/${id}`, {method:'DELETE'}); cargarUsuariosAdmin(); }};
window.editarUsuario = function(id, user, rol, nombre, tel, nivel) { 
    document.getElementById('usuarioId').value=id; document.getElementById('usuarioUsername').value=user; 
    document.getElementById('usuarioRol').value=rol; document.getElementById('usuarioNombre').value=nombre; 
    document.getElementById('usuarioTelefono').value=tel; document.getElementById('usuarioNivel').value=nivel; 
    toggleCamposAlumno(); document.querySelector('#formUsuario button').innerHTML='Actualizar'; 
}
window.limpiarFormUsuario = function() { 
    document.getElementById('formUsuario').reset(); document.getElementById('usuarioId').value=''; 
    document.querySelector('#formUsuario button').innerHTML='Crear'; toggleCamposAlumno(); 
}

// --- OTROS CRUD ---
async function cargarPagosAdmin() {
    const res = await fetch(`${API_URL}/pagos`); const data = await res.json();
    const tbody = document.getElementById('tablaPagos');
    if(tbody) tbody.innerHTML = data.map(p => `<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join('');
}
async function agregarPago(e) { e.preventDefault(); await genericPost(`${API_URL}/pagos`, { usuario_id: document.getElementById('pagoUsuario').value, concepto: document.getElementById('pagoConcepto').value, monto: document.getElementById('pagoMonto').value }); document.getElementById('formPago').reset(); cargarPagosAdmin(); }
window.borrarPago = async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/pagos/${id}`, {method:'DELETE'}); cargarPagosAdmin(); }};

async function cargarEventosAdmin() { const res = await fetch(`${API_URL}/eventos`); const data = await res.json(); const tbody = document.getElementById('tablaEventos'); if(tbody) tbody.innerHTML = data.map(ev => `<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarEvento(e) { e.preventDefault(); await genericPost(`${API_URL}/eventos`, { titulo: document.getElementById('tituloEvento').value, fecha: document.getElementById('fechaEvento').value, lugar: document.getElementById('lugarEvento').value, hora: document.getElementById('horaEvento').value }); document.getElementById('formEvento').reset(); cargarEventosAdmin(); }
window.borrarEvento = async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/eventos/${id}`, {method:'DELETE'}); cargarEventosAdmin(); }};

async function cargarVestuarioAdmin() { const res = await fetch(`${API_URL}/vestuario`); const data = await res.json(); const tbody = document.getElementById('tablaVestuario'); if(tbody) tbody.innerHTML = data.map(v => `<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`).join(''); }
async function agregarVestuario(e) { e.preventDefault(); await genericPost(`${API_URL}/vestuario`, { nombre: document.getElementById('vestuarioNombre').value, tipo: document.getElementById('vestuarioTipo').value, cantidad: document.getElementById('vestuarioCantidad').value, talla: document.getElementById('vestuarioTalla').value, estado: document.getElementById('vestuarioEstado').value }); document.getElementById('formVestuario').reset(); cargarVestuarioAdmin(); }
window.borrarVestuario = async(id)=>{ if(confirm("¿Borrar?")){ await fetch(`${API_URL}/vestuario/${id}`, {method:'DELETE'}); cargarVestuarioAdmin(); }};

async function genericPost(url, data) { try { await fetch(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); return true; } catch(e){ return false; } }

// --- ASISTENCIA ---
window.buscarAsistencia = async function() {
    const fecha = document.getElementById('fechaAsistencia').value;
    const res = await fetch(`${API_URL}/asistencia?fecha=${fecha}`);
    const data = await res.json();
    const tbody = document.getElementById('tablaAsistencia');
    tbody.innerHTML = '';
    data.forEach(item => {
        const checked = item.presente ? 'checked' : '';
        tbody.innerHTML += `<tr><td>${item.nombre}</td><td>${item.nivel || '-'}</td><td style="text-align:center"><input type="checkbox" class="checkbox-asistencia" data-id="${item.id_usuario}" ${checked}></td></tr>`;
    });
}
window.guardarAsistencia = async function() {
    const fecha = document.getElementById('fechaAsistencia').value;
    const checkboxes = document.querySelectorAll('.checkbox-asistencia');
    const registros = [];
    checkboxes.forEach(cb => { registros.push({ id_usuario: cb.dataset.id, presente: cb.checked }); });
    await genericPost(`${API_URL}/asistencia`, { fecha: fecha, registros: registros });
    alert("Asistencia Guardada");
}

// --- ALUMNO ---
async function registrarMiAsistencia() {
    const btn = document.getElementById('btnMarcarAsistencia');
    btn.disabled = true; btn.innerText = "Registrando...";
    try {
        const resU = await fetch(`${API_URL}/usuarios?rol=alumno`);
        const usuarios = await resU.json();
        const yo = usuarios.find(u => u.username === nombreUsuario);
        if(!yo) { alert("Error de usuario"); btn.disabled = false; return; }
        const hoy = new Date().toISOString().split('T')[0];
        await fetch(`${API_URL}/asistencia`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ fecha: hoy, id_usuario: yo.id }) });
        alert("¡Listo!"); btn.innerText = "Marcado";
    } catch(e) { alert("Error"); btn.disabled = false; }
}
async function cargarEventosAlumno() {
    const res = await fetch(`${API_URL}/eventos`); const data = await res.json();
    const c = document.getElementById('alumnoEventosContainer');
    if(c) { c.innerHTML=''; data.forEach(ev => c.innerHTML += `<div class="stat-card"><div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha}</p></div></div>`); }
}
async function cargarVestuarioAlumno() {
    const res = await fetch(`${API_URL}/vestuario`); const data = await res.json();
    const c = document.getElementById('alumnoVestuarioContainer');
    if(c) { c.innerHTML=''; data.forEach(v => c.innerHTML += `<div class="stat-card" style="border-left:5px solid var(--accent)"><div><h4 style="margin:0">${v.nombre}</h4><p>${v.talla}</p></div></div>`); }
}

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
                    localStorage.setItem('usuario_logueado', 'true'); localStorage.setItem('usuario_rol', data.rol); localStorage.setItem('es_admin', data.es_admin); localStorage.setItem('usuario_nombre', data.nombre);
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
        c.innerHTML = '';
        data.forEach(ev => c.innerHTML += `<div class="event-card reveal"><div class="date"><span class="day">${ev.fecha.split(' ')[0]}</span></div><div class="details"><h4>${ev.titulo}</h4><p>${ev.lugar}</p></div></div>`);
    } catch(e){}
}
window.cerrarSesion = function() { if(confirm("¿Cerrar sesión?")) { localStorage.clear(); window.location.href='/'; } };

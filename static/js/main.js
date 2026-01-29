const API_URL = '/api';

// --- ESTADO GLOBAL ---
let esAdmin = localStorage.getItem('es_admin') === 'true';
let usuarioLogueado = localStorage.getItem('usuario_logueado') === 'true';
let nombreUsuario = localStorage.getItem('usuario_nombre') || 'Invitado';
let usuarioRol = localStorage.getItem('usuario_rol');

/* =========================================
   INICIALIZACIÓN (EVENTOS DOM)
   ========================================= */
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. INICIALIZAR INTERFAZ LANDING (BOTÓN ACCESO Y MODAL)
    // Esto arregla el problema del botón que no hacía nada
    const modal = document.getElementById("loginModal");
    const btnAuth = document.getElementById("btnAuth");
    const spanClose = document.getElementById("closeModal") || document.querySelector(".close-btn"); // Soporte para ambos IDs
    const loginForm = document.getElementById('universalLoginForm');

    // Botón Acceso (Header)
    if (btnAuth) {
        // Actualizar texto si ya está logueado
        if (usuarioLogueado) {
            btnAuth.innerHTML = '<span class="material-icons">logout</span> Salir';
            btnAuth.addEventListener('click', cerrarSesion);
            
            // Mostrar botón de panel si es admin/staff
            const btnPanel = document.getElementById('nav-admin-panel');
            if(btnPanel) {
                btnPanel.style.display = 'block';
                // Si es alumno, cambiar texto a "Mi Perfil"
                if(usuarioRol !== 'admin' && usuarioRol !== 'administrativo' && usuarioRol !== 'maestro') {
                    const link = btnPanel.querySelector('a');
                    if(link) link.innerHTML = '<span class="material-icons" style="font-size:16px;">person</span> MI PERFIL';
                }
            }
        } else {
            // Si no está logueado, abrir modal
            btnAuth.addEventListener('click', (e) => {
                e.preventDefault(); // Prevenir salto de ancla
                if (modal) modal.style.display = "block";
            });
        }
    }

    // Cerrar Modal
    if (spanClose && modal) {
        spanClose.onclick = () => { modal.style.display = "none"; };
    }
    window.onclick = (event) => {
        if (modal && event.target == modal) { modal.style.display = "none"; }
    };

    // Formulario Login
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('loginMessage');
            if(msg) msg.textContent = "Verificando...";

            try {
                const res = await fetch(`${API_URL}/login`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        usuario: document.getElementById('loginUser').value,
                        password: document.getElementById('loginPass').value
                    })
                });
                const data = await res.json();
                
                if (data.success) {
                    if(msg) { msg.style.color = 'var(--verde-agave)'; msg.textContent = "¡Bienvenido!"; }
                    
                    // Guardar sesión
                    localStorage.setItem('usuario_logueado', 'true');
                    localStorage.setItem('usuario_rol', data.rol);
                    localStorage.setItem('es_admin', data.es_admin);
                    localStorage.setItem('usuario_nombre', data.mensaje.split(' ')[1]);
                    
                    // Redirección
                    setTimeout(() => window.location.href = '/dashboard', 800);
                } else {
                    if(msg) { msg.style.color = 'red'; msg.textContent = data.mensaje; }
                }
            } catch (err) {
                if(msg) msg.textContent = "Error de conexión";
            }
        });
    }

    // 2. CARGAR EVENTOS EN LANDING (Si existe el contenedor)
    if (document.getElementById('eventsContainer')) {
        cargarEventosLanding();
        
        // Animaciones Scroll (Solo en Landing)
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    }

    // 3. INICIALIZAR DASHBOARD (Si estamos en el panel)
    if (document.querySelector('.dashboard-layout')) {
        configurarDashboard();
    }
});

/* =========================================
   DASHBOARD: LÓGICA DE NEGOCIO Y ROLES
   ========================================= */
function configurarDashboard() {
    if (!usuarioLogueado) { window.location.href = '/'; return; }

    const nameDisplay = document.getElementById('userNameDisplay');
    const roleDisplay = document.getElementById('userRoleDisplay');
    const welcome = document.getElementById('welcomeTitle');
    
    if(nameDisplay) nameDisplay.textContent = nombreUsuario;
    if(welcome) welcome.textContent = `¡Hola, ${nombreUsuario}!`;

    // Ocultar menús inicialmente
    document.getElementById('adminMenu').style.display = 'none';
    document.getElementById('userMenu').style.display = 'none';

    if (esAdmin) { // Admin, Administrativo o Maestro
        document.getElementById('adminMenu').style.display = 'block';
        
        // Cargar fecha hoy para asistencia
        const hoy = new Date().toISOString().split('T')[0];
        const dateInput = document.getElementById('fechaAsistencia');
        if(dateInput) dateInput.value = hoy;

        // Bindeo general de formularios
        bindForm('formBailarin', agregarBailarin);
        bindForm('formEvento', agregarEvento);
        bindForm('formPago', agregarPago);
        bindForm('formUsuario', agregarUsuario);
        bindForm('formVestuario', agregarVestuario);

        // LÓGICA ESPECÍFICA POR ROL DE STAFF
        if (usuarioRol === 'admin') {
            if(roleDisplay) roleDisplay.textContent = 'Director General';
            mostrarTodoAdmin();
            mostrarSeccion('bailarines');
        } 
        else if (usuarioRol === 'administrativo') {
            if(roleDisplay) roleDisplay.textContent = 'Administrativo';
            // Ocultar opciones no permitidas
            ocultarOpcionMenu('nav-bailarines');
            ocultarOpcionMenu('nav-eventos');
            ocultarOpcionMenu('nav-usuarios');
            
            cargarPagosAdmin();
            cargarVestuarioAdmin();
            mostrarSeccion('pagos');
        }
        else if (usuarioRol === 'maestro') {
            if(roleDisplay) roleDisplay.textContent = 'Maestro';
            // Ocultar opciones no permitidas
            ocultarOpcionMenu('nav-bailarines');
            ocultarOpcionMenu('nav-eventos');
            ocultarOpcionMenu('nav-pagos');
            ocultarOpcionMenu('nav-usuarios');
            
            cargarVestuarioAdmin();
            mostrarSeccion('asistencia');
        }

    } else {
        // MODO ALUMNO
        document.getElementById('userMenu').style.display = 'block';
        if(roleDisplay) roleDisplay.textContent = 'Bailarín';
        
        const userWelcome = document.getElementById('userWelcomeName');
        if(userWelcome) userWelcome.textContent = `¡Hola, ${nombreUsuario}!`;
        
        // Eliminar secciones de admin para limpieza
        document.querySelectorAll('.admin-section').forEach(el => el.remove());
        
        cargarEventosAlumno();
        cargarVestuarioAlumno();
        mostrarSeccion('alumno-asistencia');
    }
}

function mostrarTodoAdmin() {
    cargarBailarinesAdmin();
    cargarEventosAdmin();
    cargarPagosAdmin();
    cargarUsuariosAdmin();
    cargarVestuarioAdmin();
}

function ocultarOpcionMenu(id) {
    const el = document.getElementById(id);
    if(el) el.style.display = 'none';
}

function bindForm(id, handler) {
    const form = document.getElementById(id);
    if(form) form.addEventListener('submit', handler);
}

// Navegación Pestañas Dashboard
window.mostrarSeccion = function(seccion) {
    document.querySelectorAll('.admin-section, .alumno-section').forEach(el => {
        el.style.display = 'none';
        el.classList.remove('active');
    });
    document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));

    const target = document.getElementById(`section-${seccion}`);
    const nav = document.getElementById(`nav-${seccion}`);
    
    if(target) {
        target.style.display = 'block';
        setTimeout(() => target.classList.add('active'), 10);
    }
    if(nav) nav.classList.add('active');
    
    const titleEl = document.getElementById('pageTitle');
    if(titleEl) titleEl.textContent = seccion.replace('alumno-', '').toUpperCase();
}

/* =========================================
   FUNCIONES CRUD (ADMINISTRACIÓN)
   ========================================= */

// 1. BAILARINES
async function cargarBailarinesAdmin() {
    try {
        const res = await fetch(`${API_URL}/bailarines`);
        const data = await res.json();
        const tbody = document.getElementById('tablaBailarines');
        const stat = document.getElementById('statBailarines');
        const select = document.getElementById('pagoBailarin'); // Llenar select de pagos

        if(stat) stat.textContent = data.length;
        
        if(select) { 
            select.innerHTML='<option value="">Seleccionar...</option>'; 
            data.forEach(b => select.innerHTML+=`<option value="${b.nombre}">${b.nombre}</option>`); 
        }

        if(tbody) {
            tbody.innerHTML = '';
            data.forEach((b, i) => {
                let badge = 'badge-principiante';
                if(b.nivel === 'Intermedio') badge = 'badge-intermedio';
                if(b.nivel === 'Avanzado') badge = 'badge-avanzado';

                tbody.innerHTML += `
                    <tr class="animate-fade" style="animation-delay: ${i*0.05}s">
                        <td><strong>${b.nombre}</strong></td>
                        <td><span class="badge ${badge}" style="background:var(--azul-talavera); color:white; padding:4px 8px; border-radius:12px;">${b.nivel || 'N/A'}</span></td>
                        <td>${b.contacto || '--'}</td>
                        <td style="text-align: right;">
                            <button onclick="borrarBailarin(${b.id})" class="btn-delete"><span class="material-icons">delete</span></button>
                        </td>
                    </tr>`;
            });
        }
    } catch(e){}
}

async function agregarBailarin(e) {
    e.preventDefault();
    await genericPost(`${API_URL}/bailarines`, {
        nombre: document.getElementById('nombreBailarin').value,
        nivel: document.getElementById('nivelBailarin').value,
        contacto: document.getElementById('contactoBailarin').value
    });
    document.getElementById('formBailarin').reset();
    cargarBailarinesAdmin();
}

window.borrarBailarin = async (id) => {
    if(confirm("¿Borrar alumno?")) { await fetch(`${API_URL}/bailarines/${id}`, { method: 'DELETE' }); cargarBailarinesAdmin(); }
};

// 2. EVENTOS
async function cargarEventosAdmin() {
    const res = await fetch(`${API_URL}/eventos`);
    const data = await res.json();
    const tbody = document.getElementById('tablaEventos');
    const stat = document.getElementById('statEventos');
    if(stat) stat.textContent = data.length;
    if(tbody) {
        tbody.innerHTML = '';
        data.forEach(ev => {
            tbody.innerHTML += `<tr><td>${ev.titulo}</td><td>${ev.fecha}</td><td>${ev.lugar}</td><td style="text-align:right"><button onclick="borrarEvento(${ev.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`;
        });
    }
}
async function agregarEvento(e) {
    e.preventDefault();
    await genericPost(`${API_URL}/eventos`, {
        titulo: document.getElementById('tituloEvento').value,
        fecha: document.getElementById('fechaEvento').value,
        lugar: document.getElementById('lugarEvento').value,
        hora: document.getElementById('horaEvento').value
    });
    document.getElementById('formEvento').reset();
    cargarEventosAdmin();
}
window.borrarEvento = async (id) => { if(confirm("¿Borrar?")) { await fetch(`${API_URL}/eventos/${id}`, { method: 'DELETE' }); cargarEventosAdmin(); } };

// 3. PAGOS
async function cargarPagosAdmin() {
    const res = await fetch(`${API_URL}/pagos`);
    const data = await res.json();
    const tbody = document.getElementById('tablaPagos');
    const total = data.reduce((sum, p) => sum + (p.monto || 0), 0);
    const stat = document.getElementById('statPagos');
    if(stat) stat.textContent = `$${total.toLocaleString()}`;
    if(tbody) {
        tbody.innerHTML = '';
        data.forEach(p => {
            tbody.innerHTML += `<tr><td>${p.bailarin}</td><td>${p.concepto}</td><td>$${p.monto}</td><td style="text-align:right"><button onclick="borrarPago(${p.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`;
        });
    }
}
async function agregarPago(e) {
    e.preventDefault();
    await genericPost(`${API_URL}/pagos`, {
        bailarin: document.getElementById('pagoBailarin').value,
        concepto: document.getElementById('pagoConcepto').value,
        monto: document.getElementById('pagoMonto').value
    });
    document.getElementById('formPago').reset();
    cargarPagosAdmin();
}
window.borrarPago = async (id) => { if(confirm("¿Borrar?")) { await fetch(`${API_URL}/pagos/${id}`, { method: 'DELETE' }); cargarPagosAdmin(); } };

// 4. VESTUARIO
async function cargarVestuarioAdmin() {
    const res = await fetch(`${API_URL}/vestuario`);
    const data = await res.json();
    const tbody = document.getElementById('tablaVestuario');
    if(tbody) {
        tbody.innerHTML = '';
        data.forEach(v => {
            tbody.innerHTML += `<tr><td>${v.nombre}</td><td>${v.tipo}</td><td>${v.cantidad}</td><td>${v.talla}</td><td>${v.estado}</td><td style="text-align:right"><button onclick="borrarVestuario(${v.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`;
        });
    }
}
async function agregarVestuario(e) {
    e.preventDefault();
    await genericPost(`${API_URL}/vestuario`, {
        nombre: document.getElementById('vestuarioNombre').value,
        tipo: document.getElementById('vestuarioTipo').value,
        cantidad: document.getElementById('vestuarioCantidad').value,
        talla: document.getElementById('vestuarioTalla').value,
        estado: document.getElementById('vestuarioEstado').value
    });
    document.getElementById('formVestuario').reset();
    cargarVestuarioAdmin();
}
window.borrarVestuario = async (id) => { if(confirm("¿Borrar?")) { await fetch(`${API_URL}/vestuario/${id}`, { method: 'DELETE' }); cargarVestuarioAdmin(); } };

// 5. USUARIOS
async function cargarUsuariosAdmin() {
    const res = await fetch(`${API_URL}/usuarios`);
    const data = await res.json();
    const tbody = document.getElementById('tablaUsuarios');
    if(tbody) {
        tbody.innerHTML = '';
        data.forEach(u => {
            tbody.innerHTML += `<tr><td>${u.username}</td><td>${u.rol}</td><td style="text-align:right"><button onclick="editarUsuario(${u.id}, '${u.username}', '${u.rol}')" class="btn-edit"><span class="material-icons">edit</span></button><button onclick="borrarUsuario(${u.id})" class="btn-delete"><span class="material-icons">delete</span></button></td></tr>`;
        });
    }
}
async function agregarUsuario(e) {
    e.preventDefault();
    const id = document.getElementById('usuarioId').value;
    const data = { 
        username: document.getElementById('usuarioUsername').value, 
        rol: document.getElementById('usuarioRol').value 
    };
    const pass = document.getElementById('usuarioPassword').value;
    if(pass) data.password = pass;

    if (id) {
        await fetch(`${API_URL}/usuarios/${id}`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    } else {
        await genericPost(`${API_URL}/usuarios`, data);
    }
    limpiarFormUsuario();
    cargarUsuariosAdmin();
}
window.borrarUsuario = async (id) => { if(confirm("¿Borrar?")) { await fetch(`${API_URL}/usuarios/${id}`, { method: 'DELETE' }); cargarUsuariosAdmin(); } };
window.editarUsuario = function(id, user, rol) {
    document.getElementById('usuarioId').value = id;
    document.getElementById('usuarioUsername').value = user;
    document.getElementById('usuarioRol').value = rol;
    document.querySelector('#formUsuario button').innerHTML = '<span class="material-icons">save</span> Actualizar';
}
window.limpiarFormUsuario = function() {
    document.getElementById('formUsuario').reset();
    document.getElementById('usuarioId').value = '';
    document.querySelector('#formUsuario button').innerHTML = '<span class="material-icons">person_add</span> Crear';
}

// 6. ASISTENCIA ADMIN
window.buscarAsistencia = async function() {
    const fecha = document.getElementById('fechaAsistencia').value;
    const res = await fetch(`${API_URL}/asistencia?fecha=${fecha}`);
    const data = await res.json();
    const tbody = document.getElementById('tablaAsistencia');
    tbody.innerHTML = '';
    data.forEach(item => {
        const checked = item.presente ? 'checked' : '';
        tbody.innerHTML += `<tr><td>${item.nombre}</td><td>${item.nivel}</td><td style="text-align:center"><input type="checkbox" class="checkbox-asistencia" data-id="${item.id_bailarin}" ${checked}></td></tr>`;
    });
}
window.guardarAsistencia = async function() {
    const fecha = document.getElementById('fechaAsistencia').value;
    const checkboxes = document.querySelectorAll('.checkbox-asistencia');
    const registros = [];
    checkboxes.forEach(cb => { registros.push({ id_bailarin: cb.dataset.id, presente: cb.checked }); });
    await genericPost(`${API_URL}/asistencia`, { fecha: fecha, registros: registros });
    alert("Asistencia Guardada");
}


// =========================================
// FUNCIONES DE ALUMNO
// =========================================
async function registrarMiAsistencia() {
    const btn = document.getElementById('btnMarcarAsistencia');
    btn.disabled = true; btn.innerText = "Registrando...";
    try {
        // Buscar ID del bailarín por nombre de usuario
        const resB = await fetch(`${API_URL}/bailarines`);
        const bailarines = await resB.json();
        const yo = bailarines.find(b => b.nombre.toLowerCase() === nombreUsuario.toLowerCase());
        
        if (!yo) { 
            alert("No se encontró tu registro de alumno. Verifica con el director."); 
            btn.disabled = false; btn.innerText = "Reintentar"; return; 
        }
        
        const hoy = new Date().toISOString().split('T')[0];
        await fetch(`${API_URL}/asistencia`, { 
            method: 'POST', headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify({ fecha: hoy, id_bailarin: yo.id }) 
        });
        
        alert("¡Asistencia registrada!"); 
        btn.innerText = "¡Asistencia Marcada!";
        btn.style.backgroundColor = "var(--verde-agave)";
    } catch (e) { alert("Error"); btn.disabled = false; }
}

async function cargarEventosAlumno() {
    const res = await fetch(`${API_URL}/eventos`);
    const data = await res.json();
    const c = document.getElementById('alumnoEventosContainer');
    if(c) { 
        c.innerHTML=''; 
        if(data.length === 0) c.innerHTML = '<p>No hay eventos próximos.</p>';
        data.forEach(ev => c.innerHTML += `
            <div class="stat-card" style="margin-bottom:15px; align-items:flex-start;">
                <div class="stat-icon"><span class="material-icons">event</span></div>
                <div><h4 style="margin:0;color:var(--primary)">${ev.titulo}</h4><p>${ev.fecha} - ${ev.lugar}</p></div>
            </div>`); 
    }
}

async function cargarVestuarioAlumno() {
    const res = await fetch(`${API_URL}/vestuario`);
    const data = await res.json();
    const c = document.getElementById('alumnoVestuarioContainer');
    if(c) { 
        c.innerHTML=''; 
        if(data.length === 0) c.innerHTML = '<p>No hay vestuario registrado.</p>';
        data.forEach(v => c.innerHTML += `
            <div class="stat-card" style="margin-bottom:15px; border-left:5px solid var(--accent);">
                <div><h4 style="margin:0">${v.nombre}</h4><p>${v.tipo} | Talla: ${v.talla}</p></div>
            </div>`); 
    }
}

// =========================================
// FUNCIONES GENERALES
// =========================================
async function genericPost(url, data) {
    try {
        await fetch(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
        return true;
    } catch(e) { return false; }
}

async function cargarEventosLanding() {
    const container = document.getElementById('eventsContainer');
    if(!container) return;
    try {
        const res = await fetch(`${API_URL}/eventos`);
        const data = await res.json();
        container.innerHTML = '';
        if(data.length === 0) container.innerHTML = '<p style="color:white; opacity:0.8">Próximamente...</p>';
        data.forEach((ev, i) => {
            const [dia, mes] = ev.fecha.split(' ');
            container.innerHTML += `
                <div class="event-card reveal" style="transition-delay: ${i*0.1}s">
                    <div class="date"><span class="day">${dia||''}</span><span class="month">${mes||''}</span></div>
                    <div class="details"><h4>${ev.titulo}</h4><p>${ev.lugar}</p></div>
                </div>`;
        });
    } catch(e) {}
}

window.cerrarSesion = function() {
    if(confirm("¿Cerrar sesión?")) { localStorage.clear(); window.location.href='/'; }
};
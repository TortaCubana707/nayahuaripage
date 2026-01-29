import os

# 1. HTML COMPLETO CON LANDING PAGE Y MODAL
contenido_index = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nayahuari | Ballet Folklórico</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}">
</head>
<body>
    <!-- Línea decorativa superior -->
    <div class="zarape-line"></div>
    
    <nav class="navbar">
        <div class="logo">
            <span style="font-size: 0.7rem; letter-spacing: 2px;">BALLET FOLKLÓRICO</span><br>
            <strong style="color: var(--amarillo-cempasuchil); font-size: 1.5rem;">NAYAHUARI</strong>
        </div>
        
        <div class="nav-links">
            <a href="#inicio">Inicio</a>
            <a href="#nosotros">Nosotros</a>
            <a href="#agenda">Agenda</a>
            <button id="btnAuth" class="btn-login">
                <span class="material-icons">login</span> Acceso
            </button>
        </div>
    </nav>

    <main>
        <!-- SECCIÓN HERO -->
        <section id="inicio" class="hero">
            <div class="hero-content">
                <h3 style="color: var(--rosa-mexicano); letter-spacing: 5px; text-transform: uppercase;">Orgullo y Tradición</h3>
                <h1 style="font-size: 4rem; line-height: 1; margin: 1rem 0;">MÉXICO EN EL <br><span style="color:var(--amarillo-cempasuchil)">CORAZÓN</span></h1>
                <p style="margin-bottom: 2rem; font-size: 1.2rem; opacity: 0.9;">Compañía de Danza Folklórica Mexicana</p>
                <button class="btn-primary" onclick="document.getElementById('agenda').scrollIntoView({behavior: 'smooth'})">Ver Presentaciones</button>
            </div>
        </section>

        <!-- SECCIÓN NOSOTROS -->
        <section id="nosotros" style="padding: 100px 5%;">
            <div class="container" style="display: grid; grid-template-columns: 1fr 1fr; gap: 50px; align-items: center;">
                <div>
                    <div style="width: 100%; height: 400px; background: #ddd; border-radius: 20px; position: relative; overflow: hidden; box-shadow: 20px 20px 0 var(--rosa-mexicano);">
                        <img src="https://images.unsplash.com/photo-1504196606672-aef5c9cefc92?q=80&w=1000" alt="Ballet" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                </div>
                <div>
                    <h2 style="font-size: 3rem; color: var(--azul-noche); margin-bottom: 1.5rem;">Nuestra <span style="color: var(--rosa-mexicano);">Esencia</span></h2>
                    <p style="font-size: 1.1rem; line-height: 1.8; color: #555;">Nayahuari nace de la pasión por nuestras raíces, llevando el color y la fuerza de México a cada escenario del mundo. Somos una familia dedicada a preservar el arte del zapateado y el color de nuestros trajes típicos.</p>
                    
                    <div style="margin-top: 2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div style="padding: 20px; background: white; border-radius: 15px; border-left: 5px solid var(--azul-talavera); box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                            <h4 style="color: var(--azul-talavera); margin:0;">+15 Años</h4>
                            <p style="margin:0; font-size: 0.9rem;">De trayectoria artística.</p>
                        </div>
                        <div style="padding: 20px; background: white; border-radius: 15px; border-left: 5px solid var(--rosa-mexicano); box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                            <h4 style="color: var(--rosa-mexicano); margin:0;">+50 Danzas</h4>
                            <p style="margin:0; font-size: 0.9rem;">En nuestro repertorio.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECCIÓN AGENDA -->
        <section id="agenda" style="padding: 100px 5%; background: #fdfaf5;">
            <div style="text-align: center; margin-bottom: 4rem;">
                <h2 style="font-size: 3rem; color: var(--azul-noche);">Próximas <span style="color: var(--amarillo-cempasuchil);">Galas</span></h2>
                <p>Acompáñanos en nuestras siguientes presentaciones</p>
            </div>
            <div id="eventsContainer" class="calendar-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px;">
                <!-- Se carga vía JavaScript -->
            </div>
        </section>
    </main>

    <!-- MODAL DE LOGIN -->
    <div id="loginModal" class="modal" style="display:none; position:fixed; z-index:9999; left:0; top:0; width:100%; height:100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px);">
        <div class="modal-content" style="background:white; margin: 10% auto; padding: 40px; border-radius: 20px; width: 90%; max-width: 400px; position: relative;">
            <span class="close-btn" id="closeModal" style="position:absolute; right:20px; top:15px; font-size: 2rem; cursor:pointer;">&times;</span>
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: var(--azul-noche); margin:0;">Iniciar Sesión</h2>
                <p style="color: #666; font-size: 0.9rem;">Acceso para integrantes y staff</p>
            </div>
            <form id="universalLoginForm">
                <div style="margin-bottom: 15px;">
                    <input type="text" id="loginUser" placeholder="Usuario" required style="width:100%; padding:12px; border:1px solid #ddd; border-radius:8px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <input type="password" id="loginPass" placeholder="Contraseña" required style="width:100%; padding:12px; border:1px solid #ddd; border-radius:8px;">
                </div>
                <p id="loginMessage" style="color: red; font-size: 0.8rem; text-align: center; margin-bottom: 10px;"></p>
                <button type="submit" class="btn-primary" style="width: 100%; padding: 15px; border:none; border-radius:8px; background: var(--rosa-mexicano); color:white; font-weight:bold; cursor:pointer;">Entrar al Panel</button>
            </form>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""

# 2. JS REPARADO (CONTROL DEL MODAL Y EVENTOS)
contenido_js = """
document.addEventListener('DOMContentLoaded', () => {
    // Referencias
    const modal = document.getElementById("loginModal");
    const btnAuth = document.getElementById("btnAuth");
    const spanClose = document.getElementById("closeModal");
    const loginForm = document.getElementById('universalLoginForm');

    // 1. FUNCIONAMIENTO DEL BOTÓN ACCESO
    if (btnAuth) {
        btnAuth.addEventListener('click', () => {
            console.log("Abriendo modal...");
            if (localStorage.getItem('usuario_logueado') === 'true') {
                window.location.href = '/dashboard';
            } else {
                modal.style.display = "block";
            }
        });
    }

    // 2. CERRAR MODAL
    if (spanClose) {
        spanClose.onclick = () => { modal.style.display = "none"; };
    }
    window.onclick = (event) => {
        if (event.target == modal) { modal.style.display = "none"; }
    };

    // 3. LOGIN AJAX
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = document.getElementById('loginMessage');
            msg.textContent = "Verificando...";

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        usuario: document.getElementById('loginUser').value,
                        password: document.getElementById('loginPass').value
                    })
                });
                const data = await res.json();
                
                if (data.success) {
                    localStorage.setItem('usuario_logueado', 'true');
                    localStorage.setItem('usuario_rol', data.rol);
                    localStorage.setItem('usuario_nombre', data.mensaje.split(' ')[1]);
                    window.location.href = '/dashboard';
                } else {
                    msg.textContent = data.mensaje || "Credenciales incorrectas";
                }
            } catch (err) {
                msg.textContent = "Error de conexión";
            }
        });
    }

    // 4. CARGAR EVENTOS AUTOMÁTICAMENTE
    cargarEventosLanding();
});

async function cargarEventosLanding() {
    const container = document.getElementById('eventsContainer');
    if (!container) return;
    
    try {
        const res = await fetch('/api/eventos');
        const data = await res.json();
        
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No hay eventos próximos registrados.</p>';
            return;
        }

        container.innerHTML = data.map(ev => `
            <div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-top: 5px solid var(--amarillo-cempasuchil);">
                <div style="color: var(--rosa-mexicano); font-weight: bold; font-size: 0.8rem; margin-bottom: 10px; text-transform: uppercase;">Próximamente</div>
                <h3 style="margin: 0 0 10px 0; color: var(--azul-noche);">${ev.titulo}</h3>
                <p style="color: #666; font-size: 0.9rem;"><span class="material-icons" style="font-size:14px; vertical-align:middle">place</span> ${ev.lugar}</p>
                <div style="margin-top: 15px; font-weight: bold; color: var(--azul-talavera);">${ev.fecha}</div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<p>Error al conectar con la agenda.</p>';
    }
}
"""

# EJECUCIÓN
print("🛠️ Restaurando Landing Page completa...")
with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(contenido_index)

with open("static/js/main.js", "w", encoding="utf-8") as f:
    f.write(contenido_js)

print("✅ Todo restaurado y botón reparado.")
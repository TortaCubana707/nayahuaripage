import os

print("\n--- 🔍 DIAGNÓSTICO DE ARCHIVOS ---")
base_dir = os.getcwd()
print(f"📍 Carpeta del proyecto: {base_dir}\n")

archivos_necesarios = [
    "app.py",
    ".env",
    "database/mi_app.sqlite",
    "templates/index.html",
    "templates/dashboard.html",
    "static/css/estilos.css",  # OJO AQUÍ
    "static/js/main.js"        # OJO AQUÍ
]

todo_bien = True

for archivo in archivos_necesarios:
    ruta_completa = os.path.join(base_dir, archivo)
    # Normalizamos la ruta para que funcione bien en Windows
    ruta_completa = os.path.normpath(ruta_completa)
    
    if os.path.exists(ruta_completa):
        print(f"✅ [OK] Encontrado: {archivo}")
    else:
        print(f"❌ [ERROR] FALTA: {archivo}")
        print(f"   (Buscaba en: {ruta_completa})")
        todo_bien = False

print("\n" + "="*30)
if todo_bien:
    print("🎉 La estructura de carpetas es PERFECTA.")
    print("El problema es 100% del navegador o del servidor.")
else:
    print("⚠️ FALTAN ARCHIVOS o están en carpetas incorrectas.")
    print("Revisa las líneas con ❌ y muévelos a la carpeta correcta.")
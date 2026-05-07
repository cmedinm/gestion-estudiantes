INSTRUCCIONES PARA EJECUTAR LA APLICACIÓN
==========================================

REQUISITOS PREVIOS:
- Python 3.x instalado
- MySQL instalado y corriendo
- MySQL Workbench (opcional, para ver la base de datos)

PASOS:

1. IMPORTAR LA BASE DE DATOS
   - Abrir MySQL Workbench
   - Ir a Server → Data Import
   - Seleccionar "Import from Self-Contained File"
   - Seleccionar el archivo: gestion_estudiantes.sql
   - Hacer clic en "Start Import"

2. CONFIGURAR CONTRASEÑA MySQL
   - Abrir el archivo app.py
   - Buscar la función get_db()
   - Cambiar el campo password='' por su contraseña de MySQL

3. INSTALAR DEPENDENCIAS
   - Abrir terminal en la carpeta del proyecto
   - Ejecutar: pip install -r requirements.txt

4. EJECUTAR LA APLICACIÓN
   - En la terminal ejecutar: python app.py
   - Abrir navegador en: http://127.0.0.1:5000

TECNOLOGÍAS USADAS:
- Python + Flask (Backend)
- MySQL (Base de datos)
- HTML + CSS + JavaScript (Frontend)
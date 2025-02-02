import streamlit as st
import sqlite3
import pathlib
from datetime import datetime,timedelta
import pandas as pd
import calendar
from PIL import Image

from login import login_required, logout

#CARGAR IMAGEN
img = Image.open('./img/KENTI-SOLO.png')
#FUNCION PARA PONER LA FOTO

st.set_page_config(page_title='Consultorio', page_icon=img)

# Función para cargar CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargar CSS si es necesario
css_path = pathlib.Path("estilo.css")
load_css(css_path)


def obtener_estadisticas_sesiones(paciente_id):
    """
    Obtiene estadísticas de sesiones para un paciente específico
    """
    cursor.execute('''
    SELECT 
        COUNT(*) as total_sesiones,
        SUM(CASE WHEN pago = 1 THEN 1 ELSE 0 END) as sesiones_pagadas,
        SUM(CASE WHEN asistio = 1 THEN 1 ELSE 0 END) as sesiones_asistidas,
        SUM(CASE WHEN pago = 0 THEN monto ELSE 0 END) as deuda_total
    FROM sesiones 
    WHERE paciente_id = ?
    ''', (paciente_id,))
    
    result = cursor.fetchone()
    return {
        'total_sesiones': result[0],
        'sesiones_pagadas': result[1] or 0,
        'sesiones_asistidas': result[2] or 0,
        'deuda_total': result[3] or 0
    }

def obtener_ultima_sesion(paciente_id):
    """
    Obtiene la fecha de la última sesión del paciente
    """
    cursor.execute('''
    SELECT fecha 
    FROM sesiones 
    WHERE paciente_id = ? 
    ORDER BY fecha DESC 
    LIMIT 1
    ''', (paciente_id,))
    
    result = cursor.fetchone()
    return result[0] if result else None

def obtener_pacientes_df():
    """Obtiene todos los pacientes y los devuelve como un DataFrame"""
    cursor.execute('SELECT * FROM pacientes')
    pacientes = cursor.fetchall()
    columnas = ['id', 'nombre', 'apellido', 'dni', 'fecha_nacimiento', 'nombre_padre', 
                'telefono_padre', 'nombre_madre', 'telefono_madre', 'nombre_familiar', 
                'telefono_familiar', 'domicilio', 'motivo_consulta', 'datos_escolares', 
                'año_inicio_consulta','telefono_paciente','obra_social','numero_afiliado','diagnostico', 'actividad']
    df = pd.DataFrame(pacientes, columns=columnas)
    return df


# Función para calcular la edad
def calcular_edad(fecha_nacimiento):
    try:
        # Convertir la fecha de string a objeto date si es necesario
        if isinstance(fecha_nacimiento, str):
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        elif isinstance(fecha_nacimiento, datetime):
            fecha_nacimiento = fecha_nacimiento.date()
            
        hoy = datetime.today()
        edad = hoy.year - fecha_nacimiento.year
        
        # Restar un año si aún no ha llegado el cumpleaños de este año
        if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
            
        return edad
    except Exception as e:
        return None
    


# Conexión a la base de datos SQLite
conn = sqlite3.connect('consultorio.db')
cursor = conn.cursor()

# Creación de tablas si no existen (ahora incluye los nuevos campos)
cursor.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    dni INTEGER NOT NULL,
    fecha_nacimiento TEXT,
    nombre_padre TEXT,
    telefono_padre TEXT,
    nombre_madre TEXT,
    telefono_madre TEXT,
    nombre_familiar TEXT,
    telefono_familiar TEXT,
    domicilio TEXT,
    motivo_consulta TEXT,
    datos_escolares TEXT,
    año_inicio_consulta INTEGER,
    telefono_paciente INTEGRER,
    obra_social TEXT,
    numero_afiliado INTEGRER,
    diagnostico TEXT,
    actividad BOOL 
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    fecha TEXT,
    notas TEXT,
    asistio BOOLEAN,
    pago BOOLEAN,
    monto REAL,
    numero_factura TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS turnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL
)
''')
conn.commit()

# Funciones para manejar la base de datos
def agregar_paciente(nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, 
                     nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, 
                     domicilio, motivo_consulta, datos_escolares, 
                     año_inicio_consulta,telefono_paciente,obra_social,numero_afiliado,diagnostico, actividad):
    cursor.execute('''
    INSERT INTO pacientes (
        nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, 
        nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, 
        domicilio, motivo_consulta, datos_escolares, año_inicio_consulta, telefono_paciente, obra_social, numero_afiliado, diagnostico, actividad )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, 
          nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, 
          domicilio, motivo_consulta, datos_escolares,
          año_inicio_consulta,telefono_paciente,obra_social,numero_afiliado, diagnostico, actividad))
    conn.commit()

def obtener_pacientes():
    cursor.execute('SELECT * FROM pacientes')
    return cursor.fetchall()




def actualizar_paciente(paciente_id, nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares,año_inicio_consulta,telefono_paciente,obra_social,numero_afiliado, diagnostico, actividad):
    cursor.execute('''
    UPDATE pacientes SET nombre = ?, apellido = ?, dni = ?, fecha_nacimiento = ?, nombre_padre = ?, telefono_padre = ?, nombre_madre = ?, telefono_madre = ?, nombre_familiar = ?, telefono_familiar = ?, domicilio = ?, motivo_consulta = ?, datos_escolares = ?, año_inicio_consulta = ?,telefono_paciente = ?,obra_social = ?,numero_afiliado = ?, diagnostico = ?, actividad = ? WHERE id = ?
    ''', (nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares,año_inicio_consulta,telefono_paciente,obra_social,numero_afiliado, diagnostico , actividad ,paciente_id))
    conn.commit()

def eliminar_paciente(paciente_id):
    cursor.execute('DELETE FROM pacientes WHERE id = ?', (paciente_id,))
    cursor.execute('DELETE FROM sesiones WHERE paciente_id = ?', (paciente_id,))  # Elimina las sesiones relacionadas
    conn.commit()

def agregar_sesion(paciente_id, fecha, notas, asistio, pago, monto, numero_factura):
    cursor.execute('''
    INSERT INTO sesiones (paciente_id, fecha, notas, asistio, pago, monto, numero_factura) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (paciente_id, fecha, notas, asistio, pago, monto, numero_factura))
    conn.commit()

def obtener_sesiones(paciente_id):
    cursor.execute('''
    SELECT id, paciente_id, fecha, notas, asistio, pago, monto, numero_factura 
    FROM sesiones 
    WHERE paciente_id = ?
    ORDER BY fecha DESC
    ''', (paciente_id,))
    return cursor.fetchall()

def actualizar_sesion(sesion_id, fecha, notas, asistio, pago, monto, numero_factura):
    cursor.execute('''
    UPDATE sesiones 
    SET fecha = ?, notas = ?, asistio = ?, pago = ?, monto = ?, numero_factura = ?
    WHERE id = ?
    ''', (fecha, notas, asistio, pago, monto, numero_factura, sesion_id))
    conn.commit()

def eliminar_sesion(sesion_id):
    cursor.execute('DELETE FROM sesiones WHERE id = ?', (sesion_id,))
    conn.commit()


def agregar_turno(nombre, fecha, hora):
    cursor.execute('''
    INSERT INTO turnos (nombre, fecha, hora)
    VALUES (?, ?, ?)
    ''', (nombre, fecha, hora))
    conn.commit()

def obtener_turnos_dia(fecha):
    cursor.execute('''
    SELECT id, nombre, fecha, hora
    FROM turnos
    WHERE fecha = ?
    ORDER BY hora
    ''', (fecha,))
    return cursor.fetchall()

def obtener_turnos_mes(año, mes):
    cursor.execute('''
    SELECT id, nombre, fecha, hora
    FROM turnos
    WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
    ORDER BY fecha, hora
    ''', (str(año), str(mes).zfill(2)))
    return cursor.fetchall()

def verificar_disponibilidad(fecha, hora_consulta):
    """
    Verifica si hay disponibilidad para un turno en la fecha y hora especificadas
    """
    # Convertir la hora de consulta a minutos desde medianoche para facilitar comparación
    hora_inicio_mins = int(hora_consulta.split(':')[0]) * 60 + int(hora_consulta.split(':')[1])
    hora_fin_mins = hora_inicio_mins + 40  # 40 minutos de duración
    
    # Obtener todos los turnos para esa fecha
    cursor.execute('''
    SELECT hora FROM turnos
    WHERE fecha = ?
    ''', (fecha,))
    
    turnos_existentes = cursor.fetchall()
    
    # Verificar superposición con turnos existentes
    for turno in turnos_existentes:
        turno_hora = turno[0]
        # Convertir hora del turno existente a minutos
        turno_mins = int(turno_hora.split(':')[0]) * 60 + int(turno_hora.split(':')[1])
        turno_fin_mins = turno_mins + 40
        
        # Verificar si hay superposición
        if not (hora_fin_mins <= turno_mins or hora_inicio_mins >= turno_fin_mins):
            return False
    
    return True

def eliminar_turno(turno_id):
    cursor.execute('DELETE FROM turnos WHERE id = ?', (turno_id,))
    conn.commit()



def eliminar_turnos_por_nombre(nombre):
    """
    Elimina todos los turnos de un paciente específico
    """
    cursor.execute('DELETE FROM turnos WHERE nombre = ?', (nombre,))
    conn.commit()
    return cursor.rowcount  # Retorna el número de turnos eliminados

def obtener_nombres_pacientes_con_turnos(año, mes):
    """
    Obtiene una lista única de nombres de pacientes que tienen turnos en el mes seleccionado
    """
    cursor.execute('''
    SELECT DISTINCT nombre
    FROM turnos
    WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
    ORDER BY nombre
    ''', (str(año), str(mes).zfill(2)))
    return [row[0] for row in cursor.fetchall()]


obras_sociales = [
                "Ninguna",
                "Prensa",
                "Galeno",
                "OSDE",
                "Swiss Medical",
                "Medife",
                "PAMI",
                "Sancor Salud",
                "Subsidio de Salud",
                "Otra"]


@login_required
def main():
    st.title("Sistema Gestor de Pacientes - Consultorio Psicopedagógico")
       
    menu = st.sidebar.selectbox(
        "Seleccione una opción", 
        ["Inicio", "Registrar Paciente", "Lista de Pacientes", "Registrar Sesión", "Calendario de Turnos"]
    )
    logout()

                #### INICIO ####
    if menu == "Inicio":
        car= Image.open('./img/KENTI.png')        
        st.image(car,use_container_width=True,)
        # Carátula de Presentación
        st.title("Bienvenido")
        st.subheader("Gestor de Pacientes para Consultorio Psicopedagógico")

        st.markdown("""
        Este sistema está diseñado para facilitar la gestión de turnos y datos de pacientes para el consultorio de psicopedagogía.
        A continuación, se presentan las instrucciones de uso de la página:

        1. **Registro de Pacientes**: Ingresa la información básica de cada paciente para llevar un control detallado.
        2. **Gestión de Turnos**: Agrega y administra los turnos de los pacientes.
        3. **Registro de Sesiones**: Documenta cada sesión con sus observaciones para tener un historial detallado.

        ¡Gracias por confiar en nuestro sistema para una mejor organización!

        """)

        st.write("---")  # Línea divisoria

            # Selector de mes y año
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mes", range(1, 13), datetime.now().month-1 )            
        with col2:
            año = st.selectbox("Año", range(2025, 2031), 0)
            
    # Obtener todos los turnos del mes seleccionado
        turnos_mes = obtener_turnos_mes(año, mes)
            
            # Crear un calendario mensual
        cal = calendar.monthcalendar(año, mes)
            
            # Crear una tabla para mostrar el calendario
        st.markdown("### Calendario de Turnos")
            
            # Encabezados de los días
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

            # Crear el calendario como una tabla HTML
        tabla_html = f"""
        <style>
        .calendario {{
            width: 100%;
            border-collapse: collapse;
            }}
        .calendario th, .calendario td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
            height: 80px;
            vertical-align: top;
            }}
        .calendario th {{
            background-color: #f8f9fa;
            }}
        .turno {{
            font-size: 0.8em;
            margin: 2px;
            padding: 2px;
            background-color: #e7f3fe;
            border-radius: 3px;
            }}
        </style>
        <table class="calendario">
        <tr>
            """
            
            # Añadir encabezados
        for dia in dias_semana:
            tabla_html += f"<th>{dia}</th>"
        tabla_html += "</tr>"
            
            # Organizar turnos por fecha
        turnos_por_fecha = {}
        for turno in turnos_mes:
            fecha = turno[2]
            if fecha not in turnos_por_fecha:
                turnos_por_fecha[fecha] = []
            turnos_por_fecha[fecha].append(turno)
            
            # Añadir las semanas
        for semana in cal:
            tabla_html += "<tr>"
            for dia in semana:
                if dia == 0:
                    tabla_html += "<td></td>"
                else:
                    fecha = f"{año}-{str(mes).zfill(2)}-{str(dia).zfill(2)}"
                    tabla_html += f"<td><div style='font-weight: bold;'>{dia}</div>"
                        
                        # Añadir turnos del día
                    if fecha in turnos_por_fecha:
                        for turno in turnos_por_fecha[fecha]:
                            tabla_html += f"<div class='turno'>{turno[3]} - {turno[1]}</div>"
                        
                    tabla_html += "</td>"
            tabla_html += "</tr>"
            
        tabla_html += "</table>"
        st.markdown(tabla_html, unsafe_allow_html=True)

        st.write("---")  # Línea divisoria


                    #### REGISTRAR PACIENTES ####
    elif menu == "Registrar Paciente":
    

        st.header("Registrar un nuevo paciente")
        nombre = st.text_input("Nombre *")
        apellido = st.text_input("Apellido *")
        dni = st.text_input("DNI *")        
        if dni:
            if not dni.isdigit():
                st.error("Por favor ingrese solo números en el DNI")
                dni = ""
            else:
                dni = int(dni)

        domicilio = st.text_input("Domicilio *")
        # Mostrar la fecha de nacimiento y la edad calculada
        col1, col2 = st.columns(2)
        with col1:
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", min_value=datetime(1960, 1, 1), max_value=datetime.today())
        with col2:
            edad = calcular_edad(fecha_nacimiento)
            if edad is not None:

                st.write("")
                st.error(f"Edad: {edad} años")        
        año_inicio_consulta = st.selectbox("Año de Inicio de Consulta", 
                                           list(range(2021, datetime.now().year + 1)))
       
        telefono_paciente = st.text_input("Teléfono del Paciente")
        nombre_padre = st.text_input("Nombre del Padre/Tutor")
        telefono_padre = st.text_input("Teléfono del Padre/Tutor")
        nombre_madre = st.text_input("Nombre de la Madre/Tutora")
        telefono_madre = st.text_input("Teléfono de la Madre/Tutora")
        nombre_familiar = st.text_input("Nombre de Otro Familiar")
        telefono_familiar = st.text_input("Teléfono del Familiar")
        obra_social = st.selectbox("Seleccione una obra social:", obras_sociales)
        if obra_social != "Ninguna":                   
            if obra_social == "Otra":
                col1, col2 = st.columns(2)
                with col1:                
                        obra_social = st.text_input("Ingrese la Obra Social")
                with col2:
                    numero_afiliado = st.text_input("Numero de Afiliado")
            else:
                numero_afiliado = st.text_input("Numero de Afiliado")
        else:
            numero_afiliado = ""    
        motivo_consulta = st.text_area("Motivo de Consulta")
        datos_escolares = st.text_area("Datos Escolares")
        diagnostico = st.text_input("Diagnostico del Paciente")

        actividad = st.checkbox(" Activo ", value=True)

        if st.button("Guardar"):
            if nombre and apellido and dni and domicilio:
                agregar_paciente(nombre, apellido, dni, fecha_nacimiento,
                                nombre_padre, telefono_padre, nombre_madre, 
                                telefono_madre, nombre_familiar, telefono_familiar, 
                                domicilio, motivo_consulta, datos_escolares,
                                año_inicio_consulta,telefono_paciente,obra_social,
                                numero_afiliado,diagnostico, actividad)
                st.success("Paciente registrado correctamente")
            else:
                st.error("Por favor, complete todos los campos obligatorios")


            #### LISTA DE PACIENTES ####
    elif menu == "Lista de Pacientes":
        st.header("Lista de Pacientes")
        
        # Obtener DataFrame de pacientes
        df_pacientes = obtener_pacientes_df()
        
        # Agregar columna de edad
        df_pacientes['edad'] = df_pacientes['fecha_nacimiento'].apply(calcular_edad)
        
        # Barra de búsqueda y filtros
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Buscar paciente por nombre, apellido o DNI", "")
        with col2:
            sort_by = st.selectbox("Ordenar por:", ["Apellido", "Nombre", "Fecha de Nac.", "Año Inicio"])
        with col3:
            # Filtro de año de inicio de consulta
            años_consulta = sorted(df_pacientes['año_inicio_consulta'].dropna().unique())
            filtro_año = st.selectbox("Filtrar por Año de Inicio", 
                                    ["Todos"] + [str(año) for año in años_consulta])
        
        # Filtrar y ordenar pacientes 
        df_filtrado = df_pacientes.copy()
        
        # Aplicar filtro de búsqueda
        if search_term:
            df_filtrado = df_filtrado[
                df_filtrado['nombre'].str.contains(search_term, case=False, na=False) |
                df_filtrado['apellido'].str.contains(search_term, case=False, na=False) |
                df_filtrado['dni'].astype(str).str.contains(search_term, case=False, na=False)
            ]
        
        # Aplicar filtro de año de inicio
        if filtro_año != "Todos":
            df_filtrado = df_filtrado[df_filtrado['año_inicio_consulta'] == int(filtro_año)]
        
        # Ordenar pacientes
        if sort_by == "Apellido":
            df_filtrado = df_filtrado.sort_values('apellido')
        elif sort_by == "Nombre":
            df_filtrado = df_filtrado.sort_values('nombre')
        elif sort_by == "Fecha de Nac.":
            df_filtrado = df_filtrado.sort_values('fecha_nacimiento', ascending=False)
        elif sort_by == "Año Inicio":
            df_filtrado = df_filtrado.sort_values('año_inicio_consulta', ascending=False)
        
        estado_activdad = st.selectbox("Filtrar por actividad:",["Todos","Activo","Inactivo"], key="act")
        if estado_activdad != "Todos":
            if estado_activdad == "Activo":
                df_filtrado = df_filtrado[df_filtrado['actividad'] == True]
            else:  # "Inactivo"
                df_filtrado = df_filtrado[df_filtrado['actividad'] == False]
        
        st.markdown("<div class='totalPacientes'>Total de pacientes: "+ str(len(df_filtrado)) +"</div> ", unsafe_allow_html=True)
        
        st.write('')

        # Mostrar tabla de resumen
        if not df_filtrado.empty:
            tabla_resumen = pd.DataFrame({
                'Nombre Completo': df_filtrado['nombre'] + " " + df_filtrado['apellido'],
                'DNI': df_filtrado['dni'].astype(str),
                'Edad': df_filtrado['edad'].apply(lambda x: f"{x} años" if pd.notnull(x) else "N/A"),
                'Fecha Nac.': df_filtrado['fecha_nacimiento'],
                'Año de Inicio': df_filtrado['año_inicio_consulta'].astype(str),

            })
            
            pd.options.display.float_format = '{:.0f}'.format


            st.dataframe(tabla_resumen, use_container_width=True)

   

            # Lista de pacientes con detalles expandibles
            for _, paciente in df_filtrado.iterrows():
                # Obtener estadísticas de sesiones
                stats = obtener_estadisticas_sesiones(paciente['id'])
                ultima_sesion = obtener_ultima_sesion(paciente['id'])
                estado = "🟢 Activo" if paciente['actividad'] else "🔴 Inactivo"
                
                with st.expander(f"📋 {paciente['nombre']} {paciente['apellido']} - DNI: {paciente['dni']} - {estado}" ):
                    st.markdown(f"**Estado:** {estado}")
                    # Primera fila: Información general y estadísticas
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Información Personal")
                        st.write(f"Fecha Nac.: {paciente['fecha_nacimiento']}")
                        st.write(f"Edad: {paciente['edad']} años")
                        st.write(f"Domicilio: {paciente['domicilio']}")                        
                        st.write(f"Obra Social: {paciente['obra_social']} N°: {paciente['numero_afiliado']}")                        
                        st.write(f"Diagnostico: {paciente['diagnostico']}")              
                                          
                    with col2:
                        st.subheader("Información de Contacto")
                        st.write(f"Padre/Tutor: {paciente['nombre_padre']}")
                        st.write(f"Tel. Padre: {paciente['telefono_padre']}")
                        st.write(f"Madre/Tutora: {paciente['nombre_madre']}")
                        st.write(f"Tel. Madre: {paciente['telefono_madre']}")
                        st.write(f"Tel. Paciente: {paciente['telefono_paciente']}")

                    st.markdown("---")

                    st.subheader("Estadísticas de Sesiones")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"Total Sesiones: {stats['total_sesiones']}")
                    with col2:
                        st.write(f"✅ Sesiones Asistidas: {stats['sesiones_asistidas']}")
                    with col3:
                        st.write(f"💰 Sesiones Pagadas: {stats['sesiones_pagadas']}")
                    with col4:
                        st.write(f"Año de inicio: {paciente['año_inicio_consulta']}")
                    if stats['deuda_total'] > 0:
                        st.error(f"💸 Deuda Total: ${stats['deuda_total']:.2f}")
                    else:
                        st.success("✨ Sin deuda pendiente")
                    if ultima_sesion:
                        st.write(f"Última sesión: {ultima_sesion}")

                    # Segunda fila: Detalles clínicos
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Motivo de Consulta:**")
                        st.text_area("", paciente['motivo_consulta'], height=100, 
                                key=f"motivo_{paciente['id']}", disabled=True)
                    
                    with col2:
                        st.markdown("**Datos Escolares:**")
                        st.text_area("", paciente['datos_escolares'], height=100, 
                                key=f"escolar_{paciente['id']}", disabled=True)

                    # Botones de acción
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Editar", key=f"edit_{paciente['id']}"):
                            st.session_state.editing = paciente['id']
                    with col2:
                        if st.button("🗑️ Eliminar", key=f"delete_{paciente['id']}"):
                            eliminar_paciente(paciente['id'])
                            st.success("Paciente eliminado correctamente")
                            st.rerun()
                    with col3:
                        if st.button("📝 Sesiones", key=f"sessions_{paciente['id']}"):
                            st.session_state.viewing_sessions = paciente['id']

                    # Mostrar formulario de edición
                    if st.session_state.get('editing') == paciente['id']:
                        st.markdown("### Editar Paciente")
                        nueva_actividad = st.checkbox(" Activo ", value=True)
                        nuevo_nombre = st.text_input("Nombre", paciente['nombre'])
                        nuevo_apellido = st.text_input("Apellido", paciente['apellido'])
                        nuevo_dni = st.text_input("DNI", paciente['dni'])
                        nuevo_domicilio = st.text_input("Domicilio", paciente['domicilio'])
                        nueva_fecha = st.date_input("Fecha de Nacimiento", 
                                                min_value=datetime(1960, 1, 1), max_value=datetime.today())
                        nuevo_año_inicio_consulta = st.selectbox("Año de Inicio de Consulta", 
                                           list(range(2021, datetime.now().year + 1))) 
                        nuevo_telefono_paciente = st.text_input("Teléfono del Paciente")                                           
                        nuevo_nombre_padre = st.text_input("Nombre del Padre", paciente['nombre_padre'])
                        nuevo_tel_padre = st.text_input("Teléfono del Padre", paciente['telefono_padre'])
                        nuevo_nombre_madre = st.text_input("Nombre de la Madre", paciente['nombre_madre'])
                        nuevo_tel_madre = st.text_input("Teléfono de la Madre", paciente['telefono_madre'])
                        nuevo_nombre_familiar = st.text_input("Nombre del Familiar", paciente['nombre_familiar'])
                        nuevo_tel_familiar = st.text_input("Teléfono del Familiar", paciente['telefono_familiar'])
                        nueva_obra_social = st.selectbox("Seleccione una obra social:", obras_sociales)
                        if nueva_obra_social != "Ninguna":                   
                            if nueva_obra_social == "Otra":
                                col1, col2 = st.columns(2)
                                with col1:                
                                        nueva_obra_social = st.text_input("Ingrese la Obra Social")
                                with col2:
                                    nuevo_numero_afiliado = st.text_input("Numero de Afiliado")
                            else:
                                nuevo_numero_afiliado = st.text_input("Numero de Afiliado")
                        else:
                            nuevo_numero_afiliado = ""                           
                        nuevo_motivo = st.text_area("Motivo de Consulta", paciente['motivo_consulta'])
                        nuevos_datos_escolares = st.text_area("Datos Escolares", paciente['datos_escolares'])
                        nuevo_diagnostico = st.text_input("Diagnostico del Paciente")

                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Guardar Cambios"):
                                actualizar_paciente(
                                    paciente['id'], nuevo_nombre, nuevo_apellido, nuevo_dni, 
                                    nueva_fecha, nuevo_nombre_padre, nuevo_tel_padre,
                                    nuevo_nombre_madre, nuevo_tel_madre, nuevo_nombre_familiar,
                                    nuevo_tel_familiar, nuevo_domicilio, nuevo_motivo, nuevos_datos_escolares,
                                    nuevo_año_inicio_consulta,nuevo_telefono_paciente,nueva_obra_social,nuevo_numero_afiliado,nuevo_diagnostico, nueva_actividad
                                )
                                st.success("Paciente actualizado correctamente")
                                st.session_state.editing = None
                                st.rerun()
                        with col2:
                            if st.button("Cancelar"):
                                st.session_state.editing = None
                                st.rerun()

                                # Mostrar sesiones
                    if st.session_state.get('viewing_sessions') == paciente['id']:
                        st.markdown("### Sesiones del Paciente")
                        sesiones = obtener_sesiones(paciente['id'])
                        
                        if sesiones:
                            st.markdown("""
                            <style>
                            .session-container {
                                border: 1px solid #ddd;
                                padding: 1px;
                                margin: 10px 0;
                                border-radius: 5px;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            for sesion in sesiones:
                                sesion_id, _, fecha, notas, asistio, pago, monto, numero_factura = sesion
                                
                                st.markdown(f'<div class="session-container">', unsafe_allow_html=True)
                                
                                # Verificar si esta sesión está en modo edición
                                is_editing = st.session_state.get(f'editing_session_{sesion_id}', False)
                                
                                if is_editing:
                                    # Modo edición
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        nueva_fecha = st.date_input(
                                            "Fecha", 
                                            datetime.strptime(fecha, '%Y-%m-%d').date(),
                                            key=f"edit_fecha_{sesion_id}"
                                        )
                                        nuevo_asistio = st.checkbox("¿Asistió?", asistio, key=f"edit_asistio_{sesion_id}")
                                        nuevo_pago = st.checkbox("¿Pagó?", pago, key=f"edit_pago_{sesion_id}")
                                        nuevo_monto = st.number_input("Monto ($)", value=float(monto), min_value=0.0, 
                                                                    step=100.0, key=f"edit_monto_{sesion_id}")
                                        nuevo_numero_factura = st.text_input("Número de Factura", 
                                                                        value=numero_factura if numero_factura else "",
                                                                        key=f"edit_factura_{sesion_id}")
                                        nuevas_notas = st.text_area("Notas", notas, height=150, 
                                                                key=f"edit_notas_{sesion_id}")
                                    
                                    with col2:
                                        col3, col4 = st.columns(2)
                                        with col3:
                                            if st.button("💾", key=f"save_session_{sesion_id}"):
                                                actualizar_sesion(
                                                    sesion_id, nueva_fecha, nuevas_notas, 
                                                    nuevo_asistio, nuevo_pago, nuevo_monto, 
                                                    nuevo_numero_factura
                                                )
                                                st.session_state[f'editing_session_{sesion_id}'] = False
                                                st.success("Sesión actualizada")
                                                st.rerun()
                                        with col4:
                                            if st.button("❌", key=f"cancel_edit_{sesion_id}"):
                                                st.session_state[f'editing_session_{sesion_id}'] = False
                                                st.rerun()
                                else:
                                    # Modo visualización
                                    col1, col2 = st.columns([5, 1])
                                    with col1:
                                        st.markdown("**Fecha:**")
                                        st.write(fecha)
                                        if numero_factura:
                                            st.write(f"**Factura N°:** {numero_factura}")
                                        st.markdown("**Estado:**")
                                        st.write(f"✓ Asistió: {'Sí' if asistio else 'No'}")
                                        st.write(f"💰 Pagó: {'Sí' if pago else 'No'}")
                                        st.write(f"💵 Monto: ${monto}")
                                        st.markdown("**Notas:**")
                                        st.text_area("", notas, height=150, key=f"notas_sesion_{sesion_id}", 
                                                disabled=True)
                                    
                                    with col2:
                                        col3, col4 = st.columns(2)
                                        with col3:
                                            if st.button("✏️", key=f"edit_session_{sesion_id}"):
                                                st.session_state[f'editing_session_{sesion_id}'] = True
                                                st.rerun()
                                        with col4:
                                            if st.button("🗑️", key=f"del_session_{sesion_id}"):
                                                eliminar_sesion(sesion_id)
                                                st.success("Sesión eliminada")
                                                st.rerun()
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.info("No hay sesiones registradas para este paciente")
                        
                        if st.button("❌ Cerrar Sesiones", key=f"close_sessions_{paciente['id']}"):
                            st.session_state.viewing_sessions = None
                            st.rerun()
                    


        #### REGISTRAR SECIONES ####
    elif menu == "Registrar Sesión":
        st.header("Registrar sesión para un paciente")

        pacientes = obtener_pacientes()
        if pacientes:
            paciente_seleccionado = st.selectbox("Seleccione un paciente", 
                                            [f"{p[1]} {p[2]}" for p in pacientes])
            paciente_id = [p[0] for p in pacientes if f"{p[1]} {p[2]}" == paciente_seleccionado][0]
            
            # Crear columnas para organizar mejor la interfaz
            col1, col2 = st.columns(2)
            
            with col1:
                fecha = st.date_input("Fecha de la sesión", datetime.now())
                asistio = st.checkbox("¿El paciente asistió a la sesión?", value=True)
                pago = st.checkbox("¿El paciente pagó la sesión?", value=False)
            
            with col2:
                monto = st.number_input("Monto de la sesión ($)", min_value=0.0, step=100.0)
                numero_factura = st.text_input("Número de Factura")
            
            notas = st.text_area("Notas de la sesión")

            if st.button("Guardar Sesión"):
                agregar_sesion(paciente_id, fecha, notas, asistio, pago, monto, numero_factura)
                st.success("Sesión registrada correctamente")

            # Mostrar historial de sesiones
            st.header("Historial de sesiones del paciente")
            sesiones = obtener_sesiones(paciente_id)
            
            if sesiones:
                # Agregar filtros de búsqueda
                col1, col2 = st.columns(2)
                with col1:
                    filtro_fecha = st.date_input("Filtrar por fecha", None)
                with col2:
                    filtro_pago = st.selectbox("Filtrar por estado de pago", 
                                            ["Todos", "Pagados", "Pendientes"])
                
                # Aplicar filtros
                sesiones_filtradas = sesiones
                if filtro_fecha:
                    sesiones_filtradas = [s for s in sesiones_filtradas 
                                        if datetime.strptime(s[2], '%Y-%m-%d').date() == filtro_fecha]
                if filtro_pago != "Todos":
                    sesiones_filtradas = [s for s in sesiones_filtradas 
                                        if (s[5] and filtro_pago == "Pagados") or 
                                        (not s[5] and filtro_pago == "Pendientes")]
                
                # Mostrar total de deuda
                total_deuda = sum([s[6] for s in sesiones_filtradas if not s[5]])
                if total_deuda > 0:
                    st.error(f"💸 Deuda total pendiente: ${total_deuda:.2f}")
                else:
                    st.success("✨ No hay deuda pendiente")
                
                for sesion in sesiones_filtradas:
                    sesion_id, _, fecha, notas, asistio, pago, monto, numero_factura = sesion
                    
                    with st.expander(f"Sesión del {fecha} - {'✅ Pagada' if pago else '⏳ Pendiente'}"):
                        # Verificar si esta sesión está en modo edición
                        is_editing = st.session_state.get(f'editing_session_{sesion_id}', False)
                        
                        if is_editing:
                            # Modo edición
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                nueva_fecha = st.date_input(
                                    "Fecha", 
                                    datetime.strptime(fecha, '%Y-%m-%d').date(),
                                    key=f"edit_fecha_{sesion_id}"
                                )
                                nuevo_asistio = st.checkbox("¿Asistió?", asistio, 
                                                        key=f"edit_asistio_{sesion_id}")
                                nuevo_pago = st.checkbox("¿Pagó?", pago, 
                                                    key=f"edit_pago_{sesion_id}")
                                nuevo_monto = st.number_input("Monto ($)", 
                                                            value=float(monto), 
                                                            min_value=0.0, 
                                                            step=100.0,
                                                            key=f"edit_monto_{sesion_id}")
                                nuevo_numero_factura = st.text_input(
                                    "Número de Factura", 
                                    value=numero_factura if numero_factura else "",
                                    key=f"edit_factura_{sesion_id}"
                                )
                                nuevas_notas = st.text_area("Notas", notas, 
                                                        height=150,
                                                        key=f"edit_notas_{sesion_id}")
                            
                            with col2:
                                if st.button("💾 Guardar", key=f"save_session_{sesion_id}"):
                                    actualizar_sesion(
                                        sesion_id, nueva_fecha, nuevas_notas,
                                        nuevo_asistio, nuevo_pago, nuevo_monto,
                                        nuevo_numero_factura
                                    )
                                    st.session_state[f'editing_session_{sesion_id}'] = False
                                    st.success("Sesión actualizada")
                                    st.rerun()
                                
                                if st.button("❌ Cancelar", key=f"cancel_edit_{sesion_id}"):
                                    st.session_state[f'editing_session_{sesion_id}'] = False
                                    st.rerun()
                        
                        else:
                            # Modo visualización
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write("**Estado de la sesión:**")
                                st.write(f"✓ Asistió: {'Sí' if asistio else 'No'}")
                                st.write(f"💰 Pagó: {'Sí' if pago else 'No'}")
                                st.write(f"💵 Monto: ${monto}")
                                if numero_factura:
                                    st.write(f"📄 Factura N°: {numero_factura}")
                                st.write("**Notas:**")
                                st.text_area("", notas, height=100, 
                                        key=f"notas_sesion_{sesion_id}", 
                                        disabled=True)
                            
                            with col2:
                                if st.button("✏️ Editar", key=f"edit_session_{sesion_id}"):
                                    st.session_state[f'editing_session_{sesion_id}'] = True
                                    st.rerun()
                                
                                if st.button("🗑️ Eliminar", key=f"del_session_{sesion_id}"):
                                    eliminar_sesion(sesion_id)
                                    st.success("Sesión eliminada")
                                    st.rerun()
            else:
                st.info("No hay sesiones registradas para este paciente")

                                                ### TURNOS ###
    elif menu == "Calendario de Turnos":
        st.title("Gestión de Turnos")

        # Crear pestañas para separar la vista de turnos y el registro
        tab1, tab2, tab3 = st.tabs(["📅 Ver Turnos", "➕ Registrar Turno", "🗑️ Eliminar Turnos"])

        with tab1:
            st.header("Calendario de Turnos")

            # Selector de mes y año
            col1, col2 = st.columns(2)
            with col1:
                mes = st.selectbox("Mes", range(1, 13), datetime.now().month-1 )            
            with col2:
                año = st.selectbox("Año", range(2025, 2031), 0)
            
            # Obtener todos los turnos del mes seleccionado
            turnos_mes = obtener_turnos_mes(año, mes)
            
            # Crear un calendario mensual
            cal = calendar.monthcalendar(año, mes)
            
            # Crear una tabla para mostrar el calendario
            st.markdown("### Calendario")
            
            # Encabezados de los días
            dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

            # Crear el calendario como una tabla HTML
            tabla_html = f"""
            <style>
            .calendario {{
                width: 100%;
                border-collapse: collapse;
            }}
            .calendario th, .calendario td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
                height: 80px;
                vertical-align: top;
            }}
            .calendario th {{
                background-color: #f8f9fa;
            }}
            .turno {{
                font-size: 0.8em;
                margin: 2px;
                padding: 2px;
                background-color: #e7f3fe;
                border-radius: 3px;
            }}
            </style>
            <table class="calendario">
            <tr>
            """
            
            # Añadir encabezados
            for dia in dias_semana:
                tabla_html += f"<th>{dia}</th>"
            tabla_html += "</tr>"
            
            # Organizar turnos por fecha
            turnos_por_fecha = {}
            for turno in turnos_mes:
                fecha = turno[2]
                if fecha not in turnos_por_fecha:
                    turnos_por_fecha[fecha] = []
                turnos_por_fecha[fecha].append(turno)
            
            # Añadir las semanas
            for semana in cal:
                tabla_html += "<tr>"
                for dia in semana:
                    if dia == 0:
                        tabla_html += "<td></td>"
                    else:
                        fecha = f"{año}-{str(mes).zfill(2)}-{str(dia).zfill(2)}"
                        tabla_html += f"<td><div style='font-weight: bold;'>{dia}</div>"
                        
                        # Añadir turnos del día
                        if fecha in turnos_por_fecha:
                            for turno in turnos_por_fecha[fecha]:
                                tabla_html += f"<div class='turno'>{turno[3]} - {turno[1]}</div>"
                        
                        tabla_html += "</td>"
                tabla_html += "</tr>"
            
            tabla_html += "</table>"
            st.markdown(tabla_html, unsafe_allow_html=True)
            
            # Mostrar lista detallada de turnos del mes
            if turnos_mes:            
                st.markdown("### Lista de Turnos del Mes")
                for turno in turnos_mes:
                    with st.expander(f"{turno[2]} - {turno[3]} - {turno[1]}"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Nombre:** {turno[1]}")
                        with col2:
                            if st.button("🗑️ Cancelar", key=f"del_turno_{turno[0]}"):
                                eliminar_turno(turno[0])
                                st.success("Turno cancelado")
                                st.rerun()
        
        with tab2:
            st.header("Registrar Nuevo Turno")
            
            # Formulario de registro de turno
            nombre = st.text_input("Nombre")
            es_recurrente = st.checkbox("Turno recurrente", value=False)
            
            col1, col2 = st.columns(2)
            with col1:
                if es_recurrente:
                    dia_semana = st.selectbox("Día de la semana", 
                                            ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
                    primer_dia = datetime(año, mes, 1)
                    ultimo_dia = datetime(año, mes, calendar.monthrange(año, mes)[1])
                    
                    dias_map = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4}
                    fechas_dia = []
                    fecha_actual = primer_dia
                    while fecha_actual <= ultimo_dia:
                        if fecha_actual.weekday() == dias_map[dia_semana]:
                            fechas_dia.append(fecha_actual.date())
                        fecha_actual += timedelta(days=1)
                else:
                    fecha = st.date_input("Fecha", min_value=datetime.today())
            
            with col2:
                horarios = []
                hora_actual = datetime.strptime("08:00", "%H:%M")
                hora_fin = datetime.strptime("20:00", "%H:%M")
                while hora_actual < hora_fin:
                    horarios.append(hora_actual.strftime("%H:%M"))
                    hora_actual += timedelta(minutes=40)
                hora = st.selectbox("Hora", horarios)
            
            # Inicializar estado si no existe
            if 'turno_registrado' not in st.session_state:
                st.session_state.turno_registrado = False
            
            if st.button("Registrar Turno"):
                if nombre and hora:
                    if es_recurrente:
                        turnos_exitosos = 0
                        turnos_fallidos = 0
                        for fecha_dia in fechas_dia:
                            if verificar_disponibilidad(fecha_dia, hora):
                                agregar_turno(nombre, fecha_dia, hora)
                                turnos_exitosos += 1
                            else:
                                turnos_fallidos += 1
                        
                        if turnos_exitosos > 0:
                            st.session_state.turno_registrado = True
                        if turnos_fallidos > 0:
                            st.warning(f"No se pudieron registrar {turnos_fallidos} turnos por conflictos de horario")
                        st.rerun()
                    else:
                        if verificar_disponibilidad(fecha, hora):
                            agregar_turno(nombre, fecha, hora)
                            st.session_state.turno_registrado = True
                            st.rerun()
                        else:
                            st.error("El horario seleccionado no está disponible")
                else:
                    st.warning("Por favor complete todos los campos requeridos")
            
            # Mostrar el mensaje de éxito después de la recarga
            if st.session_state.turno_registrado:
                st.success("Turno registrado exitosamente")
                st.session_state.turno_registrado = False
        
        with tab3:
            st.header("Eliminar Turnos por Paciente")
            
            # Selector de mes y año
            col1, col2 = st.columns(2)
            with col1:
                mes = st.selectbox("Mes", range(1, 13), datetime.now().month-1, key="mes_eliminar")
            with col2:
                año = st.selectbox("Año", range(2025, 2031), 0, key="año_eliminar")

            # Obtener lista de pacientes con turnos en el mes seleccionado
            pacientes_con_turnos = obtener_nombres_pacientes_con_turnos(año, mes)
            
            if pacientes_con_turnos:
                # Selector de paciente
                paciente_seleccionado = st.selectbox(
                    "Seleccione el paciente cuyos turnos desea eliminar",
                    pacientes_con_turnos
                )
                
                # Mostrar turnos del paciente seleccionado
                cursor.execute('''
                    SELECT fecha, hora
                    FROM turnos
                    WHERE nombre = ? AND strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
                    ORDER BY fecha, hora
                ''', (paciente_seleccionado, str(año), str(mes).zfill(2)))
                
                turnos_paciente = cursor.fetchall()
                
                if turnos_paciente:
                    st.write("Turnos programados para", paciente_seleccionado)
                    for fecha, hora in turnos_paciente:
                        st.write(f"- {fecha} a las {hora}")
                    
                    # Opciones de eliminación
                    opcion_eliminar = st.radio(
                        "¿Qué turnos desea eliminar?",
                        ["Todos los turnos", "Seleccionar turnos específicos"]
                    )
                    
                    if opcion_eliminar == "Todos los turnos":
                        if st.button("Eliminar Todos los Turnos", type="primary"):
                            turnos_eliminados = eliminar_turnos_por_nombre(paciente_seleccionado)
                            st.session_state['mensaje_exito'] = f"Se eliminaron {turnos_eliminados} turnos del paciente {paciente_seleccionado}"
                            st.rerun()
                    else:
                        # Permitir selección múltiple de turnos
                        turnos_a_eliminar = st.multiselect(
                            "Seleccione los turnos a eliminar",
                            [(fecha, hora) for fecha, hora in turnos_paciente],
                            format_func=lambda x: f"{x[0]} a las {x[1]}"
                        )
                        
                        if turnos_a_eliminar and st.button("Eliminar Turnos Seleccionados", type="primary"):
                            for fecha, hora in turnos_a_eliminar:
                                cursor.execute('''
                                    DELETE FROM turnos 
                                    WHERE nombre = ? AND fecha = ? AND hora = ?
                                ''', (paciente_seleccionado, fecha, hora))
                            conn.commit()
                            st.session_state['mensaje_exito'] = f"Se eliminaron {len(turnos_a_eliminar)} turnos seleccionados"
                            st.rerun()
            else:
                st.info(f"No hay turnos registrados para el mes {mes}/{año}")

            # Mostrar mensaje de éxito si existe
            if 'mensaje_exito' in st.session_state:
                st.success(st.session_state['mensaje_exito'])
                del st.session_state['mensaje_exito']  # Limpiar el mensaje después de mostrarlo
                        
    
if __name__ == "__main__":
    main()
conn.close()
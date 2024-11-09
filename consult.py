import streamlit as st
import sqlite3
import pathlib
from datetime import datetime,timedelta
import pandas as pd
import calendar

# Conexión a la base de datos SQLite
conn = sqlite3.connect('consultorio.db')
cursor = conn.cursor()

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
                'telefono_familiar', 'domicilio', 'motivo_consulta', 'datos_escolares']
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
    

# Creación de tablas si no existen (ahora incluye los nuevos campos)
cursor.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    dni TEXT NOT NULL,
    fecha_nacimiento TEXT,
    nombre_padre TEXT,
    telefono_padre TEXT,
    nombre_madre TEXT,
    telefono_madre TEXT,
    nombre_familiar TEXT,
    telefono_familiar TEXT,
    domicilio TEXT,
    motivo_consulta TEXT,
    datos_escolares TEXT
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

# Agregar tabla para gestionar días fijos
cursor.execute('''
CREATE TABLE IF NOT EXISTS dias_fijos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dia_semana INTEGER NOT NULL,  -- 0 = Lunes, 1 = Martes, etc.
    hora TIME NOT NULL,
    UNIQUE(nombre)
)
''')
conn.commit()

# Funciones para manejar la base de datos
def agregar_paciente(nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares):
    cursor.execute('INSERT INTO pacientes (nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares))
    conn.commit()

def obtener_pacientes():
    cursor.execute('SELECT * FROM pacientes')
    return cursor.fetchall()

def actualizar_paciente(paciente_id, nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares):
    cursor.execute('''
    UPDATE pacientes SET nombre = ?, apellido = ?, dni = ?, fecha_nacimiento = ?, nombre_padre = ?, telefono_padre = ?, nombre_madre = ?, telefono_madre = ?, nombre_familiar = ?, telefono_familiar = ?, domicilio = ?, motivo_consulta = ?, datos_escolares = ? WHERE id = ?
    ''', (nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares, paciente_id))
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

def agregar_dia_fijo(nombre, dia_semana, hora):
    """Asigna un día fijo de la semana a un paciente"""
    try:
        cursor.execute('''
        INSERT INTO dias_fijos (nombre, dia_semana, hora)
        VALUES (?, ?, ?)
        ''', (nombre, dia_semana, hora))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def obtener_dia_fijo(nombre):
    """Obtiene el día fijo asignado a un paciente"""
    cursor.execute('''
    SELECT dia_semana, hora
    FROM dias_fijos
    WHERE nombre = ?
    ''', (nombre,))
    return cursor.fetchone()

def eliminar_dia_fijo(nombre):
    """Elimina la asignación de día fijo de un paciente"""
    cursor.execute('DELETE FROM dias_fijos WHERE nombre = ?', (nombre,))
    conn.commit()

def verificar_disponibilidad_dia_fijo(nombre, fecha, hora):
    """Verifica si el paciente puede tomar un turno en ese día y hora"""
    dia_fijo = obtener_dia_fijo(nombre)
    
    if dia_fijo is None:
        return True  # Si no tiene día fijo asignado, puede tomar cualquier turno
    
    dia_semana_turno = datetime.strptime(fecha, '%Y-%m-%d').weekday()
    return dia_semana_turno == dia_fijo[0] and hora == dia_fijo[1]

# Modificar la función de agregar turno para incluir la validación
def agregar_turno(nombre, fecha, hora):
    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d') if isinstance(fecha, str) else fecha
    
    if verificar_disponibilidad_dia_fijo(nombre, fecha_obj.strftime('%Y-%m-%d'), hora):
        if verificar_disponibilidad(fecha_obj.strftime('%Y-%m-%d'), hora):
            cursor.execute('''
            INSERT INTO turnos (nombre, fecha, hora)
            VALUES (?, ?, ?)
            ''', (nombre, fecha_obj.strftime('%Y-%m-%d'), hora))
            conn.commit()
            return True, "Turno registrado exitosamente"
    else:
        dia_fijo = obtener_dia_fijo(nombre)
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return False, f"Este paciente solo puede tomar turnos los {dias[dia_fijo[0]]} a las {dia_fijo[1]}"


# Interfaz de Streamlit
st.title("Sistema Gestor de Pacientes - Consultorio Psicopedagógico")

menu = st.sidebar.selectbox(
    "Seleccione una opción", 
    ["Registrar Paciente", "Lista de Pacientes", "Registrar Sesión", "Calendario de Turnos"]
)

if menu == "Registrar Paciente":
    st.header("Registrar un nuevo paciente")
    nombre = st.text_input("Nombre")
    apellido = st.text_input("Apellido")
    dni = st.text_input("DNI")
    domicilio = st.text_input("Domicilio")
    # Mostrar la fecha de nacimiento y la edad calculada
    col1, col2 = st.columns(2)
    with col1:
        fecha_nacimiento = st.date_input("Fecha de Nacimiento", min_value=datetime(1960, 1, 1), max_value=datetime.today())
    with col2:
        edad = calcular_edad(fecha_nacimiento)
        if edad is not None:
            st.info(f"Edad: {edad} años")
    # fecha_nacimiento = st.date_input("Fecha de Nacimiento", min_value=datetime(1960, 1, 1), max_value=datetime.today())
    nombre_padre = st.text_input("Nombre del Padre/Tutor")
    telefono_padre = st.text_input("Teléfono del Padre/Tutor")
    nombre_madre = st.text_input("Nombre de la Madre/Tutora")
    telefono_madre = st.text_input("Teléfono de la Madre/Tutora")
    nombre_familiar = st.text_input("Nombre de Otro Familiar")
    telefono_familiar = st.text_input("Teléfono del Familiar")
    motivo_consulta = st.text_area("Motivo de Consulta")
    datos_escolares = st.text_area("Datos Escolares")

    if st.button("Guardar Paciente"):
        agregar_paciente(nombre, apellido, dni, fecha_nacimiento, nombre_padre, telefono_padre, nombre_madre, telefono_madre, nombre_familiar, telefono_familiar, domicilio, motivo_consulta, datos_escolares)
        st.success("Paciente registrado correctamente")

elif menu == "Lista de Pacientes":
    st.header("Lista de Pacientes")
    
    # Obtener DataFrame de pacientes
    df_pacientes = obtener_pacientes_df()
    
    # Agregar columna de edad
    df_pacientes['edad'] = df_pacientes['fecha_nacimiento'].apply(calcular_edad)
    
    # Barra de búsqueda
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Buscar paciente por nombre, apellido o DNI", "")
    with col2:
        sort_by = st.selectbox("Ordenar por:", ["Apellido", "Nombre", "Edad", "Fecha de Nacimiento"])
    
    # Filtrar y ordenar pacientes 
    if search_term:
        mask = (
            df_pacientes['nombre'].str.contains(search_term, case=False, na=False) |
            df_pacientes['apellido'].str.contains(search_term, case=False, na=False) |
            df_pacientes['dni'].str.contains(search_term, case=False, na=False)
        )
        df_filtrado = df_pacientes[mask]
    else:
        df_filtrado = df_pacientes

    # Ordenar pacientes
    if sort_by == "Apellido":
        df_filtrado = df_filtrado.sort_values('apellido')
    elif sort_by == "Nombre":
        df_filtrado = df_filtrado.sort_values('nombre')
    elif sort_by == "Edad":
        df_filtrado = df_filtrado.sort_values('edad', ascending=False)
    else:  # Fecha de Nacimiento
        df_filtrado = df_filtrado.sort_values('fecha_nacimiento', ascending=False)

    st.info(f"Total de pacientes: {len(df_filtrado)}")

    # Mostrar tabla de resumen [código existente sin cambios]
    if not df_filtrado.empty:
        tabla_resumen = pd.DataFrame({
            'Nombre Completo': df_filtrado['nombre'] + " " + df_filtrado['apellido'],
            'DNI': df_filtrado['dni'],
            'Edad': df_filtrado['edad'].apply(lambda x: f"{x} años" if pd.notnull(x) else "N/A"),
            'Fecha Nac.': df_filtrado['fecha_nacimiento'],
            'Tel. Padre': df_filtrado['telefono_padre'],
            'Tel. Madre': df_filtrado['telefono_madre']
        })


        st.dataframe(tabla_resumen, use_container_width=True)

        # Lista de pacientes con detalles expandibles
        for _, paciente in df_filtrado.iterrows():
            # Obtener estadísticas de sesiones
            stats = obtener_estadisticas_sesiones(paciente['id'])
            ultima_sesion = obtener_ultima_sesion(paciente['id'])
            
            with st.expander(f"📋 {paciente['nombre']} {paciente['apellido']} - DNI: {paciente['dni']}"):
                # Primera fila: Información general y estadísticas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Información Personal**")
                    st.write(f"Fecha Nac.: {paciente['fecha_nacimiento']}")
                    st.write(f"Edad: {paciente['edad']} años")
                    st.write(f"Domicilio: {paciente['domicilio']}")
                
                with col2:
                    st.markdown("**Información de Contacto**")
                    st.write(f"Padre/Tutor: {paciente['nombre_padre']}")
                    st.write(f"Tel. Padre: {paciente['telefono_padre']}")
                    st.write(f"Madre/Tutora: {paciente['nombre_madre']}")
                    st.write(f"Tel. Madre: {paciente['telefono_madre']}")
                
                with col3:
                    st.markdown("**Estadísticas de Sesiones**")
                    st.write(f"Total Sesiones: {stats['total_sesiones']}")
                    st.write(f"✅ Sesiones Asistidas: {stats['sesiones_asistidas']}")
                    st.write(f"💰 Sesiones Pagadas: {stats['sesiones_pagadas']}")
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
                    nuevo_nombre = st.text_input("Nombre", paciente['nombre'])
                    nuevo_apellido = st.text_input("Apellido", paciente['apellido'])
                    nuevo_dni = st.text_input("DNI", paciente['dni'])
                    nuevo_domicilio = st.text_input("Domicilio", paciente['domicilio'])
                    nueva_fecha = st.date_input("Fecha de Nacimiento", 
                                              datetime.strptime(paciente['fecha_nacimiento'], '%Y-%m-%d').date() 
                                              if paciente['fecha_nacimiento'] else None)
                    nuevo_nombre_padre = st.text_input("Nombre del Padre", paciente['nombre_padre'])
                    nuevo_tel_padre = st.text_input("Teléfono del Padre", paciente['telefono_padre'])
                    nuevo_nombre_madre = st.text_input("Nombre de la Madre", paciente['nombre_madre'])
                    nuevo_tel_madre = st.text_input("Teléfono de la Madre", paciente['telefono_madre'])
                    nuevo_nombre_familiar = st.text_input("Nombre del Familiar", paciente['nombre_familiar'])
                    nuevo_tel_familiar = st.text_input("Teléfono del Familiar", paciente['telefono_familiar'])
                    nuevo_motivo = st.text_area("Motivo de Consulta", paciente['motivo_consulta'])
                    nuevos_datos_escolares = st.text_area("Datos Escolares", paciente['datos_escolares'])

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Guardar Cambios"):
                            actualizar_paciente(
                                paciente['id'], nuevo_nombre, nuevo_apellido, nuevo_dni, 
                                nueva_fecha, nuevo_nombre_padre, nuevo_tel_padre,
                                nuevo_nombre_madre, nuevo_tel_madre, nuevo_nombre_familiar,
                                nuevo_tel_familiar, nuevo_domicilio, nuevo_motivo, 
                                nuevos_datos_escolares
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
                            padding: 10px;
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
                    
                    if st.button("❌ Cerrar Sesiones"):
                        st.session_state.viewing_sessions = None
                        st.rerun()
                    else:
                        st.warning("No se encontraron pacientes con los criterios de búsqueda especificados.")

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
    st.title("Calendario de Turnos")
    
    # Crear pestañas para separar la vista de turnos y el registro
    tab1, tab2, tab3 = st.tabs(["📅 Ver Turnos", "➕ Registrar Turno", "⚙️ Configurar Días Fijos"])

    with tab1:
        st.header("Calendario de Turnos")

        # Selector de mes y año
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mes", range(1, 13), datetime.now().month - 1)
        with col2:
            año = st.selectbox("Año", range(2024, 2026), 0)
        
        # Obtener todos los turnos del mes seleccionado
        turnos_mes = obtener_turnos_mes(año, mes)
        
        # Obtener los días fijos
        cursor.execute('SELECT nombre, dia_semana, hora FROM dias_fijos ORDER BY dia_semana, hora')
        dias_fijos = cursor.fetchall()
        
        # Crear un calendario mensual
        import calendar
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
        .turno-fijo {{
            font-size: 0.8em;
            margin: 2px;
            padding: 2px;
            background-color: green;
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
        
        # Calcular los días fijos para el mes seleccionado
        dias_fijos_mes = {}
        for nombre, dia_semana, hora in dias_fijos:
            # Iterar sobre todas las semanas del mes
            for semana in cal:
                if semana[dia_semana] != 0:  # Si el día existe en esta semana
                    fecha = f"{año}-{str(mes).zfill(2)}-{str(semana[dia_semana]).zfill(2)}"
                    if fecha not in dias_fijos_mes:
                        dias_fijos_mes[fecha] = []
                    dias_fijos_mes[fecha].append((nombre, hora))
        
        # Añadir las semanas
        for semana in cal:
            tabla_html += "<tr>"
            for dia in semana:
                if dia == 0:
                    tabla_html += "<td></td>"
                else:
                    fecha = f"{año}-{str(mes).zfill(2)}-{str(dia).zfill(2)}"
                    tabla_html += f"<td><div style='font-weight: bold;'>{dia}</div>"
                    
                    # Añadir turnos regulares del día
                    if fecha in turnos_por_fecha:
                        for turno in turnos_por_fecha[fecha]:
                            tabla_html += f"<div class='turno'>{turno[3]} - {turno[1]}</div>"
                    
                    # Añadir turnos fijos del día
                    if fecha in dias_fijos_mes:
                        for nombre, hora in dias_fijos_mes[fecha]:
                            tabla_html += f"<div class='turno-fijo'>📌 {hora} - {nombre}</div>"
                    
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
        
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", min_value=datetime.today())
        with col2:
            # Crear lista de horarios disponibles (de 8:00 a 20:00)
            horarios = []
            hora_actual = datetime.strptime("08:00", "%H:%M")
            hora_fin = datetime.strptime("20:00", "%H:%M")
            
            while hora_actual < hora_fin:
                horarios.append(hora_actual.strftime("%H:%M"))
                hora_actual = hora_actual + timedelta(minutes=40)
            
            hora = st.selectbox("Hora", horarios)

        if 'turno_registrado' not in st.session_state:
            st.session_state.turno_registrado = False
        
        if st.button("Registrar Turno"):
            if nombre and fecha and hora:
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
        st.header("Configuración de Días Fijos")
        
        # Formulario para asignar día fijo
        nombre_paciente = st.text_input("Nombre del Paciente")
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dia_seleccionado = st.selectbox("Día de la semana", dias_semana)
        hora_fija = st.selectbox("Hora fija", horarios)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Asignar Día Fijo"):
                if nombre_paciente and dia_seleccionado and hora_fija:
                    if agregar_dia_fijo(nombre_paciente, dias_semana.index(dia_seleccionado), hora_fija):
                        st.success(f"Día fijo asignado: {dia_seleccionado} a las {hora_fija}")
                        st.rerun()
                    else:
                        st.error("Este paciente ya tiene un día fijo asignado")
                else:
                    st.warning("Complete todos los campos")
        
        with col2:
            if st.button("Eliminar Día Fijo"):
                if nombre_paciente:
                    eliminar_dia_fijo(nombre_paciente)
                    st.success("Día fijo eliminado correctamente")
                    st.rerun()
                else:
                    st.warning("Ingrese el nombre del paciente")
        
        # Mostrar lista de días fijos asignados
        st.subheader("Días Fijos Asignados")
        cursor.execute('SELECT nombre, dia_semana, hora FROM dias_fijos ORDER BY dia_semana, hora')
        dias_fijos = cursor.fetchall()
        
        if dias_fijos:
            for paciente in dias_fijos:
                st.write(f"**{paciente[0]}**: {dias_semana[paciente[1]]} a las {paciente[2]}")
        else:
            st.info("No hay días fijos asignados")

conn.close()
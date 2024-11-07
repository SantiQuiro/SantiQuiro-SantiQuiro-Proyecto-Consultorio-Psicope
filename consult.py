import streamlit as st
import sqlite3
import pathlib
from datetime import datetime
import pandas as pd


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
    

# Función para cargar CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargar CSS si es necesario
css_path = pathlib.Path("estilo.css")
load_css(css_path)

# Conexión a la base de datos SQLite
conn = sqlite3.connect('consultorio.db')
cursor = conn.cursor()

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
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
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

def agregar_sesion(paciente_id, fecha, notas):
    cursor.execute('INSERT INTO sesiones (paciente_id, fecha, notas) VALUES (?, ?, ?)',
                   (paciente_id, fecha, notas))
    conn.commit()

def obtener_sesiones(paciente_id):
    cursor.execute('SELECT * FROM sesiones WHERE paciente_id = ?', (paciente_id,))
    return cursor.fetchall()

def eliminar_sesion(sesion_id):
    cursor.execute('DELETE FROM sesiones WHERE id = ?', (sesion_id,))
    conn.commit()

# Interfaz de Streamlit
st.title("Sistema Gestor de Pacientes - Consultorio Psicopedagógico")

menu = st.sidebar.selectbox("Seleccione una opción", ["Registrar Paciente", "Lista de Pacientes", "Registrar Sesión"])

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
    
    # Filtrar y ordenar pacientes [código existente sin cambios]
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
            with st.expander(f"📋 Detalles de {paciente['nombre']} {paciente['apellido']}"):
                # Información del paciente [código existente]
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Información Personal**")
                    st.write(f"DNI: {paciente['dni']}")
                    st.write(f"Fecha Nac.: {paciente['fecha_nacimiento']}")
                    st.write(f"Edad: {paciente['edad']} años")
                    st.write(f"Domicilio: {paciente['domicilio']}")

                with col2:
                    st.markdown("**Información de Contacto**")
                    st.write(f"Padre/Tutor: {paciente['nombre_padre']}")
                    st.write(f"Tel. Padre: {paciente['telefono_padre']}")
                    st.write(f"Madre/Tutora: {paciente['nombre_madre']}")
                    st.write(f"Tel. Madre: {paciente['telefono_madre']}")
                    if paciente['nombre_familiar']:
                        st.write(f"Otro Familiar: {paciente['nombre_familiar']}")
                        st.write(f"Tel. Familiar: {paciente['telefono_familiar']}")

                with col3:
                    st.markdown("**Información Clínica**")
                    st.write("Motivo de Consulta:")
                    st.text_area("", paciente['motivo_consulta'], height=100, key=f"motivo_{paciente['id']}", disabled=True)
                    st.write("Datos Escolares:")
                    st.text_area("", paciente['datos_escolares'], height=100, key=f"escolar_{paciente['id']}", disabled=True)

                # Botones de acción
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
                        # Crear un contenedor con borde para las sesiones
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
                            st.markdown(f'<div class="session-container">', unsafe_allow_html=True)
                            col1, col2 = st.columns([5, 1])
                            with col1:
                                st.markdown("**Fecha:**")
                                st.write(sesion[2])
                                st.markdown("**Notas:**")
                                st.text_area("", sesion[3], height=150, key=f"notas_sesion_{sesion[0]}", disabled=True)
                            with col2:
                                if st.button("🗑️", key=f"del_session_{sesion[0]}"):
                                    eliminar_sesion(sesion[0])
                                    st.success("Sesión eliminada correctamente")
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
        paciente_seleccionado = st.selectbox("Seleccione un paciente", [f"{p[1]} {p[2]}" for p in pacientes])
        paciente_id = [p[0] for p in pacientes if f"{p[1]} {p[2]}" == paciente_seleccionado][0]
        fecha = st.date_input("Fecha de la sesión", datetime.now())
        notas = st.text_area("Notas de la sesión")

        if st.button("Guardar Sesión"):
            agregar_sesion(paciente_id, fecha, notas)
            st.success("Sesión registrada correctamente")

    else:
        st.warning("No hay pacientes registrados. Registre al menos un paciente antes de registrar una sesión.")

# Cerrar la conexión
conn.close()

import io
import platform
import json
import time
import streamlit as st
import paho.mqtt.client as mqtt

# Configuración de la página con temática de expedición geológica
st.set_page_config(
    page_title="Geosensor — Estación de Monitoreo de Taludes",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# ESTILOS CSS: TEMÁTICA DE MONTAÑAS, ROCAS Y AGUA
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Fondo simulando la atmósfera montañosa / terreno rocoso */
    .stApp {
        background-color: #1a2118 !important;
        background-image: linear-gradient(rgba(26, 33, 24, 0.92), rgba(15, 20, 14, 0.95)),
                          radial-gradient(circle at 50% 20%, #2e3d2b 0%, transparent 60%);
    }

    /* Sidebar estilo campamento base */
    [data-testid="stSidebar"] {
        background-color: #263323 !important;
        border-right: 3px solid #4a5c43;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2ebd8 !important;
    }

    /* Tarjetas estilo "Bloque de Roca / Monolito" */
    .rock-panel {
        background: #2c3628 !important;
        border: 2px solid #556b4d;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        color: #f0f4ec !important;
    }

    /* Panel de Alerta / Seguridad */
    .danger-safe {
        background: #1e3322 !important;
        border: 2px solid #2e7d32;
        border-radius: 12px;
        padding: 20px;
        color: #a5d6a7 !important;
    }

    .danger-warning {
        background: #3b2b1e !important;
        border: 2px solid #ef6c00;
        border-radius: 12px;
        padding: 20px;
        color: #ffccbc !important;
    }

    .danger-high {
        background: #3b1e1e !important;
        border: 2px solid #c62828;
        border-radius: 12px;
        padding: 20px;
        color: #ffab91 !important;
    }

    /* Títulos con tipografía de expedición */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #e2ebd8 !important;
    }

    /* Elementos gráficos simulando el relieve (Rocas y Ríos) */
    .landscape-bar {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-bottom: 20px;
        font-size: 1.5rem;
    }

    /* Botones de expedición */
    .stButton button {
        background: #556b4d !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 1px solid #738f68 !important;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: #6b8561 !important;
        border-color: #a5d6a7 !important;
        transform: translateY(-2px);
    }

    p, span, label {
        color: #c2d1b6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VARIABLES DE ESTADO
# ─────────────────────────────────────────────
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

# ─────────────────────────────────────────────
# FUNCIÓN DE CONEXIÓN MQTT
# ─────────────────────────────────────────────
def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT del simulador Wokwi"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# ─────────────────────────────────────────────
# SIDEBAR - CAMPAMENTO BASE Y CONFIGURACIÓN
# ─────────────────────────────────────────────
with st.sidebar:
    st.subheader('⛺ Campamento Base (MQTT)')
    st.markdown("Configura los enlaces de radio con el nodo sensor en la zona rocosa.")
    
    broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com',
                           help='Dirección del broker MQTT')
    
    port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535,
                           help='Puerto del broker (ej. 1883)')
    
    topic = st.text_input('Tópico de la Zona', value='Sensor/THP2',
                          help='Tópico MQTT del sensor en el talud')
    
    client_id = st.text_input('ID de Expedición', value='geologo_client_01',
                              help='Identificador del equipo de campo')

    st.divider()
    with st.expander('ℹ️ Manual de Campo', expanded=False):
        st.markdown("""
        **Guía de Supervivencia Geológica:**
        * **Humedad Alta (>80%):** Aumenta la presión de poros en las fisuras de la roca. Riesgo inminente de desprendimiento por saturación.
        * **Temperaturas Extremas:** Ciclos de congelación/descongelación fracturan la roca (meteorización física).
        * **Cuerpos de Agua:** Los arroyos y filtraciones aumentan el caudal y aceleran la erosión basal del talud.
        """)

# ─────────────────────────────────────────────
# ENCABEZADO GEOLÓGICO Y PAISAJE SIMULADO
# ─────────────────────────────────────────────
st.markdown("""
<div class="rock-panel" style="text-align: center;">
    <div class="landscape-bar">
        🏔️ ⛰️ 🧗 💧 🌊 ⛰️ 🏔️
    </div>
    <h1>Monitoreo Geotécnico de Taludes</h1>
    <p style="font-size: 1.05rem; letter-spacing: 0.5px;">
        Sistema de telemetría en tiempo real para evaluar la estabilidad de zonas rocosas inestables y determinar ventanas seguras de observación científica.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ACCIÓN DE TELEMETRÍA
# ─────────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button('📡 Sincronizar Sensores del Talud', use_container_width=True):
        with st.spinner('🛰️ Recibiendo telemetría satelital / MQTT desde la zona de riesgo...'):
            sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
            st.session_state.sensor_data = sensor_data

# ─────────────────────────────────────────────
# PROCESAMIENTO Y VISUALIZACIÓN DE DATOS
# ─────────────────────────────────────────────
if st.session_state.sensor_data:
    st.divider()
    st.subheader('📊 Estado Actual del Ecosistema Rocoso')
    
    data = st.session_state.sensor_data
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Pérdida de señal con el sensor: {data['error']}")
    else:
        st.success('✅ Enlace establecido con éxito. Datos telemetricos actualizados.')
        
        if isinstance(data, dict):
            # Extraer valores comunes si existen (temperatura, humedad)
            temp = data.get('temperature', data.get('temp', data.get('Temperatura', 25)))
            hum = data.get('humidity', data.get('hum', data.get('Humedad', 50)))
            
            try:
                temp_val = float(temp)
                hum_val = float(hum)
            except:
                temp_val = 25.0
                hum_val = 50.0

            # Mostrar métricas en tarjetas de roca
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key.upper(), value=value)
            
            st.markdown("<br>", unsafe_allow_html=True)

            # ─────────────────────────────────────────────
            # ANÁLISIS DE RIESGO PARA GEÓLOGOS (EVALUACIÓN DE CAMPO)
            # ─────────────────────────────────────────────
            st.markdown("### 🧗‍♂️ Evaluación de Ventana de Ingreso para Investigadores")
            
            # Lógica de seguridad geológica basada en humedad y temperatura
            if hum_val > 80.0:
                estado_clase = "danger-high"
                recomendacion = "🛑 **ALERTA ROJA - ZONA INESTABLE:** La humedad supera el 80%. Existe alta probabilidad de saturación de agua en las diaclasas y riesgo inminente de caída de bloques o deslizamiento masivo. **PROHIBIDO EL ACCESO AL TALUD.**"
            elif hum_val > 60.0 or temp_val < 2.0 or temp_val > 38.0:
                estado_clase = "danger-warning"
                recomendacion = "⚠️ **PRECAUCIÓN MODERADA:** Las condiciones ambientales son semifavorables pero inestables. Se registran niveles de humedad o temperaturas de riesgo térmico/mecánico sobre la roca. **Acceso restringido solo con equipo de protección y monitoreo visual constante.**"
            else:
                estado_clase = "danger-safe"
                recomendacion = "✅ **VENTANA ÓPTIMA DE ESTUDIO:** Los parámetros de temperatura y humedad se encuentran en rangos de estabilidad estrcutural. **Momento excelente para que los investigadores se acerquen a tomar muestras y observaciones.**"

            st.markdown(f"""
            <div class="{estado_clase}">
                <h4>🔍 Dictamen Geotécnico Automatizado:</h4>
                <p style="font-size: 1.05rem; margin-top: 8px;">{recomendacion}</p>
            </div>
            """, unsafe_allow_html=True)

            # Detalles del entorno simulado (Ríos y laderas)
            st.markdown("<br>", unsafe_allow_html=True)
            col_geo1, col_geo2 = st.columns(2)
            
            with col_geo1:
                st.markdown("""
                <div class="rock-panel">
                    <h4>🌊 Comportamiento Hídrico y Arroyo</h4>
                    <p>Las mediciones de humedad nos ayudan a inferir el caudal del arroyo base en el cañón. Un incremento rápido indica escorrentía superficial acelerada que debimenta la base del talud rocoso.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_geo2:
                st.markdown("""
                <div class="rock-panel">
                    <h4>⛰️ Integridad del Estrato Rocoso</h4>
                    <p>Las variaciones térmicas bruscas combinadas con la humedad provocan contracción y expansión térmica en las fisuras (meteorización mecánica), predisponiendo desprendimientos súbitos.</p>
                </div>
                """, unsafe_allow_html=True)

            # JSON Completo
            with st.expander('📂 Ver trama de datos en crudo (MQTT Raw Payload)'):
                st.json(data)
        else:
            st.code(data)
else:
    st.markdown("""
    <div class="rock-panel" style="text-align: center;">
        <h3>⏳ Esperando transmisión de telemetría...</h3>
        <p>Haz clic en el botón superior <b>"Sincronizar Sensores del Talud"</b> para capturar la lectura actual del broker MQTT.</p>
    </div>
    """, unsafe_allow_html=True)

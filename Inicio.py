import io
import platform
import json
import time
import streamlit as st
import paho.mqtt.client as mqtt

# Configuración de la página con temática de rocas y agua (Café y Azul)
st.set_page_config(
    page_title="Geosensor — Estación de Monitoreo de Taludes",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# ESTILOS CSS: TEMÁTICA DE MONTAÑAS CAFÉ Y CUERPOS DE AGUA AZULES
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Fondo simulando el terreno rocoso (café oscuro) con destellos de agua */
    .stApp {
        background-color: #181514 !important;
        background-image: linear-gradient(rgba(24, 21, 20, 0.94), rgba(12, 10, 9, 0.96)),
                          radial-gradient(circle at 50% 20%, #1e293b 0%, transparent 70%);
    }

    /* Sidebar estilo campamento base (café terracota) */
    [data-testid="stSidebar"] {
        background-color: #27211d !important;
        border-right: 3px solid #4a3b32;
    }
    
    [data-testid="stSidebar"] * {
        color: #f3f4f6 !important;
    }

    /* Tarjetas estilo "Bloque de Roca / Monolito de Tierra" */
    .rock-panel {
        background: #332924 !important;
        border: 2px solid #5c4a40;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        color: #f3f4f6 !important;
    }

    /* Paneles de Estado / Alerta con acentos azules de agua y tierra */
    .danger-safe {
        background: #0f172a !important;
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 20px;
        color: #38bdf8 !important;
    }

    .danger-warning {
        background: #3a2518 !important;
        border: 2px solid #d97706;
        border-radius: 12px;
        padding: 20px;
        color: #fcd34d !important;
    }

    .danger-high {
        background: #3b1e1e !important;
        border: 2px solid #dc2626;
        border-radius: 12px;
        padding: 20px;
        color: #f87171 !important;
    }

    /* Títulos con tipografía de expedición */
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #f3f4f6 !important;
    }

    /* Elementos gráficos simulando el relieve rocoso y los ríos */
    .landscape-bar {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-bottom: 20px;
        font-size: 1.5rem;
    }

    /* Botones estilo expedición con acento azul agua */
    .stButton button {
        background: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 1px solid #38bdf8 !important;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: #0369a1 !important;
        border-color: #bae6fd !important;
        transform: translateY(-2px);
    }

    p, span, label {
        color: #d1d5db !important;
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
    st.markdown("Configura los enlaces de radio con los sensores instalados en la ladera rocosa y los cauces de agua.")
    
    broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com',
                           help='Dirección del broker MQTT')
    
    port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535,
                           help='Puerto del broker (ej. 1883)')
    
    topic = st.text_input('Tópico de la Zona', value='Sensor/THP2',
                          help='Tópico MQTT del sensor en el talud')
    
    client_id = st.text_input('ID de Expedición', value='geologo_client_01',
                              help='Identificador del equipo de campo')

    st.divider()
    with st.expander('ℹ️ Manual de Campo Geológico', expanded=False):
        st.markdown("""
        **Guía de Seguridad en Montaña:**
        * **Humedad Alta (>80%):** Alerta de saturación hídrica en las filtraciones de los acuíferos subterráneos y fisuras de la roca.
        * **Temperaturas Extremas:** Provocan dilatación térmica y contracción en los bloques de piedra (meteorización).
        * **Cuerpos de Agua y Ríos:** El incremento en la humedad ambiental suele correlacionarse con crecidas repentinas en los arroyos del cañón.
        """)

# ─────────────────────────────────────────────
# ENCABEZADO GEOLÓGICO CON TEMA CAFÉ Y AZUL
# ─────────────────────────────────────────────
st.markdown("""
<div class="rock-panel" style="text-align: center;">
    <div class="landscape-bar">
        🏔️ 🪨 💧 🌊 🟦 🪨 🏔️
    </div>
    <h1>Monitoreo Geotécnico: Taludes y Cuerpos de Agua</h1>
    <p style="font-size: 1.05rem; letter-spacing: 0.5px; color: #94a3b8 !important;">
        Estación inteligente de telemetría en tiempo real. Analiza las condiciones de humedad y temperatura de la roca para garantizar ventanas de investigación seguras.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ACCIÓN DE TELEMETRÍA
# ─────────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button('📡 Sincronizar Sensores de la Zona', use_container_width=True):
        with st.spinner('🛰️ Recibiendo datos telemétricos del nodo en la roca...'):
            sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
            st.session_state.sensor_data = sensor_data

# ─────────────────────────────────────────────
# PROCESAMIENTO Y VISUALIZACIÓN DE DATOS
# ─────────────────────────────────────────────
if st.session_state.sensor_data:
    st.divider()
    st.subheader('📊 Estado Actual del Ecosistema (Roca y Agua)')
    
    data = st.session_state.sensor_data
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Pérdida de enlace satelital con el sensor: {data['error']}")
    else:
        st.success('✅ Conexión establecida con éxito. Telemetría de campo actualizada.')
        
        if isinstance(data, dict):
            # Extraer valores comunes si existen
            temp = data.get('temperature', data.get('temp', data.get('Temperatura', 25)))
            hum = data.get('humidity', data.get('hum', data.get('Humedad', 50)))
            
            try:
                temp_val = float(temp)
                hum_val = float(hum)
            except:
                temp_val = 25.0
                hum_val = 50.0

            # Mostrar métricas en tarjetas de roca/tierra
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key.upper(), value=value)
            
            st.markdown("<br>", unsafe_allow_html=True)

            # ─────────────────────────────────────────────
            # ANÁLISIS DE RIESGO PARA GEÓLOGOS
            # ─────────────────────────────────────────────
            st.markdown("### 🧗‍♂️ Evaluación de Ventana de Ingreso al Terreno")
            
            if hum_val > 80.0:
                estado_clase = "danger-high"
                recomendacion = "🛑 **ALERTA ROJA - ZONA DE ALTO RIESGO:** La humedad supera el 80%. Las filtraciones de agua en la roca aumentan drásticamente la presión hidrostática interna. **Peligro inminente de desprendimiento. Prohibido el acceso.**"
            elif hum_val > 60.0 or temp_val < 2.0 or temp_val > 38.0:
                estado_clase = "danger-warning"
                recomendacion = "⚠️ **PRECAUCIÓN MODERADA:** Los niveles hídricos y térmicos muestran inestabilidad en los estratos rocosos. **Acceso restringido exclusivamente con equipo de protección y supervisión visual del caudal del río.**"
            else:
                estado_clase = "danger-safe"
                recomendacion = "💙 **VENTANA ÓPTIMA DE CAMPO:** Los parámetros de humedad y temperatura se encuentran estables. **Momento seguro para que los geólogos se acerquen a la base rocosa para realizar mediciones y toma de muestras.**"

            st.markdown(f"""
            <div class="{estado_clase}">
                <h4>🌊 Dictamen Hidrogeológico Automatizado:</h4>
                <p style="font-size: 1.05rem; margin-top: 8px;">{recomendacion}</p>
            </div>
            """, unsafe_allow_html=True)

            # Detalles del entorno simulado (Ríos y laderas de roca)
            st.markdown("<br>", unsafe_allow_html=True)
            col_geo1, col_geo2 = st.columns(2)
            
            with col_geo1:
                st.markdown("""
                <div class="rock-panel">
                    <h4>💧 Comportamiento de Cuerpos de Agua</h4>
                    <p>El monitoreo de humedad ambiental y del suelo adyacente nos indica el nivel de saturación de los mantos acuíferos que alimentan el río del valle. Evita descensos al cañón si hay picos repentinos de humedad.</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_geo2:
                st.markdown("""
                <div class="rock-panel">
                    <h4>🪨 Estabilidad de la Pared Rocosa</h4>
                    <p>Las rocas expuestas absorben humedad ambiental, reblandeciendo las arcillas internas de las fisuras. Combinado con los ciclos térmicos, esto define el coeficiente de seguridad para la expedición.</p>
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
        <h3>⏳ Esperando transmisión de telemetría del sensor...</h3>
        <p>Haz clic en el botón superior <b>"Sincronizar Sensores de la Zona"</b> para enlazar con el broker MQTT y obtener las lecturas actuales de la montaña.</p>
    </div>
    """, unsafe_allow_html=True)

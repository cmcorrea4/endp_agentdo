import streamlit as st
import requests
import json

# Configuración de la página
st.set_page_config(
    page_title="Agente de IA",
    page_icon="🤖",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .response-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Título y descripción de la aplicación
st.markdown("<h1 class='main-header'>Agente de Inteligencia Artificial</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Interactúa con nuestro agente de IA para obtener respuestas inteligentes.</p>", unsafe_allow_html=True)

# El historial de chat ya se inicia en initialize_session_vars()

# Función para enviar solicitud al endpoint de IA
def query_ai_endpoint(prompt, history=None):
    try:
        # Obtener URL y token de API desde session_state
        api_url = st.session_state.api_url
        api_key = st.session_state.api_key
        
        if not api_url or not api_key:
            return {"error": "Las credenciales de API no están configuradas correctamente."}
        
        # Preparar la solicitud
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Usar los valores de los sliders
        payload = {
            "prompt": prompt,
            "max_tokens": max_length,
            "temperature": temperature
        }
        
        # Añadir historial si está disponible
        if history:
            payload["history"] = history
        
        # Enviar solicitud al endpoint
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Verificar respuesta
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error en la solicitud. Código: {response.status_code}",
                "details": response.text
            }
    
    except Exception as e:
        return {"error": f"Error al comunicarse con el endpoint de IA: {str(e)}"}

# Función para inicializar variables de sesión
def initialize_session_vars():
    if "is_configured" not in st.session_state:
        st.session_state.is_configured = False
    if "api_url" not in st.session_state:
        st.session_state.api_url = ""
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Inicializar variables
initialize_session_vars()

# Pantalla de configuración inicial si aún no se ha configurado
if not st.session_state.is_configured:
    st.markdown("<h2 class='subheader'>Configuración Inicial</h2>", unsafe_allow_html=True)
    
    st.info("Por favor, configura los parámetros de conexión para el agente de IA.")
    
    # Campos para la configuración
    api_url = st.text_input(
        "URL del Endpoint de IA", 
        placeholder="https://api.digitalocean.com/v1/ai/endpoints/your-endpoint-id",
        help="URL completa del endpoint de Digital Ocean"
    )
    
    api_key = st.text_input(
        "API Key", 
        type="password",
        placeholder="Ingresa tu API key de Digital Ocean",
        help="Tu clave de API para autenticar las solicitudes"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Guardar configuración"):
            if not api_url or not api_key:
                st.error("Por favor, ingresa tanto la URL como la API Key")
            else:
                # Guardar configuración en session_state
                st.session_state.api_url = api_url
                st.session_state.api_key = api_key
                st.session_state.is_configured = True
                st.success("¡Configuración guardada correctamente!")
                st.rerun()
    
    # Parar ejecución hasta que se configure
    st.stop()

# Una vez configurado, mostrar la interfaz normal
# Sidebar para configuración
st.sidebar.title("Configuración")

# Mostrar información de conexión actual
st.sidebar.success("✅ Configuración cargada")
with st.sidebar.expander("Ver configuración actual"):
    st.code(f"URL: {st.session_state.api_url}\nAPI Key: {'*'*10}")
    if st.button("Editar configuración"):
        st.session_state.is_configured = False
        st.rerun()

# Opciones de modelo (si hay varios disponibles)
model_option = st.sidebar.selectbox(
    "Seleccione el modelo",
    ["GPT-3.5", "GPT-4", "Claude", "Personalizado"]
)

# Ajustes avanzados
with st.sidebar.expander("Ajustes avanzados"):
    temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                          help="Valores más altos generan respuestas más creativas, valores más bajos generan respuestas más deterministas.")
    max_length = st.slider("Longitud máxima", min_value=100, max_value=2000, value=1000, step=100,
                          help="Número máximo de tokens en la respuesta.")

# Sección para probar conexión con el endpoint
with st.sidebar.expander("Probar conexión"):
    if st.button("Verificar endpoint"):
        with st.spinner("Verificando conexión..."):
            try:
                api_url = st.session_state.api_url
                api_key = st.session_state.api_key
                
                if not api_url or not api_key:
                    st.error("Falta configuración de URL o API key")
                else:
                    # Petición simple para verificar conexión
                    headers = {"Authorization": f"Bearer {api_key}"}
                    response = requests.get(f"{api_url}/health", headers=headers)
                    
                    if response.status_code == 200:
                        st.success("Conexión exitosa con el endpoint")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error de conexión: {str(e)}")

# Mostrar historial de conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada para la consulta
prompt = st.chat_input("Escribe tu mensaje aquí...")

# Procesar la entrada del usuario
if prompt:
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Preparar historial para la API (solo si la API lo soporta)
    api_history = []
    for msg in st.session_state.messages[:-1]:  # Excluir el mensaje actual
        api_history.append({"role": msg["role"], "content": msg["content"]})
    
    # Mostrar indicador de carga mientras se procesa
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            # Llamar al endpoint de IA
            response = query_ai_endpoint(prompt, api_history)
            
            if "error" in response:
                st.error(f"Error: {response['error']}")
                if "details" in response:
                    with st.expander("Detalles del error"):
                        st.code(response["details"])
            else:
                # Mostrar respuesta del asistente
                response_text = response.get("response", "No se recibió respuesta del modelo.")
                st.markdown(response_text)
                
                # Añadir respuesta al historial
                st.session_state.messages.append({"role": "assistant", "content": response_text})

# Sección de opciones adicionales
st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.experimental_rerun()

with col2:
    if st.button("💾 Guardar conversación"):
        # Convertir historial a formato JSON
        conversation_data = json.dumps(st.session_state.messages, indent=2)
        
        # Crear archivo para descargar
        st.download_button(
            label="Descargar JSON",
            data=conversation_data,
            file_name="conversacion.json",
            mime="application/json",
        )

# Pie de página
st.markdown("<div class='footer'>Desarrollado con Streamlit y Digital Ocean AI © 2025</div>", unsafe_allow_html=True)

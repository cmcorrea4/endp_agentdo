import streamlit as st
import requests
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Agente DigitalOcean",
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

# Función para inicializar variables de sesión
def initialize_session_vars():
    if "is_configured" not in st.session_state:
        st.session_state.is_configured = False
    if "agent_id" not in st.session_state:
        st.session_state.agent_id = ""
    if "access_token" not in st.session_state:
        st.session_state.access_token = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Inicializar variables
initialize_session_vars()

# Título y descripción de la aplicación
st.markdown("<h1 class='main-header'>Agente de DigitalOcean</h1>", unsafe_allow_html=True)

# Pantalla de configuración inicial si aún no se ha configurado
if not st.session_state.is_configured:
    st.markdown("<h2 class='subheader'>Configuración Inicial</h2>", unsafe_allow_html=True)
    
    st.info("Por favor, configura los parámetros para conectar con tu agente de DigitalOcean.")
    
    # Campos para la configuración
    agent_id = st.text_input(
        "ID del Agente", 
        placeholder="Ejemplo: 12345",
        help="ID numérico del agente de DigitalOcean"
    )
    
    access_token = st.text_input(
        "Token de Acceso", 
        type="password",
        placeholder="Ingresa tu token de acceso a DigitalOcean",
        help="Tu token de acceso para autenticar las solicitudes a la API de DigitalOcean"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Guardar configuración"):
            if not agent_id or not access_token:
                st.error("Por favor, ingresa tanto el ID del agente como el token de acceso")
            else:
                # Guardar configuración en session_state
                st.session_state.agent_id = agent_id
                st.session_state.access_token = access_token
                st.session_state.is_configured = True
                st.success("¡Configuración guardada correctamente!")
                time.sleep(1)  # Breve pausa para mostrar el mensaje de éxito
                st.rerun()
    
    # Parar ejecución hasta que se configure
    st.stop()

# Una vez configurado, mostrar la interfaz normal
st.markdown("<p class='subheader'>Interactúa con tu agente de DigitalOcean.</p>", unsafe_allow_html=True)

# Sidebar para configuración
st.sidebar.title("Configuración")

# Mostrar información de conexión actual
st.sidebar.success("✅ Configuración cargada")
with st.sidebar.expander("Ver configuración actual"):
    st.code(f"ID del Agente: {st.session_state.agent_id}\nToken de Acceso: {'*'*10}")
    if st.button("Editar configuración"):
        st.session_state.is_configured = False
        st.rerun()

# Ajustes avanzados
with st.sidebar.expander("Ajustes avanzados"):
    action_type = st.selectbox(
        "Tipo de acción",
        options=["Consulta general", "Iniciar", "Detener", "Reiniciar", "Personalizada"],
        index=0
    )
    
    # Si se selecciona acción personalizada, mostrar campo para ingresar la acción
    custom_action = ""
    if action_type == "Personalizada":
        custom_action = st.text_input("Acción personalizada", placeholder="Ejemplo: update")

# Función para enviar acción al agente
def send_agent_action(prompt, action=None):
    try:
        # Obtener datos de configuración
        agent_id = st.session_state.agent_id
        access_token = st.session_state.access_token
        
        if not agent_id or not access_token:
            return {"error": "Falta configuración del agente o token de acceso."}
        
        # Construir URL según el tipo de acción
        base_url = f"https://api.digitalocean.com/v2/agents/{agent_id}"
        
        if action == "Iniciar":
            endpoint_url = f"{base_url}/actions/start"
        elif action == "Detener":
            endpoint_url = f"{base_url}/actions/stop"
        elif action == "Reiniciar":
            endpoint_url = f"{base_url}/actions/restart"
        elif action == "Personalizada" and custom_action:
            endpoint_url = f"{base_url}/actions/{custom_action}"
        else:
            # Acción por defecto - general
            endpoint_url = f"{base_url}/actions"
        
        # Preparar headers con autenticación
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Preparar payload con el prompt del usuario
        payload = {
            "query": prompt,
            "parameters": {
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }
        
        # Enviar solicitud POST
        try:
            response = requests.post(endpoint_url, headers=headers, json=payload, timeout=60)
            
            # Verificar respuesta
            if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                try:
                    response_data = response.json()
                    
                    # Buscar la respuesta en diferentes campos posibles
                    for field in ["result", "data", "action", "message", "output", "response"]:
                        if field in response_data:
                            if isinstance(response_data[field], str):
                                return {"response": response_data[field]}
                            elif isinstance(response_data[field], dict):
                                for subfield in ["result", "message", "content", "output", "text"]:
                                    if subfield in response_data[field] and isinstance(response_data[field][subfield], str):
                                        return {"response": response_data[field][subfield]}
                    
                    # Si no encontramos un campo específico, devolvemos toda la respuesta
                    return {"response": json.dumps(response_data, indent=2)}
                    
                except ValueError:
                    # Si no es JSON, devolver el texto plano
                    return {"response": response.text}
            else:
                # Error en la respuesta
                error_message = f"Error en la solicitud. Código: {response.status_code}"
                try:
                    error_details = response.json()
                    return {"error": error_message, "details": json.dumps(error_details, indent=2)}
                except:
                    return {"error": error_message, "details": response.text}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Error en la solicitud HTTP: {str(e)}"}
        
    except Exception as e:
        return {"error": f"Error al comunicarse con el agente: {str(e)}"}

# Sección para probar conexión con el agente
with st.sidebar.expander("Probar conexión"):
    if st.button("Verificar agente"):
        with st.spinner("Verificando conexión..."):
            try:
                agent_id = st.session_state.agent_id
                access_token = st.session_state.access_token
                
                if not agent_id or not access_token:
                    st.error("Falta configuración del agente o token de acceso")
                else:
                    # Construir URL para verificar el estado del agente
                    check_url = f"https://api.digitalocean.com/v2/agents/{agent_id}"
                    
                    # Preparar headers
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Intentar obtener información del agente
                    try:
                        response = requests.get(check_url, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            st.success(f"✅ Conexión exitosa con el agente")
                            with st.expander("Detalles del agente"):
                                try:
                                    agent_info = response.json()
                                    st.json(agent_info)
                                except:
                                    st.code(response.text)
                        else:
                            st.error(f"❌ Error al conectar con el agente. Código: {response.status_code}")
                            with st.expander("Detalles del error"):
                                st.code(response.text)
                    except Exception as e:
                        st.error(f"Error de conexión: {str(e)}")
            except Exception as e:
                st.error(f"Error al verificar agente: {str(e)}")

# Mostrar historial de conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada para el mensaje
prompt = st.chat_input("Escribe tu mensaje aquí...")

# Procesar la entrada del usuario
if prompt:
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtener el tipo de acción seleccionado
    selected_action = action_type
    
    # Mostrar indicador de carga mientras se procesa
    with st.chat_message("assistant"):
        with st.spinner("Procesando..."):
            # Enviar acción al agente
            response = send_agent_action(prompt, selected_action)
            
            if "error" in response:
                st.error(f"Error: {response['error']}")
                if "details" in response:
                    with st.expander("Detalles del error"):
                        st.code(response["details"])
                
                # Añadir mensaje de error al historial
                error_msg = f"Lo siento, ocurrió un error al procesar tu solicitud: {response['error']}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                # Mostrar respuesta del asistente
                response_text = response.get("response", "No se recibió respuesta del agente.")
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
st.markdown("<div class='footer'>Agente de DigitalOcean © 2025</div>", unsafe_allow_html=True)

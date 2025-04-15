import streamlit as st
import requests
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Agente de DigitalOcean",
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
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "action_type" not in st.session_state:
        st.session_state.action_type = "text_completion"

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
        help="ID del agente de DigitalOcean con el que deseas interactuar"
    )
    
    api_key = st.text_input(
        "API Key de DigitalOcean", 
        type="password",
        placeholder="Ingresa tu API key",
        help="Tu clave de API para autenticar las solicitudes a DigitalOcean"
    )
    
    # Tipo de acción para el agente
    action_type = st.selectbox(
        "Tipo de Acción",
        options=["Completar Texto", "Responder Preguntas", "Generar Imágenes", "Personalizada"],
        index=0,
        help="Tipo de acción que deseas realizar con el agente"
    )
    
    # Mapear selección a valor interno
    action_type_value = "text_completion" if action_type == "Completar Texto" else \
                        "question_answering" if action_type == "Responder Preguntas" else \
                        "image_generation" if action_type == "Generar Imágenes" else "custom"
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Guardar configuración"):
            if not agent_id or not api_key:
                st.error("Por favor, ingresa tanto el ID del agente como la API Key")
            else:
                # Guardar configuración en session_state
                st.session_state.agent_id = agent_id
                st.session_state.api_key = api_key
                st.session_state.action_type = action_type_value
                st.session_state.is_configured = True
                st.success("¡Configuración guardada correctamente!")
                time.sleep(1)  # Breve pausa para mostrar el mensaje de éxito
                st.rerun()
    
    # Parar ejecución hasta que se configure
    st.stop()

# Una vez configurado, mostrar la interfaz normal
st.markdown("<p class='subheader'>Interactúa con tu agente de DigitalOcean para realizar acciones.</p>", unsafe_allow_html=True)

# Sidebar para configuración
st.sidebar.title("Configuración")

# Mostrar información de conexión actual
st.sidebar.success("✅ Configuración cargada")
with st.sidebar.expander("Ver configuración actual"):
    st.code(f"ID del Agente: {st.session_state.agent_id}\nAPI Key: {'*'*10}\nTipo de Acción: {st.session_state.action_type}")
    if st.button("Editar configuración"):
        st.session_state.is_configured = False
        st.rerun()

# Ajustes avanzados según el tipo de acción
with st.sidebar.expander("Ajustes avanzados"):
    if st.session_state.action_type == "text_completion" or st.session_state.action_type == "question_answering":
        temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                              help="Valores más altos generan respuestas más creativas, valores más bajos generan respuestas más deterministas.")
        max_length = st.slider("Longitud máxima", min_value=100, max_value=2000, value=1000, step=100,
                              help="Número máximo de tokens en la respuesta.")
    elif st.session_state.action_type == "image_generation":
        image_size = st.selectbox(
            "Tamaño de imagen",
            options=["256x256", "512x512", "1024x1024"],
            index=1
        )
        image_style = st.selectbox(
            "Estilo de imagen",
            options=["Natural", "Cartoon", "Artistic", "Realistic"],
            index=0
        )

# Función para enviar acción al agente de DigitalOcean
def send_agent_action(prompt, history=None):
    try:
        # Obtener datos desde session_state
        agent_id = st.session_state.agent_id
        api_key = st.session_state.api_key
        action_type = st.session_state.action_type
        
        if not agent_id or not api_key:
            return {"error": "Falta configuración de ID del agente o API key."}
        
        # Construir URL según el formato de DigitalOcean
        base_url = "https://api.digitalocean.com/v2/agents"
        if action_type in ["text_completion", "question_answering"]:
            # Para completar texto o responder preguntas
            endpoint_url = f"{base_url}/{agent_id}/actions"
        elif action_type == "image_generation":
            # Para generar imágenes
            endpoint_url = f"{base_url}/{agent_id}/images"
        else:
            # Para acción personalizada
            endpoint_url = f"{base_url}/{agent_id}/actions"
        
        # Preparar headers con autenticación
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Construir payload según el tipo de acción
        if action_type == "text_completion":
            payload = {
                "type": "completion",
                "input": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_length
                }
            }
            if history:
                payload["context"] = format_history_for_digitalocean(history)
                
        elif action_type == "question_answering":
            payload = {
                "type": "question_answering",
                "question": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_length
                }
            }
            if history:
                payload["context"] = format_history_for_digitalocean(history)
                
        elif action_type == "image_generation":
            payload = {
                "prompt": prompt,
                "parameters": {
                    "size": image_size,
                    "style": image_style.lower()
                }
            }
            
        else:  # acción personalizada
            payload = {
                "type": "custom",
                "input": prompt,
                "parameters": {
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            }
            if history:
                payload["context"] = format_history_for_digitalocean(history)
        
        # Enviar solicitud POST (las acciones de agentes generalmente usan POST)
        try:
            response = requests.post(endpoint_url, headers=headers, json=payload, timeout=60)
            
            # Verificar respuesta
            if response.status_code == 200 or response.status_code == 201:
                try:
                    response_data = response.json()
                    
                    # Procesar la respuesta según el tipo de acción
                    if action_type == "text_completion" or action_type == "question_answering":
                        # Buscar el contenido de la respuesta en diferentes posibles estructuras
                        if "action" in response_data and "result" in response_data["action"]:
                            return {"response": response_data["action"]["result"]}
                        elif "result" in response_data:
                            return {"response": response_data["result"]}
                        elif "output" in response_data:
                            return {"response": response_data["output"]}
                        else:
                            # Si no encontramos una estructura estándar, devolvemos todo
                            return {"response": str(response_data)}
                            
                    elif action_type == "image_generation":
                        # Para generación de imágenes, devolver URL o datos de la imagen
                        if "image_url" in response_data:
                            return {"response": f"![Imagen generada]({response_data['image_url']})", "image_url": response_data["image_url"]}
                        elif "data" in response_data and "url" in response_data["data"]:
                            return {"response": f"![Imagen generada]({response_data['data']['url']})", "image_url": response_data["data"]["url"]}
                        else:
                            return {"response": "Imagen generada correctamente, pero no se pudo obtener la URL."}
                    
                    else:  # Acción personalizada
                        # Buscar una respuesta en diferentes campos posibles
                        for field in ["result", "output", "response", "data", "content"]:
                            if field in response_data and isinstance(response_data[field], str):
                                return {"response": response_data[field]}
                        
                        # Si no encontramos un campo específico, devolvemos toda la respuesta
                        return {"response": str(response_data)}
                
                except ValueError:
                    # Si no es JSON, devolver el texto plano
                    return {"response": response.text}
            else:
                # Error en la respuesta
                error_message = f"Error en la solicitud. Código: {response.status_code}"
                try:
                    error_details = response.json()
                    return {"error": error_message, "details": str(error_details)}
                except:
                    return {"error": error_message, "details": response.text}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Error en la solicitud HTTP: {str(e)}"}
        
    except Exception as e:
        return {"error": f"Error al comunicarse con el agente: {str(e)}"}

# Función para formatear el historial para DigitalOcean
def format_history_for_digitalocean(history):
    formatted_history = []
    for msg in history:
        role = "assistant" if msg["role"] == "assistant" else "user"
        formatted_history.append({
            "role": role,
            "content": msg["content"]
        })
    return formatted_history

# Sección para probar conexión con el agente
with st.sidebar.expander("Probar conexión"):
    if st.button("Verificar conexión"):
        with st.spinner("Verificando conexión..."):
            try:
                agent_id = st.session_state.agent_id
                api_key = st.session_state.api_key
                
                if not agent_id or not api_key:
                    st.error("Falta configuración de ID del agente o API key")
                else:
                    # Construir URL para verificar el estado del agente
                    check_url = f"https://api.digitalocean.com/v2/agents/{agent_id}"
                    
                    # Preparar headers
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # Intentar obtener información del agente (GET)
                    try:
                        response = requests.get(check_url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            st.success(f"✅ Conexión exitosa con el agente")
                            with st.expander("Ver detalles del agente"):
                                try:
                                    agent_info = response.json()
                                    st.json(agent_info)
                                except:
                                    st.code(response.text)
                        else:
                            st.error(f"❌ Error al conectar con el agente. Código: {response.status_code}")
                            with st.expander("Ver detalles del error"):
                                st.code(response.text)
                    except Exception as e:
                        st.error(f"Error de conexión: {str(e)}")
            except Exception as e:
                st.error(f"Error al verificar conexión: {str(e)}")

# Mostrar historial de conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de entrada para el prompt
prompt = st.chat_input("Escribe tu mensaje aquí...")

# Procesar la entrada del usuario
if prompt:
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Preparar historial para la API
    api_history = st.session_state.messages[:-1]  # Excluir el mensaje actual
    
    # Mostrar indicador de carga mientras se procesa
    with st.chat_message("assistant"):
        with st.spinner("Procesando..."):
            # Enviar acción al agente
            response = send_agent_action(prompt, api_history)
            
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
                
                # Si es una imagen, mostrar la imagen
                if "image_url" in response:
                    st.image(response["image_url"], caption="Imagen generada")
                    # Ajustar el texto para guardar solo la URL en el historial
                    response_text = f"[Imagen generada]({response['image_url']})"
                
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

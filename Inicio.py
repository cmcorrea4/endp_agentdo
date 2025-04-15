import streamlit as st
import requests
import json
import time
import os

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

# Función para inicializar variables de sesión
def initialize_session_vars():
    if "is_configured" not in st.session_state:
        st.session_state.is_configured = False
    if "agent_endpoint" not in st.session_state:
        st.session_state.agent_endpoint = ""
    if "agent_access_key" not in st.session_state:
        st.session_state.agent_access_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "include_retrieval" not in st.session_state:
        st.session_state.include_retrieval = False

# Inicializar variables
initialize_session_vars()

# Título y descripción de la aplicación
st.markdown("<h1 class='main-header'>Agente de Inteligencia Artificial</h1>", unsafe_allow_html=True)

# Pantalla de configuración inicial si aún no se ha configurado
if not st.session_state.is_configured:
    st.markdown("<h2 class='subheader'>Configuración Inicial</h2>", unsafe_allow_html=True)
    
    st.info("Por favor, configura los parámetros de conexión para el agente de IA.")
    
    # Campos para la configuración
    agent_endpoint = st.text_input(
        "URL del Endpoint del Agente", 
        placeholder="https://tu-agente.dominio.com",
        help="URL base del endpoint de tu agente de IA (sin '/api/v1/')"
    )
    
    agent_access_key = st.text_input(
        "Clave de Acceso", 
        type="password",
        placeholder="Ingresa tu clave de acceso al agente",
        help="Tu clave de acceso para autenticar las solicitudes"
    )
    
    include_retrieval = st.checkbox(
        "Incluir información de recuperación",
        value=False,
        help="Activa esta opción para incluir información de recuperación (retrieval) en la respuesta"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Guardar configuración"):
            if not agent_endpoint or not agent_access_key:
                st.error("Por favor, ingresa tanto el endpoint como la clave de acceso")
            else:
                # Guardar configuración en session_state
                st.session_state.agent_endpoint = agent_endpoint
                st.session_state.agent_access_key = agent_access_key
                st.session_state.include_retrieval = include_retrieval
                st.session_state.is_configured = True
                st.success("¡Configuración guardada correctamente!")
                time.sleep(1)  # Breve pausa para mostrar el mensaje de éxito
                st.rerun()
    
    # Parar ejecución hasta que se configure
    st.stop()

# Una vez configurado, mostrar la interfaz normal
st.markdown("<p class='subheader'>Interactúa con el agente de IA para obtener respuestas inteligentes.</p>", unsafe_allow_html=True)

# Sidebar para configuración
st.sidebar.title("Configuración")

# Mostrar información de conexión actual
st.sidebar.success("✅ Configuración cargada")
with st.sidebar.expander("Ver configuración actual"):
    st.code(f"Endpoint: {st.session_state.agent_endpoint}\nClave de acceso: {'*'*10}")
    st.code(f"Incluir retrieval: {'Sí' if st.session_state.include_retrieval else 'No'}")
    if st.button("Editar configuración"):
        st.session_state.is_configured = False
        st.rerun()

# Ajustes avanzados
with st.sidebar.expander("Ajustes avanzados"):
    temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                           help="Valores más altos generan respuestas más creativas, valores más bajos generan respuestas más deterministas.")
    
    max_tokens = st.slider("Longitud máxima", min_value=100, max_value=2000, value=1000, step=100,
                          help="Número máximo de tokens en la respuesta.")
    
    include_retrieval = st.checkbox(
        "Incluir información de recuperación",
        value=st.session_state.include_retrieval,
        help="Activa esta opción para incluir información de recuperación (retrieval) en la respuesta"
    )
    # Actualizar la configuración de retrieval si cambia
    if include_retrieval != st.session_state.include_retrieval:
        st.session_state.include_retrieval = include_retrieval

# Función para enviar solicitud al agente de IA
def query_agent(prompt, history=None):
    try:
        # Obtener configuración del agente
        agent_endpoint = st.session_state.agent_endpoint
        agent_access_key = st.session_state.agent_access_key
        include_retrieval = st.session_state.include_retrieval
        
        if not agent_endpoint or not agent_access_key:
            return {"error": "Las credenciales de API no están configuradas correctamente."}
        
        # Asegurarse de que el endpoint termine con /api/v1/
        api_endpoint = agent_endpoint
        if not api_endpoint.endswith("/"):
            api_endpoint += "/"
        if not api_endpoint.endswith("api/v1/"):
            api_endpoint += "api/v1/"
        
        # Preparar URL completa para chat completions
        completions_url = f"{api_endpoint}chat/completions"
        
        # Preparar los headers
        headers = {
            "Authorization": f"Bearer {agent_access_key}",
            "Content-Type": "application/json"
        }
        
        # Preparar los mensajes en formato OpenAI
        messages = []
        if history:
            messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in history])
        messages.append({"role": "user", "content": prompt})
        
        # Preparar el payload
        payload = {
            "model": "n/a",  # El modelo no es relevante para el agente
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Añadir extra_body si se requiere información de recuperación
        if include_retrieval:
            payload["extra_body"] = {"include_retrieval_info": True}
        
        # Enviar solicitud POST
        try:
            response = requests.post(completions_url, headers=headers, json=payload, timeout=60)
            
            # Verificar respuesta
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    # Procesar la respuesta en formato OpenAI
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        choice = response_data["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            result = {
                                "response": choice["message"]["content"]
                            }
                            
                            # Añadir información de recuperación si está disponible
                            if include_retrieval and "retrieval" in response_data:
                                result["retrieval"] = response_data["retrieval"]
                            
                            return result
                    
                    # Si no se encuentra la estructura esperada
                    return {"error": "Formato de respuesta inesperado", "details": str(response_data)}
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

# Sección para probar conexión con el agente
with st.sidebar.expander("Probar conexión"):
    if st.button("Verificar endpoint"):
        with st.spinner("Verificando conexión..."):
            try:
                agent_endpoint = st.session_state.agent_endpoint
                agent_access_key = st.session_state.agent_access_key
                
                if not agent_endpoint or not agent_access_key:
                    st.error("Falta configuración del endpoint o clave de acceso")
                else:
                    # Asegurarse de que el endpoint termine con /api/v1/
                    api_endpoint = agent_endpoint
                    if not api_endpoint.endswith("/"):
                        api_endpoint += "/"
                    if not api_endpoint.endswith("api/v1/"):
                        api_endpoint += "api/v1/"
                    
                    # Preparar URL para modelos (endpoint común para verificar)
                    models_url = f"{api_endpoint}models"
                    
                    # Preparar headers
                    headers = {
                        "Authorization": f"Bearer {agent_access_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # Intentar hacer una solicitud simple para verificar conexión
                    try:
                        response = requests.get(models_url, headers=headers, timeout=10)
                        
                        if response.status_code < 400:
                            st.success(f"✅ Conexión exitosa con el agente")
                            try:
                                response_data = response.json()
                                if "data" in response_data:
                                    st.write("Modelos disponibles:")
                                    for model in response_data["data"]:
                                        st.write(f"- {model.get('id', 'Desconocido')}")
                                else:
                                    with st.expander("Ver detalles de la respuesta"):
                                        st.json(response_data)
                            except:
                                with st.expander("Ver detalles de la respuesta"):
                                    st.code(response.text)
                        else:
                            # Si el endpoint /models no funciona, intentar directamente con chat/completions
                            completions_url = f"{api_endpoint}chat/completions"
                            test_payload = {
                                "model": "n/a",
                                "messages": [{"role": "user", "content": "Hola"}],
                                "max_tokens": 5
                            }
                            
                            response = requests.post(completions_url, headers=headers, json=test_payload, timeout=10)
                            
                            if response.status_code < 400:
                                st.success(f"✅ Conexión exitosa con el agente (chat/completions)")
                                with st.expander("Ver detalles de la respuesta"):
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

# Campo de entrada para el mensaje
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
        with st.spinner("Pensando..."):
            # Llamar al agente
            response = query_agent(prompt, api_history)
            
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
                
                # Mostrar información de recuperación si está disponible
                if "retrieval" in response:
                    with st.expander("Información de recuperación (retrieval)"):
                        st.json(response["retrieval"])
                
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
st.markdown("<div class='footer'>Agente de IA © 2025</div>", unsafe_allow_html=True)

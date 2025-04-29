import streamlit as st
import requests
import json
import time
import base64
from gtts import gTTS
import io

# Configuración de la página
st.set_page_config(
    page_title="Agente DigitalOcean con Voz",
    page_icon="🎙️",
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
    .audio-controls {
        display: flex;
        align-items: center;
        margin-top: 10px;
    }
    .audio-button {
        background-color: #1E88E5;
        color: white;
        border: none;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        margin-right: 10px;
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
    if "include_functions" not in st.session_state:
        st.session_state.include_functions = False
    if "include_guardrails" not in st.session_state:
        st.session_state.include_guardrails = False
    if "enable_tts" not in st.session_state:
        st.session_state.enable_tts = True
    if "tts_language" not in st.session_state:
        st.session_state.tts_language = "es"
    if "tts_speed" not in st.session_state:
        st.session_state.tts_speed = False

# Inicializar variables
initialize_session_vars()

# Función para generar audio a partir de texto
def text_to_speech(text, lang='es', slow=False):
    try:
        # Crear objeto gTTS
        tts = gTTS(text=text, lang=lang, slow=slow)
        
        # Guardar audio en un buffer en memoria
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Convertir a base64 para reproducir en HTML
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()
        audio_html = f'''
        <div class="audio-controls">
            <audio autoplay="false" controls>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Tu navegador no soporta el elemento de audio.
            </audio>
        </div>
        '''
        return audio_html
    except Exception as e:
        return f"<div class='error'>Error al generar audio: {str(e)}</div>"

# Título y descripción de la aplicación
st.markdown("<h1 class='main-header'>Agente de DigitalOcean con Voz</h1>", unsafe_allow_html=True)

# Pantalla de configuración inicial si aún no se ha configurado
if not st.session_state.is_configured:
    st.markdown("<h2 class='subheader'>Configuración Inicial</h2>", unsafe_allow_html=True)
    
    st.info("Por favor, configura los parámetros para conectar con tu agente de DigitalOcean.")
    
    # Campos para la configuración
    agent_endpoint = st.text_input(
        "Endpoint del Agente", 
        placeholder="https://tu-agente-identifier.ondigitalocean.app",
        help="URL completa del endpoint del agente (sin '/api/v1/')"
    )
    
    agent_access_key = st.text_input(
        "Clave de Acceso", 
        type="password",
        placeholder="Ingresa tu clave de acceso al agente",
        help="Tu clave de acceso para autenticar las solicitudes"
    )
    
    # Opciones adicionales
    st.subheader("Opciones de Text-to-Speech")
    
    enable_tts = st.checkbox(
        "Habilitar Text-to-Speech",
        value=True,
        help="Convertir respuestas de texto a voz"
    )
    
    tts_language = st.selectbox(
        "Idioma para Text-to-Speech",
        options=["es", "en", "fr", "de", "it", "pt"],
        format_func=lambda x: {
            "es": "Español", 
            "en": "Inglés",
            "fr": "Francés",
            "de": "Alemán",
            "it": "Italiano",
            "pt": "Portugués"
        }[x],
        index=0,
        help="Selecciona el idioma para la síntesis de voz"
    )
    
    tts_speed = st.checkbox(
        "Habla lenta",
        value=False,
        help="Reducir la velocidad de la voz generada"
    )
    
    # Otras opciones del agente
    st.subheader("Opciones del Agente")
    
    include_retrieval = st.checkbox(
        "Incluir información de recuperación",
        value=False,
        help="Incluir información de recuperación en la respuesta"
    )
    
    include_functions = st.checkbox(
        "Incluir información de funciones",
        value=False,
        help="Incluir información de funciones en la respuesta"
    )
    
    include_guardrails = st.checkbox(
        "Incluir información de guardrails",
        value=False,
        help="Incluir información de guardrails en la respuesta"
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
                st.session_state.include_functions = include_functions
                st.session_state.include_guardrails = include_guardrails
                st.session_state.enable_tts = enable_tts
                st.session_state.tts_language = tts_language
                st.session_state.tts_speed = tts_speed
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
    st.code(f"Endpoint: {st.session_state.agent_endpoint}\nClave de acceso: {'*'*10}")
    st.write(f"Text-to-Speech: {'Habilitado' if st.session_state.enable_tts else 'Deshabilitado'}")
    st.write(f"Idioma TTS: {st.session_state.tts_language}")
    st.write(f"Include retrieval: {'Sí' if st.session_state.include_retrieval else 'No'}")
    st.write(f"Include functions: {'Sí' if st.session_state.include_functions else 'No'}")
    st.write(f"Include guardrails: {'Sí' if st.session_state.include_guardrails else 'No'}")
    if st.button("Editar configuración"):
        st.session_state.is_configured = False
        st.rerun()

# Ajustes avanzados
with st.sidebar.expander("Ajustes avanzados"):
    temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                          help="Valores más altos generan respuestas más creativas, valores más bajos generan respuestas más deterministas.")
    
    max_tokens = st.slider("Longitud máxima", min_value=100, max_value=2000, value=1000, step=100,
                          help="Número máximo de tokens en la respuesta.")
    
    # Opciones de Text-to-Speech
    st.subheader("Text-to-Speech")
    
    enable_tts = st.checkbox(
        "Habilitar Text-to-Speech",
        value=st.session_state.enable_tts,
        help="Convertir respuestas de texto a voz"
    )
    
    tts_language = st.selectbox(
        "Idioma para Text-to-Speech",
        options=["es", "en", "fr", "de", "it", "pt"],
        format_func=lambda x: {
            "es": "Español", 
            "en": "Inglés",
            "fr": "Francés",
            "de": "Alemán",
            "it": "Italiano",
            "pt": "Portugués"
        }[x],
        index=["es", "en", "fr", "de", "it", "pt"].index(st.session_state.tts_language),
        help="Selecciona el idioma para la síntesis de voz"
    )
    
    tts_speed = st.checkbox(
        "Habla lenta",
        value=st.session_state.tts_speed,
        help="Reducir la velocidad de la voz generada"
    )
    
    # Opciones para incluir información adicional
    st.subheader("Opciones del Agente")
    
    include_retrieval = st.checkbox(
        "Incluir información de recuperación",
        value=st.session_state.include_retrieval,
        help="Incluir información de recuperación en la respuesta"
    )
    include_functions = st.checkbox(
        "Incluir información de funciones",
        value=st.session_state.include_functions,
        help="Incluir información de funciones en la respuesta"
    )
    include_guardrails = st.checkbox(
        "Incluir información de guardrails",
        value=st.session_state.include_guardrails,
        help="Incluir información de guardrails en la respuesta"
    )
    
    # Actualizar la configuración si cambia
    if (enable_tts != st.session_state.enable_tts or
        tts_language != st.session_state.tts_language or
        tts_speed != st.session_state.tts_speed or
        include_retrieval != st.session_state.include_retrieval or
        include_functions != st.session_state.include_functions or
        include_guardrails != st.session_state.include_guardrails):
        st.session_state.enable_tts = enable_tts
        st.session_state.tts_language = tts_language
        st.session_state.tts_speed = tts_speed
        st.session_state.include_retrieval = include_retrieval
        st.session_state.include_functions = include_functions
        st.session_state.include_guardrails = include_guardrails

# Función para enviar consulta al agente
def query_agent(prompt, history=None):
    try:
        # Obtener configuración del agente
        agent_endpoint = st.session_state.agent_endpoint
        agent_access_key = st.session_state.agent_access_key
        include_retrieval = st.session_state.include_retrieval
        include_functions = st.session_state.include_functions
        include_guardrails = st.session_state.include_guardrails
        
        if not agent_endpoint or not agent_access_key:
            return {"error": "Las credenciales de API no están configuradas correctamente."}
        
        # Asegurarse de que el endpoint termine correctamente
        if not agent_endpoint.endswith("/"):
            agent_endpoint += "/"
        
        # Construir URL para chat completions
        completions_url = f"{agent_endpoint}api/v1/chat/completions"
        
        # Preparar headers con autenticación
        headers = {
            "Authorization": f"Bearer {agent_access_key}",
            "Content-Type": "application/json"
        }
        
        # Preparar los mensajes en formato OpenAI
        messages = []
        if history:
            messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in history])
        messages.append({"role": "user", "content": prompt})
        
        # Construir el payload
        payload = {
            "model": "n/a",  # El modelo no es relevante para el agente
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "include_retrieval_info": include_retrieval,
            "include_functions_info": include_functions,
            "include_guardrails_info": include_guardrails
        }
        
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
                            
                            # Añadir información adicional si está disponible
                            for info_type in ["retrieval", "functions", "guardrails"]:
                                if info_type in response_data:
                                    result[info_type] = response_data[info_type]
                            
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
                    # Asegurarse de que el endpoint termine correctamente
                    if not agent_endpoint.endswith("/"):
                        agent_endpoint += "/"
                    
                    # Verificar si la documentación está disponible (común en estos endpoints)
                    docs_url = f"{agent_endpoint}docs"
                    
                    # Preparar headers
                    headers = {
                        "Authorization": f"Bearer {agent_access_key}",
                        "Content-Type": "application/json"
                    }
                    
                    try:
                        # Primero intentar verificar si hay documentación disponible
                        response = requests.get(docs_url, timeout=10)
                        
                        if response.status_code < 400:
                            st.success(f"✅ Documentación del agente accesible en: {docs_url}")
                        
                        # Luego intentar hacer una solicitud simple para verificar la conexión
                        completions_url = f"{agent_endpoint}api/v1/chat/completions"
                        test_payload = {
                            "model": "n/a",
                            "messages": [{"role": "user", "content": "Hello"}],
                            "max_tokens": 5,
                            "stream": False
                        }
                        
                        response = requests.post(completions_url, headers=headers, json=test_payload, timeout=10)
                        
                        if response.status_code < 400:
                            st.success(f"✅ Conexión exitosa con el endpoint del agente")
                            with st.expander("Ver detalles de la respuesta"):
                                try:
                                    st.json(response.json())
                                except:
                                    st.code(response.text)
                            st.info("🔍 La API está configurada correctamente y responde a las solicitudes.")
                        else:
                            st.error(f"❌ Error al conectar con el agente. Código: {response.status_code}")
                            with st.expander("Ver detalles del error"):
                                st.code(response.text)
                    except Exception as e:
                        st.error(f"Error de conexión: {str(e)}")
            except Exception as e:
                st.error(f"Error al verificar endpoint: {str(e)}")

# Mostrar historial de conversación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Si es un mensaje del asistente y tiene audio asociado, mostrarlo
        if message["role"] == "assistant" and "audio_html" in message:
            st.markdown(message["audio_html"], unsafe_allow_html=True)

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
            # Enviar consulta al agente
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
                
                # Generar audio si está habilitado
                audio_html = None
                if st.session_state.enable_tts:
                    with st.spinner("Generando audio..."):
                        audio_html = text_to_speech(
                            response_text, 
                            lang=st.session_state.tts_language, 
                            slow=st.session_state.tts_speed
                        )
                        st.markdown(audio_html, unsafe_allow_html=True)
                
                # Mostrar información adicional si está disponible
                for info_type, display_name in [
                    ("retrieval", "Información de recuperación"),
                    ("functions", "Información de funciones"),
                    ("guardrails", "Información de guardrails")
                ]:
                    if info_type in response:
                        with st.expander(f"{display_name}"):
                            st.json(response[info_type])
                
                # Añadir respuesta al historial con el audio
                message_data = {"role": "assistant", "content": response_text}
                if audio_html:
                    message_data["audio_html"] = audio_html
                st.session_state.messages.append(message_data)

# Sección de opciones adicionales
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.experimental_rerun()

with col2:
    if st.button("💾 Guardar conversación"):
        # Crear una versión del historial sin HTML para guardar
        save_messages = []
        for msg in st.session_state.messages:
            save_msg = {"role": msg["role"], "content": msg["content"]}
            save_messages.append(save_msg)
            
        # Convertir historial a formato JSON
        conversation_data = json.dumps(save_messages, indent=2)
        
        # Crear archivo para descargar
        st.download_button(
            label="Descargar JSON",
            data=conversation_data,
            file_name="conversacion.json",
            mime="application/json",
        )

with col3:
    if st.button("🔄 Cambiar TTS " + ("✅" if st.session_state.enable_tts else "❌")):
        st.session_state.enable_tts = not st.session_state.enable_tts
        st.success(f"Text-to-Speech {'habilitado' if st.session_state.enable_tts else 'deshabilitado'}")
        time.sleep(0.5)
        st.experimental_rerun()

# Pie de página
st.markdown("<div class='footer'>Agente de DigitalOcean con Text-to-Speech © 2025</div>", unsafe_allow_html=True)

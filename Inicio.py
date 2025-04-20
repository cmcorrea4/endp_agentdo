import streamlit as st
import requests
import json
import time
import io
import base64
import os
from gtts import gTTS
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
import tempfile

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
        margin-bottom: 0.5rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #424242;
        margin-bottom: 0.5rem;
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
    .stAudio {
        margin-top: 10px;
    }
    .stAudio > audio {
        width: 100%; 
    }
    /* Ocultar la barra de título del sidebar */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    /* Mejorar el espacio para el chat */
    .stChatMessageContent {
        padding: 0.5rem;
    }
    .stChatMessage {
        margin-bottom: 0.5rem;
    }
    /* Dar más espacio a la conversación */
    section.main > div {
        padding-bottom: 5rem;
    }
    /* Eliminar espacios extra */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
    }
    .main .block-container {
        padding: 1rem 1rem 3rem 1rem !important;
        max-width: 100% !important;
    }
    /* Ajustar contenedor principal */
    .css-1d391kg, .css-1knacbx {
        padding-top: 0 !important;
    }
    /* Espacio para los mensajes */
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    div.element-container {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
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
    if "audio_responses" not in st.session_state:
        st.session_state.audio_responses = {}
    if "tts_enabled" not in st.session_state:
        st.session_state.tts_enabled = False
    if "connection_result" not in st.session_state:
        st.session_state.connection_result = None
    if "pending_message" not in st.session_state:
        st.session_state.pending_message = None

# Inicializar variables
initialize_session_vars()

# Función para actualizar configuración
def update_config():
    st.session_state.is_configured = True

# Función para editar configuración
def edit_config():
    st.session_state.is_configured = False

# Función para limpiar conversación
def clear_conversation():
    st.session_state.messages = []
    st.session_state.audio_responses = {}

# Función para cambiar estado TTS
def toggle_tts():
    st.session_state.tts_enabled = not st.session_state.tts_enabled

# Función para crear PDF de la conversación
def create_pdf(messages):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    user_style = ParagraphStyle(
        'UserStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.blue,
        leftIndent=0,
        spaceAfter=5
    )
    
    assistant_style = ParagraphStyle(
        'AssistantStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.darkgreen,
        leftIndent=10,
        spaceAfter=15
    )
    
    # Crear contenido del PDF
    content = []
    
    # Título
    content.append(Paragraph("Conversación con Agente de DigitalOcean", title_style))
    content.append(Spacer(1, 12))
    
    # Fecha y hora
    from datetime import datetime
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    content.append(Paragraph(f"Generado el: {now}", styles['Normal']))
    content.append(Spacer(1, 12))
    
    # Añadir cada mensaje
    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            prefix = "👤 Usuario: "
            style = user_style
        else:
            prefix = "🤖 Asistente: "
            style = assistant_style
        
        content.append(Paragraph(f"{prefix}{msg['content']}", style))
        
        # Separador entre conversaciones completas (pregunta-respuesta)
        if i % 2 == 1:
            content.append(Spacer(1, 10))
    
    # Construir el PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

# Función para crear audio de texto
def text_to_speech(text):
    try:
        # Limitar la longitud del texto (gTTS tiene límites)
        if len(text) > 5000:
            text = text[:5000] + "... [Texto truncado debido a limitaciones]"
            
        # Crear objeto de texto a voz en español
        tts = gTTS(text=text, lang='es', slow=False)
        
        # Usar un archivo temporal en lugar de BytesIO para asegurar compatibilidad
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            temp_audio_file = tmp_file.name
            
        # Guardar en el archivo temporal
        tts.save(temp_audio_file)
        
        # Leer el archivo como binario
        with open(temp_audio_file, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Eliminar archivo temporal
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        
        return audio_bytes
    except Exception as e:
        st.error(f"Error al generar audio: {str(e)}")
        return None

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

# Función para verificar la conexión con el agente
def check_endpoint():
    try:
        agent_endpoint = st.session_state.agent_endpoint
        agent_access_key = st.session_state.agent_access_key
        
        if not agent_endpoint or not agent_access_key:
            return [{"status": "error", "message": "Falta configuración del endpoint o clave de acceso"}]
        
        # Asegurarse de que el endpoint termine correctamente
        if not agent_endpoint.endswith("/"):
            agent_endpoint += "/"
        
        # Verificar si la documentación está disponible
        docs_url = f"{agent_endpoint}docs"
        
        # Preparar headers
        headers = {
            "Authorization": f"Bearer {agent_access_key}",
            "Content-Type": "application/json"
        }
        
        results = []
        
        # Intentar verificar si hay documentación disponible
        try:
            response = requests.get(docs_url, timeout=10)
            
            if response.status_code < 400:
                results.append({"status": "success", "message": f"✅ Documentación del agente accesible en: {docs_url}"})
            
            # Intentar hacer una solicitud simple para verificar la conexión
            completions_url = f"{agent_endpoint}api/v1/chat/completions"
            test_payload = {
                "model": "n/a",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5,
                "stream": False
            }
            
            response = requests.post(completions_url, headers=headers, json=test_payload, timeout=10)
            
            if response.status_code < 400:
                results.append({"status": "success", "message": "✅ Conexión exitosa con el endpoint del agente"})
                
                # Obtener detalles de la respuesta para mostrar
                try:
                    resp_json = response.json()
                    results.append({"status": "info", "message": "🔍 La API está configurada correctamente y responde a las solicitudes.", "details": resp_json})
                except:
                    results.append({"status": "info", "message": "🔍 La API está configurada correctamente y responde a las solicitudes.", "details": response.text})
            else:
                results.append({"status": "error", "message": f"❌ Error al conectar con el agente. Código: {response.status_code}", "details": response.text})
                
        except Exception as e:
            results.append({"status": "error", "message": f"Error de conexión: {str(e)}"})
    
        return results
        
    except Exception as e:
        return [{"status": "error", "message": f"Error al verificar endpoint: {str(e)}"}]

# Título y descripción de la aplicación
st.markdown("<h1 class='main-header'>Agente de DigitalOcean</h1>", unsafe_allow_html=True)

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
    
    # Opción para habilitar text-to-speech
    tts_enabled = st.checkbox(
        "Habilitar Text-to-Speech",
        value=False,
        help="Convertir respuestas del asistente a voz"
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
                st.session_state.tts_enabled = tts_enabled
                update_config()
                st.success("¡Configuración guardada correctamente!")
                st.rerun()
    
    # Parar ejecución hasta que se configure
    st.stop()

# Una vez configurado, mostrar la interfaz normal
st.markdown("<p class='subheader'>Interactúa con tu agente de DigitalOcean</p>", unsafe_allow_html=True)

# Sidebar para configuración
st.sidebar.title("Configuración")

# Mostrar información de conexión actual
st.sidebar.success("✅ Configuración cargada")
with st.sidebar.expander("Ver configuración actual"):
    st.code(f"Endpoint: {st.session_state.agent_endpoint}\nClave de acceso: {'*'*10}")
    st.write(f"Include retrieval: {'Sí' if st.session_state.include_retrieval else 'No'}")
    st.write(f"Include functions: {'Sí' if st.session_state.include_functions else 'No'}")
    st.write(f"Include guardrails: {'Sí' if st.session_state.include_guardrails else 'No'}")
    st.write(f"Text-to-Speech: {'Habilitado' if st.session_state.tts_enabled else 'Deshabilitado'}")
    if st.button("Editar configuración"):
        edit_config()
        st.rerun()

# Ajustes avanzados
with st.sidebar.expander("Ajustes avanzados"):
    temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.2, step=0.1,
                          help="Valores más altos generan respuestas más creativas, valores más bajos generan respuestas más deterministas.")
    
    max_tokens = st.slider("Longitud máxima", min_value=100, max_value=2000, value=1000, step=100,
                          help="Número máximo de tokens en la respuesta.")
    
    # Opciones para incluir información adicional
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
    
    # Opción para habilitar/deshabilitar TTS
    tts_enabled = st.checkbox(
        "Habilitar Text-to-Speech",
        value=st.session_state.tts_enabled,
        help="Convertir respuestas del asistente a voz"
    )
    
    # Actualizar la configuración si cambia
    if (include_retrieval != st.session_state.include_retrieval or
        include_functions != st.session_state.include_functions or
        include_guardrails != st.session_state.include_guardrails or
        tts_enabled != st.session_state.tts_enabled):
        st.session_state.include_retrieval = include_retrieval
        st.session_state.include_functions = include_functions
        st.session_state.include_guardrails = include_guardrails
        st.session_state.tts_enabled = tts_enabled

# Sección para probar conexión con el agente
with st.sidebar.expander("Probar conexión"):
    if st.button("Verificar endpoint"):
        with st.spinner("Verificando conexión..."):
            # Ejecutar verificación y guardar resultado
            st.session_state.connection_result = check_endpoint()
            st.rerun()
    
    # Mostrar resultados si existen
    if st.session_state.connection_result:
        for result in st.session_state.connection_result:
            if result["status"] == "success":
                st.success(result["message"])
            elif result["status"] == "error":
                st.error(result["message"])
            elif result["status"] == "info":
                st.info(result["message"])
                
                # Mostrar detalles si existen (fuera del expander)
                if "details" in result:
                    st.subheader("Detalles de la respuesta")
                    try:
                        if isinstance(result["details"], dict) or isinstance(result["details"], list):
                            st.json(result["details"])
                        else:
                            st.code(result["details"])
                    except:
                        st.code(str(result["details"]))

# MOVER TODAS LAS OPCIONES AL SIDEBAR
st.sidebar.divider()
st.sidebar.subheader("Opciones de conversación")

# Sección de opciones adicionales en la barra lateral
button_col1, button_col2 = st.sidebar.columns(2)

with button_col1:
    if st.button("🗑️ Limpiar conversación"):
        clear_conversation()
        st.rerun()

with button_col2:
    # Opción para cambiar el estado de TTS
    tts_status = "Habilitado" if st.session_state.tts_enabled else "Deshabilitado"
    if st.button(f"🔊 TTS: {tts_status}"):
        toggle_tts()
        st.rerun()

# Opciones de exportación
save_col1, save_col2 = st.sidebar.columns(2)

with save_col1:
    if len(st.session_state.messages) > 0:
        # Generar PDF
        pdf_buffer = create_pdf(st.session_state.messages)
        
        # Botón para descargar el PDF
        st.download_button(
            label="📄 Guardar como PDF",
            data=pdf_buffer,
            file_name="conversacion.pdf",
            mime="application/pdf",
        )
    else:
        st.button("📄 Guardar como PDF", disabled=True)

with save_col2:
    if len(st.session_state.messages) > 0:
        # Convertir historial a formato JSON
        conversation_data = json.dumps(st.session_state.messages, indent=2)
        
        # Crear archivo para descargar
        st.download_button(
            label="💾 Guardar como JSON",
            data=conversation_data,
            file_name="conversacion.json",
            mime="application/json",
        )
    else:
        st.button("💾 Guardar como JSON", disabled=True)

# Mostrar historial de conversación - ELIMINADO EL ESPACIO EXTRA
# Contenedor para la conversación con altura ajustada
chat_container = st.container()

with chat_container:
    # Mostrar mensajes existentes
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostrar audio para respuestas del asistente si TTS está habilitado
            if message["role"] == "assistant" and st.session_state.tts_enabled:
                # Verificar si ya tenemos el audio para este mensaje
                message_id = f"msg_{i}"
                if message_id not in st.session_state.audio_responses:
                    # Generar audio para este mensaje
                    audio_data = text_to_speech(message["content"])
                    if audio_data:
                        st.session_state.audio_responses[message_id] = audio_data
                
                # Mostrar reproductor de audio si tenemos datos
                if message_id in st.session_state.audio_responses:
                    # Usar el método de Streamlit para mostrar audio con autoplay=False
                    st.audio(st.session_state.audio_responses[message_id], format="audio/mp3")

# Campo de entrada de chat - COLOCADO DIRECTAMENTE DEBAJO DE LOS MENSAJES
prompt = st.chat_input("Escribe tu mensaje aquí...")
if prompt:
    st.session_state.pending_message = prompt
    st.rerun()

# Procesar la entrada del usuario si hay un mensaje pendiente
if st.session_state.pending_message:
    prompt = st.session_state.pending_message
    st.session_state.pending_message = None  # Limpiar para evitar múltiples procesamientos
    
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Preparar historial para la API
    api_history = st.session_state.messages[:-1]  # Excluir el mensaje actual
    
    # Mostrar indicador de carga mientras se procesa
    with st.spinner("El asistente está procesando tu mensaje..."):
        # Enviar consulta al agente
        response = query_agent(prompt, api_history)
        
        if "error" in response:
            error_msg = f"Lo siento, ocurrió un error al procesar tu solicitud: {response['error']}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            # Obtener respuesta del asistente
            response_text = response.get("response", "No se recibió respuesta del agente.")
            
            # Generar audio si TTS está habilitado
            audio_data = None
            if st.session_state.tts_enabled:
                with st.spinner("Generando audio..."):
                    audio_data = text_to_speech(response_text)
                
            # Añadir respuesta al historial
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Almacenar audio si se generó
            if audio_data:
                message_id = f"msg_{len(st.session_state.messages) - 1}"
                st.session_state.audio_responses[message_id] = audio_data
    
    # Actualizar la interfaz para mostrar los nuevos mensajes
    st.rerun()

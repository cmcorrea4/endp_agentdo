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
    .audio-btn {
        margin-top: 5px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        cursor: pointer;
    }
    .audio-btn:hover {
        background-color: #45a049;
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

# Inicializar variables
initialize_session_vars()

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
def text_to_speech(text, lang='es'):
    try:
        # Limitar la longitud del texto (gTTS tiene límites)
        if len(text) > 5000:
            text = text[:5000] + "... [Texto truncado debido a limitaciones]"
            
        # Crear objeto de texto a voz
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Guardar a un buffer en memoria
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Convertir a base64 para incrustar en HTML
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()
        
        return audio_base64
    except Exception as e:
        st.error(f"Error al generar audio: {str(e)}")
        return None

# Función para mostrar el audio player
def display_audio_player(audio_base64):
    audio_html = f"""
        <audio controls autoplay="false">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Tu navegador no soporta el elemento de audio.
        </audio>
    """
    return st.markdown(audio_html, unsafe_allow_html=True)

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
    st.write(f"Include retrieval: {'Sí' if st.session_state.include_retrieval else 'No'}")
    st.write(f"Include functions: {'Sí' if st.session_state.include_functions else 'No'}")
    st.write(f"Include guardrails: {'Sí' if st.session_state.include_guardrails else 'No'}")
    st.write(f"Text-to-Speech: {'Habilitado' if st.session_state.tts_enabled else 'Deshabilitado'}")
    if st.button("Editar configuración"):
        st.session_state.is_configured = False
        st.rerun()

# Ajustes avanzados
with st.sidebar.expander("Ajustes avanzados"):
    temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
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
    
    # Selección de idioma para TTS
    tts_language = st.selectbox(
        "Idioma para Text-to-Speech",
        options=["es", "en", "fr", "de", "it", "pt"],
        index=0,
        format_func=lambda x: {
            "es": "Español", 
            "en": "Inglés", 
            "fr": "Francés", 
            "de": "Alemán",
            "it": "Italiano",
            "pt": "Portugués"
        }.get(x, x),
        help="Selecciona el idioma para la síntesis de voz"
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
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Mostrar botón de audio para respuestas del asistente si TTS está habilitado
        if message["role"] == "assistant" and st.session_state.tts_enabled:
            # Verificar si ya tenemos el audio para este mensaje
            message_id = f"msg_{i}"
            if message_id not in st.session_state.audio_responses:
                # Generar audio para este mensaje
                audio_data = text_to_speech(message["content"], tts_language)
                if audio_data:
                    st.session_state.audio_responses[message_id] = audio_data
            
            # Mostrar reproductor de audio si tenemos datos
            if message_id in st.session_state.audio_responses:
                display_audio_player(st.session_state.audio_responses[message_id])

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
                
                # Generar y mostrar audio si TTS está habilitado
                if st.session_state.tts_enabled:
                    audio_data = text_to_speech(response_text, tts_language)
                    if audio_data:
                        display_audio_player(audio_data)
                        # Guardar para la historia
                        message_id = f"msg_{len(st.session_state.messages)}"
                        st.session_state.audio_responses[message_id] = audio_data
                
                # Mostrar información adicional si está disponible
                for info_type, display_name in [
                    ("retrieval", "Información de recuperación"),
                    ("functions", "Información de funciones"),
                    ("guardrails", "Información de guardrails")
                ]:
                    if info_type in response:
                        with st.expander(f"{display_name}"):
                            st.json(response[info_type])
                
                # Añadir respuesta al historial
                st.session_state.messages.append({"role": "assistant", "content": response_text})

# Sección de opciones adicionales
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.session_state.audio_responses = {}
        st.experimental_rerun()

with col2:
    if st.button("📄 Guardar como PDF"):
        if len(st.session_state.messages) > 0:
            # Generar PDF
            pdf_buffer = create_pdf(st.session_state.messages)
            
            # Botón para descargar el PDF
            st.download_button(
                label="Descargar PDF",
                data=pdf_buffer,
                file_name="conversacion.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("No hay mensajes para guardar.")

with col3:
    if st.button("💾 Guardar como JSON"):
        if len(st.session_state.messages) > 0:
            # Convertir historial a formato JSON
            conversation_data = json.dumps(st.session_state.messages, indent=2)
            
            # Crear archivo para descargar
            st.download_button(
                label="Descargar JSON",
                data=conversation_data,
                file_name="conversacion.json",
                mime="application/json",
            )
        else:
            st.warning("No hay mensajes para guardar.")

# Configuración de TTS en la parte inferior
st.divider()
tts_col1, tts_col2 = st.columns(2)

with tts_col1:
    # Mostrar estado actual de TTS
    tts_status = "Habilitado" if st.session_state.tts_enabled else "Deshabilitado"
    st.write(f"🔊 Text-to-Speech: {tts_status}")

with tts_col2:
    # Botón para cambiar el estado de TTS
    if st.button("Cambiar estado de TTS"):
        st.session_state.tts_enabled = not st.session_state.tts_enabled
        st.experimental_rerun()

# Pie de página
st.markdown("<div class='footer'>Agente de DigitalOcean © 2025</div>", unsafe_allow_html=True)

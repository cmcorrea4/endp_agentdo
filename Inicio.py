import streamlit as st
import requests
import json
import time

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
    if "api_url" not in st.session_state:
        st.session_state.api_url = ""
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_type" not in st.session_state:
        st.session_state.api_type = "standard"

# Inicializar variables
initialize_session_vars()

# Título y descripción de la aplicación
st.markdown("<h1 class='main-header'>Agente de Inteligencia Artificial</h1>", unsafe_allow_html=True)

# Pantalla de configuración inicial si aún no se ha configurado
if not st.session_state.is_configured:
    st.markdown("<h2 class='subheader'>Configuración Inicial</h2>", unsafe_allow_html=True)
    
    st.info("Por favor, configura los parámetros de conexión para el agente de IA.")
    
    # Campos para la configuración
    api_url = st.text_input(
        "URL del Endpoint de IA", 
        placeholder="https://api.ejemplo.com/v1/completions",
        help="URL completa del endpoint de la API de IA"
    )
    
    api_key = st.text_input(
        "API Key", 
        type="password",
        placeholder="Ingresa tu API key",
        help="Tu clave de API para autenticar las solicitudes"
    )
    
    # Tipo de API
    api_type = st.selectbox(
        "Tipo de API",
        options=["Standard (OpenAI-like)", "Digital Ocean", "Personalizada"],
        index=0,
        help="Selecciona el tipo de API con la que te conectarás"
    )
    
    # Mapear selección a valor interno
    api_type_value = "standard" if api_type == "Standard (OpenAI-like)" else "digitalocean" if api_type == "Digital Ocean" else "custom"
    
    # Mostrar mensaje de ayuda según el tipo seleccionado
    if api_type_value == "standard":
        st.info("Formato compatible con OpenAI, Azure OpenAI, o servicios similares.")
    elif api_type_value == "digitalocean":
        st.info("Formato específico para Digital Ocean AI API.")
    else:
        st.info("Formato personalizado. Puedes necesitar ajustar el código para adaptarlo.")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Guardar configuración"):
            if not api_url or not api_key:
                st.error("Por favor, ingresa tanto la URL como la API Key")
            else:
                # Guardar configuración en session_state
                st.session_state.api_url = api_url
                st.session_state.api_key = api_key
                st.session_state.api_type = api_type_value
                st.session_state.is_configured = True
                st.success("¡Configuración guardada correctamente!")
                time.sleep(1)  # Breve pausa para mostrar el mensaje de éxito
                st.rerun()
    
    # Parar ejecución hasta que se configure
    st.stop()

# Una vez configurado, mostrar la interfaz normal
st.markdown("<p class='subheader'>Interactúa con nuestro agente de IA para obtener respuestas inteligentes.</p>", unsafe_allow_html=True)

# Sidebar para configuración
st.sidebar.title("Configuración")

# Mostrar información de conexión actual
st.sidebar.success("✅ Configuración cargada")
with st.sidebar.expander("Ver configuración actual"):
    st.code(f"URL: {st.session_state.api_url}\nAPI Key: {'*'*10}\nTipo: {st.session_state.api_type}")
    if st.button("Editar configuración"):
        st.session_state.is_configured = False
        st.rerun()

# Opciones de modelo (si hay varios disponibles)
model_option = st.sidebar.selectbox(
    "Seleccione el modelo",
    ["GPT-4o Mini", "GPT-3.5", "GPT-4", "Claude", "Personalizado"],
    index=0  # Establecer GPT-4o Mini como selección predeterminada
)

# Ajustes avanzados
with st.sidebar.expander("Ajustes avanzados"):
    temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                          help="Valores más altos generan respuestas más creativas, valores más bajos generan respuestas más deterministas.")
    max_length = st.slider("Longitud máxima", min_value=100, max_value=2000, value=1000, step=100,
                          help="Número máximo de tokens en la respuesta.")

# Función para enviar solicitud al endpoint de IA
def query_ai_endpoint(prompt, history=None):
    try:
        # Obtener URL y token de API desde session_state
        api_url = st.session_state.api_url
        api_key = st.session_state.api_key
        api_type = st.session_state.api_type
        
        if not api_url or not api_key:
            return {"error": "Las credenciales de API no están configuradas correctamente."}
        
        # Preparar la solicitud
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Construir el payload basado en el tipo de API y el modelo seleccionado
        if api_type == "standard":  # Compatible con OpenAI
            payload = {
                "model": "gpt-4o-mini",  # Usar GPT-4o Mini por defecto
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_length
            }
            
            # Añadir historial si está disponible
            if history:
                messages = []
                for msg in history:
                    role = "assistant" if msg["role"] == "assistant" else "user"
                    messages.append({"role": role, "content": msg["content"]})
                # Añadir el mensaje actual al final
                messages.append({"role": "user", "content": prompt})
                payload["messages"] = messages
                
        elif api_type == "digitalocean":  # Digital Ocean
            payload = {
                "prompt": prompt,
                "max_tokens": max_length,
                "temperature": temperature
            }
            
            # Añadir historial si está disponible
            if history:
                payload["history"] = history
                
        else:  # API personalizada
            # Formato genérico que podría necesitar ser ajustado
            payload = {
                "prompt": prompt,
                "model": "gpt-4o-mini",  # Usar GPT-4o Mini por defecto
                "max_tokens": max_length,
                "temperature": temperature
            }
            
            # Añadir historial en formato genérico
            if history:
                payload["history"] = history
        
        # Enviar solicitud al endpoint usando POST (más común para APIs de IA)
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            # Verificar respuesta
            if response.status_code == 200:
                response_data = response.json()
                
                # Procesar la respuesta según el tipo de API
                if api_type == "standard":  # OpenAI-like
                    # Estructura estándar de OpenAI: { choices: [{ message: { content: "..." } }] }
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        response_text = response_data["choices"][0].get("message", {}).get("content", "")
                        return {"response": response_text}
                    else:
                        return {"error": "Formato de respuesta inesperado", "details": str(response_data)}
                else:
                    # Para otros tipos de API, intentamos extraer "response" o "text" o retornamos todo
                    if "response" in response_data:
                        return response_data
                    elif "text" in response_data:
                        return {"response": response_data["text"]}
                    else:
                        # Intentar buscar algún campo con texto en la respuesta
                        for key in response_data:
                            if isinstance(response_data[key], str) and len(response_data[key]) > 20:
                                return {"response": response_data[key]}
                        # Si no encontramos nada útil, devolvemos la respuesta completa
                        return {"response": str(response_data)}
            
            elif response.status_code == 405:  # Method Not Allowed
                # Intentar con método GET como fallback (menos común)
                try:
                    if api_type == "standard":
                        # Generalmente las APIs tipo OpenAI no soportan GET para completions
                        return {"error": "El endpoint no acepta solicitudes POST", "details": response.text}
                    else:
                        # Convertir payload a query params para GET
                        params = {}
                        for key, value in payload.items():
                            if not isinstance(value, (dict, list)):
                                params[key] = value
                        # Si hay listas o diccionarios, esto no funcionará bien, pero lo intentamos
                        response = requests.get(api_url, headers=headers, params=params, timeout=30)
                        if response.status_code == 200:
                            return {"response": response.json()}
                except Exception as e:
                    pass  # Si falla el GET, regresamos el error original
            
            # Si llegamos aquí, hubo un error
            return {
                "error": f"Error en la solicitud. Código: {response.status_code}",
                "details": response.text
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Error en la solicitud HTTP: {str(e)}"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}
    
    except Exception as e:
        return {"error": f"Error al comunicarse con el endpoint de IA: {str(e)}"}

# Sección para probar conexión con el endpoint
with st.sidebar.expander("Probar conexión"):
    if st.button("Verificar endpoint"):
        with st.spinner("Verificando conexión..."):
            try:
                api_url = st.session_state.api_url
                api_key = st.session_state.api_key
                api_type = st.session_state.api_type
                
                if not api_url or not api_key:
                    st.error("Falta configuración de URL o API key")
                else:
                    # Preparar headers
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    # Mensaje de prueba mínimo
                    test_prompt = "Hola"
                    
                    # Preparar payload según el tipo de API
                    if api_type == "standard":  # OpenAI-like
                        payload = {
                            "model": "gpt-4o-mini",
                            "messages": [{"role": "user", "content": test_prompt}],
                            "temperature": 0.1,
                            "max_tokens": 5
                        }
                    else:  # Digital Ocean u otro
                        payload = {
                            "prompt": test_prompt,
                            "max_tokens": 5,
                            "temperature": 0.1
                        }
                    
                    # Variable para controlar si ya se encontró una conexión exitosa
                    conexion_exitosa = False
                    
                    # Intentar conexión POST
                    if not conexion_exitosa:
                        try:
                            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
                            if response.status_code < 400:
                                st.success(f"✅ Conexión exitosa (POST)")
                                with st.expander("Ver detalles de la respuesta"):
                                    st.code(response.text)
                                conexion_exitosa = True
                        except Exception as e:
                            st.warning(f"No se pudo conectar usando POST: {str(e)}")
                    
                    # Si POST falló, intentar con GET
                    if not conexion_exitosa:
                        try:
                            # Simplificar para GET
                            params = {"prompt": test_prompt}
                            response = requests.get(api_url, headers=headers, params=params, timeout=10)
                            if response.status_code < 400:
                                st.success(f"✅ Conexión exitosa (GET)")
                                with st.expander("Ver detalles de la respuesta"):
                                    st.code(response.text)
                                conexion_exitosa = True
                        except Exception as e:
                            st.warning(f"No se pudo conectar usando GET: {str(e)}")
                    
                    # Si nada funcionó
                    if not conexion_exitosa:
                        st.error("❌ No se pudo establecer conexión con el endpoint.")
                        st.info("Sugerencias: Verifica la URL, la API key, y asegúrate de que el endpoint esté activo.")
                    
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
    
    # Preparar historial para la API
    api_history = st.session_state.messages[:-1]  # Excluir el mensaje actual
    
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
                
                # Añadir mensaje de error al historial
                error_msg = f"Lo siento, ocurrió un error al procesar tu solicitud: {response['error']}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
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
st.markdown("<div class='footer'>Agente de IA con GPT-4o Mini © 2025</div>", unsafe_allow_html=True)

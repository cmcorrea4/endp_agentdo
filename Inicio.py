import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import base64

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Asistentes Digitales SUME",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Aplicar CSS personalizado para mejorar la apariencia
    st.markdown("""
    <style>
    /* Colores corporativos */
    :root {
        --primary: #EB6600;
        --secondary: #031B4E;
        --background: #ffffff;
        --text: #333333;
    }
    
    /* Reducción de espacios innecesarios */
    .stApp {
        background-color: var(--background);
        padding: 0;
        margin: 0;
    }
    
    /* Eliminar espacios entre elementos */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        max-width: 95%;
    }
    
    .st-emotion-cache-16txtl3 {
        padding: 0.5rem 0.5rem 0.5rem;
    }
    
    /* Reducir espacio vertical entre componentes */
    .element-container, [data-testid="stVerticalBlock"] {
        gap: 0px !important;
        margin-bottom: 5px !important;
    }
    
    h1, h2, h3 {
        color: var(--secondary);
        font-family: 'Segoe UI', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    /* Tarjetas para cada asistente */
    .assistant-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
        border-left: 5px solid var(--primary);
    }
    
    /* Iconos grandes */
    .icon-large {
        font-size: 2rem;
        color: var(--primary);
        margin-right: 10px;
    }
    
    /* Separador con gradiente */
    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #EB6600, #031B4E);
        margin: 10px 0;
        border-radius: 3px;
    }
    
    /* Ajustar altura del chatbot */
    .chatbot-container {
        height: 500px;
        margin-top: 0;
        padding: 0;
    }
    
    /* Ocultar el encabezado "streamlit" por defecto */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Ajuste para el logo y título */
    .header-container {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    
    .header-title {
        color: #031B4E;
        margin-left: 15px;
        font-size: 1.8rem;
    }
    
    /* Ajustes para el menú */
    .stHorizontalBlock {
        gap: 0 !important;
    }
    
    /* Eliminar margen superior del primer elemento */
    .main > .block-container > div:first-child {
        margin-top: 0 !important;
    }
    
    /* Corregir el espacio entre tarjetas y elementos */
    p {
        margin-bottom: 0.5rem;
    }
    
    ul {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header con logo y título
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("logo_sume2.png", width=100)
    with col2:
        st.markdown("<h1 class='header-title'>Asistentes Digitales SUME</h1>", unsafe_allow_html=True)
    
    # Navegación con iconos
    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Asistente de Voz", "Asistente de Energía", "Asistente Textil", "Acerca de"],
        icons=["house", "mic", "lightning-charge", "layers", "info-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#EB6600", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee", "padding": "10px"},
            "nav-link-selected": {"background-color": "#EB6600", "color": "white"},
        }
    )
    
    # Página de inicio
    if selected == "Inicio":
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            <div class="assistant-card">
                <h2>Bienvenido a los Asistentes Digitales SUME</h2>
                <p>Nuestros asistentes digitales están diseñados para facilitar su interacción con los servicios de SUME Energy. 
                Elija el tipo de asistente que necesita utilizando la barra de navegación superior.</p>
                
            </div>
            """, unsafe_allow_html=True)
            
            # Usar componentes nativos de Streamlit para el divisor y la lista
            st.markdown('<hr style="height: 3px; background: linear-gradient(90deg, #EB6600, #031B4E); margin: 10px 0; border: none;">', unsafe_allow_html=True)
            
            st.markdown("<h3>Nuestros Asistentes:</h3>", unsafe_allow_html=True)
            
            # Usar listas nativas de Streamlit para evitar problemas de renderizado
            st.markdown("• **Asistente de Voz** - Interactúe mediante comandos de voz")
            st.markdown("• **Asistente de Energía** - Consulte información sobre consumo y eficiencia energética")
            st.markdown("• **Asistente Textil** - Obtenga asistencia relacionada con nuestros productos textiles")
        
        with col2:
            st.image("logo_sume2.png", width=150)
    
    # Asistente de Voz
    elif selected == "Asistente de Voz":
        # Encabezado del asistente
        st.markdown("""
        <div class="assistant-card">
            <div style="display: flex; align-items: center;">
                <i class="material-icons icon-large">mic</i>
                <h2 style="margin-left: 10px; margin-bottom: 0;">Asistente de Voz</h2>
            </div>
            <p>Interactúa a través de la voz con nuestro asistente inteligente.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Añadir columnas para estructurar mejor el contenido
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Widget de voz con Elevenlabs (altura reducida)
            html_voice = """
            <div style="background-color: #f8f8f8; border-radius: 10px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 0;">
                <div style="height: 450px;">
                    <elevenlabs-convai agent-id="gMh8bGtmxS5OxxPwDuKT"></elevenlabs-convai>
                    <script src="https://elevenlabs.io/convai-widget/index.js" async></script>
                </div>
            </div>
            """
            st.markdown('<div style="margin-top: -10px;">', unsafe_allow_html=True)
            components.html(html_voice, height=450, scrolling=False)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Información descriptiva del asistente de voz - usando método nativo de Streamlit para evitar HTML visible
            st.markdown("""
            <div style="background-color: #f8f8f8; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 0; border-left: 3px solid #EB6600;">
                <h4 style="color: #031B4E; margin-top: 0; margin-bottom: 20px; font-size: 18px;">Características</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Usar componentes nativos de Streamlit para las listas con más espacio
            st.markdown("<div style='margin-bottom: 12px;'>• Interacción por comandos de voz</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Reconocimiento de lenguaje natural</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Respuestas claras y conversacionales</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Compatible con diferentes acentos</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Navegación manos libres por servicios</div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #f8f8f8; padding-left: 15px; padding-bottom: 5px; margin-top: 25px;">
                <h4 style="color: #031B4E; margin-top: 15px; margin-bottom: 20px; font-size: 18px;">¿Qué puedes preguntar?</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Usar componentes nativos de Streamlit para las preguntas con más espacio
            st.markdown("<div style='margin-bottom: 12px;'>• \"¿Qué servicios ofrece SUME Energy?\"</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• \"Necesito información sobre productos\"</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• \"¿Cómo puedo contactar a un asesor?\"</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• \"Cuéntame sobre las soluciones energéticas\"</div>", unsafe_allow_html=True)
    
    # Asistente de Energía
    elif selected == "Asistente de Energía":
        # Encabezado del asistente
        st.markdown("""
        <div class="assistant-card">
            <div style="display: flex; align-items: center;">
                <i class="material-icons icon-large">bolt</i>
                <h2 style="margin-left: 10px; margin-bottom: 0;">Asistente de Energía</h2>
            </div>
            <p>Consulta información sobre consumo energético, eficiencia y recomendaciones personalizadas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Añadir columnas para estructurar mejor el contenido
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Widget de chatbot de energía (altura reducida)
            html_energy = """
            <div style="background-color: #f8f8f8; border-radius: 10px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 0;">
                <div style="height: 450px;">
                    <script async
                      src="https://agent-3f4373bb9b9e2521b014-cd9qj.ondigitalocean.app/static/chatbot/widget.js"
                      data-agent-id="de703369-fcf2-11ef-bf8f-4e013e2ddde4"
                      data-chatbot-id="M1iBgnKnoSo7U1LS4gvPlJbUb5VWTaWG"
                      data-name="Electra - Asistente de Energía"
                      data-primary-color="#EB6600"
                      data-secondary-color="#E5E8ED"
                      data-button-background-color="#EB6600"
                      data-starting-message="Hola soy Electra, la asistente Digital de SUME EnergyC, ¿en qué puedo ayudarte?"
                      data-logo="/static/chatbot/icons/default-agent.svg">
                    </script>
                </div>
            </div>
            """
            st.markdown('<div style="margin-top: -10px;">', unsafe_allow_html=True)
            components.html(html_energy, height=470)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Información descriptiva del asistente - usando el método nativo de Streamlit para evitar HTML visible
            st.markdown("""
            <div style="background-color: #f8f8f8; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 0; border-left: 3px solid #EB6600;">
                <h4 style="color: #031B4E; margin-top: 0; margin-bottom: 20px; font-size: 18px;">Características</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Usar componentes nativos de Streamlit para las listas con más espacio
            st.markdown("<div style='margin-bottom: 12px;'>• Monitoreo de consumo energético en tiempo real</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Análisis de patrones de uso de energía</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Recomendaciones personalizadas para ahorro</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Alertas de consumo inusual</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Calculadora de eficiencia energética</div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #f8f8f8; padding-left: 15px; padding-bottom: 5px; margin-top: 25px;">
                <h4 style="color: #031B4E; margin-top: 15px; margin-bottom: 20px; font-size: 18px;">¿Qué puedes preguntar?</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Usar componentes nativos de Streamlit para las preguntas con más espacio
            st.markdown("<div style='margin-bottom: 12px;'>• ¿Cómo reducir mi factura eléctrica?</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• ¿Cuáles son mis horas de mayor consumo?</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Comparación de consumo mensual</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Tips para mejorar la eficiencia energética</div>", unsafe_allow_html=True)
    
    # Asistente Textil
    elif selected == "Asistente Textil":
        # Encabezado del asistente
        st.markdown("""
        <div class="assistant-card">
            <div style="display: flex; align-items: center;">
                <i class="material-icons icon-large">layers</i>
                <h2 style="margin-left: 10px; margin-bottom: 0;">Asistente Textil</h2>
            </div>
            <p>Resuelve tus dudas sobre nuestros productos textiles y recomendaciones personalizadas.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Añadir columnas para estructurar mejor el contenido
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Widget de chatbot textil (altura reducida)
            html_textile = """
            <div style="background-color: #f8f8f8; border-radius: 10px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 0;">
                <div style="height: 450px;">
                    <script async
                      src="https://uq726hao4xro7jumqyhtswwr.agents.do-ai.run/static/chatbot/widget.js"
                      data-agent-id="7b5424b4-04e6-11f0-bf8f-4e013e2ddde4"
                      data-chatbot-id="w2nmpPtU6h_qGYKXdZ1-hSmvAlRhkzKQ"
                      data-name="Asistente Textil SUME"
                      data-primary-color="#031B4E"
                      data-secondary-color="#E5E8ED"
                      data-button-background-color="#0061EB"
                      data-starting-message="¡Hola! ¿En qué puedo asistirte con nuestros productos textiles?"
                      data-logo="/static/chatbot/icons/default-agent.svg">
                    </script>
                </div>
            </div>
            """
            st.markdown('<div style="margin-top: -10px;">', unsafe_allow_html=True)
            components.html(html_textile, height=470)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Información descriptiva del asistente textil - usando método nativo de Streamlit
            st.markdown("""
            <div style="background-color: #f8f8f8; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 0; border-left: 3px solid #031B4E;">
                <h4 style="color: #031B4E; margin-top: 0; margin-bottom: 20px; font-size: 18px;">Características</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Usar componentes nativos de Streamlit para las listas con más espacio
            st.markdown("<div style='margin-bottom: 12px;'>• Catálogo completo de productos textiles</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Especificaciones técnicas detalladas</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Recomendaciones según necesidades</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Información sobre disponibilidad</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Guía de mantenimiento y cuidados</div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #f8f8f8; padding-left: 15px; padding-bottom: 5px; margin-top: 25px;">
                <h4 style="color: #031B4E; margin-top: 15px; margin-bottom: 20px; font-size: 18px;">¿Qué puedes preguntar?</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Usar componentes nativos de Streamlit para las preguntas con más espacio
            st.markdown("<div style='margin-bottom: 12px;'>• ¿Qué materiales usan en sus productos?</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• ¿Tienen opciones sostenibles?</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Recomendaciones según mi industria</div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 12px;'>• Información de envíos y disponibilidad</div>", unsafe_allow_html=True)
    
    # Acerca de
    elif selected == "Acerca de":
        st.markdown("""
        <div class="assistant-card">
            <h2>Acerca de SUME Energy</h2>
            <p>SUME Energy es una empresa comprometida con la innovación y la eficiencia energética.
            Nuestros asistentes digitales están diseñados para facilitar el acceso a nuestros servicios
            y proporcionar una experiencia de usuario excepcional.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Usar componentes nativos de Streamlit para el divisor y la lista
        st.markdown('<hr style="height: 3px; background: linear-gradient(90deg, #EB6600, #031B4E); margin: 10px 0; border: none;">', unsafe_allow_html=True)
        
        st.markdown("<h3>Contacto</h3>", unsafe_allow_html=True)
        st.markdown("Para más información, contáctenos a través de:")
        
        # Usar texto nativo de Streamlit para la lista
        st.markdown("• Email: info@sume-energy.com")
        st.markdown("• Teléfono: +123 456 7890")
        st.markdown("• Dirección: Calle Principal 123, Ciudad")
        
        st.image("logo_sume2.png", width=200)

    # Aplicar material design
    st.markdown("""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Footer compacto
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 5px; text-align: center; border-top: 1px solid #ddd; margin-top: 10px;">
        <p style="margin: 0; font-size: 12px;">© 2025 SUME Energy - Todos los derechos reservados</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

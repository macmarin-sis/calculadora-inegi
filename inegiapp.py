import streamlit as st
import pandas as pd

# Título
#st.title("Filtro de datos INEGI")

# Entradas del usuario
#estado = st.number_input("Número de estado", min_value=1, max_value=32, step=1)
#municipio = st.number_input("Número de municipio", min_value=1, step=1)



#===============================================================================
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Indicadores INEGI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Token de la API
TOKEN = "153e4680-d5df-e1b1-b367-6a6c2d1dda05"

# Diccionario de indicadores
INDICADORES = {
    'poblacion': {
        'codigo': '1002000001',
        'nombre': 'Población Total',
        'color': '#2E86AB',
        'unidad': 'habitantes'
    },
    'viviendas': {
        'codigo': '1003000001',
        'nombre': 'Total de Viviendas Particulares Habitadas',
        'color': '#A23B72',
        'unidad': 'viviendas'
    },
    'ocupantes_vivienda': {
        'codigo': '1003000015',
        'nombre': 'Promedio de Ocupantes por Vivienda',
        'color': '#F18F01',
        'unidad': 'personas/vivienda'
    }
}

# Diccionario de estados (códigos INEGI)
ESTADOS_MEXICO = {
    "01": "Aguascalientes",
    "02": "Baja California",
    "03": "Baja California Sur",
    "04": "Campeche",
    "05": "Coahuila de Zaragoza",
    "06": "Colima",
    "07": "Chiapas",
    "08": "Chihuahua",
    "09": "Ciudad de México",
    "10": "Durango",
    "11": "Guanajuato",
    "12": "Guerrero",
    "13": "Hidalgo",
    "14": "Jalisco",
    "15": "México",
    "16": "Michoacán de Ocampo",
    "17": "Morelos",
    "18": "Nayarit",
    "19": "Nuevo León",
    "20": "Oaxaca",
    "21": "Puebla",
    "22": "Querétaro",
    "23": "Quintana Roo",
    "24": "San Luis Potosí",
    "25": "Sinaloa",
    "26": "Sonora",
    "27": "Tabasco",
    "28": "Tamaulipas",
    "29": "Tlaxcala",
    "30": "Veracruz de Ignacio de la Llave",
    "31": "Yucatán",
    "32": "Zacatecas"
}

@st.cache_data(ttl=3600)
def obtener_datos_indicador(codigo_indicador, codigo_estado, codigo_municipio):
    """Obtiene datos de un indicador específico para un municipio"""
    try:
        # Formatear el código de municipio a 3 dígitos
        codigo_municipio_str = str(codigo_municipio).zfill(3)
        
        url = f"https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/{codigo_indicador}/es/{codigo_estado}{codigo_municipio_str}/false/BISE/2.0/{TOKEN}?type=json"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        datos = response.json()
        
        # Verificar si hay datos disponibles
        if 'Series' not in datos or len(datos['Series']) == 0:
            return None, "No hay datos disponibles para esta combinación"
        
        # Procesar los datos
        series = datos['Series'][0]
        observaciones = series['OBSERVATIONS']
        
        # Crear DataFrame
        df = pd.DataFrame(observaciones)
        df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
        df['TIME_PERIOD'] = pd.to_numeric(df['TIME_PERIOD'], errors='coerce')
        df = df.sort_values('TIME_PERIOD')
        
        return df, None
        
    except Exception as e:
        return None, str(e)

def crear_visualizacion_comparativa(datos_completos, estado_nombre, municipio_codigo):
    """Crea la visualización comparativa de los indicadores"""
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(20, 15))
    
    # Gráfica 1: Evolución de los tres indicadores
    ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2)
    for key, indicador in INDICADORES.items():
        if key in datos_completos and datos_completos[key] is not None and not datos_completos[key].empty:
            df = datos_completos[key]
            ax1.plot(df['TIME_PERIOD'], df['OBS_VALUE'], 'o-', 
                    linewidth=2.5, markersize=6, 
                    color=indicador['color'], 
                    label=indicador['nombre'])
    
    ax1.set_title(f'Evolución Comparativa de Indicadores\nMunicipio {municipio_codigo}, {estado_nombre}', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Año')
    ax1.set_ylabel('Valor')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfica 2: Población Total
    ax2 = plt.subplot2grid((3, 3), (0, 2))
    if 'poblacion' in datos_completos and datos_completos['poblacion'] is not None and not datos_completos['poblacion'].empty:
        df_pob = datos_completos['poblacion']
        bars = ax2.bar(df_pob['TIME_PERIOD'], df_pob['OBS_VALUE'], 
                       color=INDICADORES['poblacion']['color'], alpha=0.7)
        ax2.set_title('Población Total', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Año')
        ax2.set_ylabel('Habitantes')
        ax2.ticklabel_format(style='plain', axis='y')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (height*0.01),
                    f'{height:,.0f}', ha='center', va='bottom', fontsize=8)
    
    # Gráfica 3: Total de Viviendas
    ax3 = plt.subplot2grid((3, 3), (1, 0))
    if 'viviendas' in datos_completos and datos_completos['viviendas'] is not None and not datos_completos['viviendas'].empty:
        df_viv = datos_completos['viviendas']
        bars = ax3.bar(df_viv['TIME_PERIOD'], df_viv['OBS_VALUE'], 
                       color=INDICADORES['viviendas']['color'], alpha=0.7)
        ax3.set_title('Total de Viviendas Habitadas', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Año')
        ax3.set_ylabel('Viviendas')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + (height*0.01),
                    f'{height:,.0f}', ha='center', va='bottom', fontsize=8)
    
    # Gráfica 4: Ocupantes por Vivienda
    ax4 = plt.subplot2grid((3, 3), (1, 1))
    if 'ocupantes_vivienda' in datos_completos and datos_completos['ocupantes_vivienda'] is not None and not datos_completos['ocupantes_vivienda'].empty:
        df_ocup = datos_completos['ocupantes_vivienda']
        bars = ax4.bar(df_ocup['TIME_PERIOD'], df_ocup['OBS_VALUE'], 
                       color=INDICADORES['ocupantes_vivienda']['color'], alpha=0.7)
        ax4.set_title('Ocupantes por Vivienda', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Año')
        ax4.set_ylabel('Personas por Vivienda')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    
    # Gráfica 5: Relación Población-Viviendas
    ax5 = plt.subplot2grid((3, 3), (1, 2))
    if ('poblacion' in datos_completos and datos_completos['poblacion'] is not None and not datos_completos['poblacion'].empty and 
        'viviendas' in datos_completos and datos_completos['viviendas'] is not None and not datos_completos['viviendas'].empty):
        
        df_pob = datos_completos['poblacion']
        df_viv = datos_completos['viviendas']
        
        # Unir datos por año
        merged = pd.merge(df_pob, df_viv, on='TIME_PERIOD', suffixes=('_pob', '_viv'))
        merged['personas_por_vivienda'] = merged['OBS_VALUE_pob'] / merged['OBS_VALUE_viv']
        
        bars = ax5.bar(merged['TIME_PERIOD'], merged['personas_por_vivienda'], 
                       color='#1B998B', alpha=0.7)
        ax5.set_title('Personas por Vivienda (Cálculo)', fontsize=14, fontweight='bold')
        ax5.set_xlabel('Año')
        ax5.set_ylabel('Personas/Vivienda')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    
    # Gráfica 6: Resumen comparativo
    ax6 = plt.subplot2grid((3, 3), (2, 0), colspan=3)
    ax6.axis('off')
    
    # Calcular estadísticas comparativas
    info_text = f" RESUMEN COMPARATIVO - MUNICIPIO {municipio_codigo}, {estado_nombre.upper()}\n"
    info_text += "=" * 60 + "\n\n"
    
    for key, indicador in INDICADORES.items():
        if key in datos_completos and datos_completos[key] is not None and not datos_completos[key].empty:
            df = datos_completos[key]
            ultimo_valor = df['OBS_VALUE'].iloc[-1]
            primer_valor = df['OBS_VALUE'].iloc[0]
            crecimiento = ((ultimo_valor - primer_valor) / primer_valor * 100) if primer_valor != 0 else 0
            
            info_text += f"● {indicador['nombre']}:\n"
            info_text += f"   - Actual: {ultimo_valor:,.2f} {indicador['unidad']}\n"
            info_text += f"   - Crecimiento total: {crecimiento:+.1f}%\n"
            info_text += f"   - Período: {int(df['TIME_PERIOD'].min())}-{int(df['TIME_PERIOD'].max())}\n\n"
    
    # Análisis de relación entre indicadores
    if ('poblacion' in datos_completos and datos_completos['poblacion'] is not None and not datos_completos['poblacion'].empty and 
        'viviendas' in datos_completos and datos_completos['viviendas'] is not None and not datos_completos['viviendas'].empty):
        
        df_pob = datos_completos['poblacion']
        df_viv = datos_completos['viviendas']
        
        # Encontrar años comunes
        años_comunes = set(df_pob['TIME_PERIOD']).intersection(set(df_viv['TIME_PERIOD']))
        if años_comunes:
            año_mas_reciente = max(años_comunes)
            pob_reciente = df_pob[df_pob['TIME_PERIOD'] == año_mas_reciente]['OBS_VALUE'].values[0]
            viv_reciente = df_viv[df_viv['TIME_PERIOD'] == año_mas_reciente]['OBS_VALUE'].values[0]
            
            densidad = pob_reciente / viv_reciente if viv_reciente != 0 else 0
            
            info_text += " ANÁLISIS DE RELACIÓN:\n"
            info_text += f"   - Densidad calculada ({int(año_mas_reciente)}): {densidad:.2f} personas/vivienda\n"
            info_text += f"   - Población por vivienda: {pob_reciente:,.0f} / {viv_reciente:,.0f}\n"
    
    ax6.text(0.02, 0.98, info_text, transform=ax6.transAxes, fontsize=11, 
             verticalalignment='top', fontfamily='monospace', linespacing=1.5)
    
    plt.tight_layout()
    return fig

def crear_tabla_detallada(df, indicador):
    """Crea una tabla detallada formateada para un indicador"""
    if df is None or df.empty:
        return None
    
    df_display = df.copy()
    df_display['Año'] = df_display['TIME_PERIOD'].astype(int)
    
    # Formatear valores según el indicador
    if indicador['nombre'] == 'Promedio de Ocupantes por Vivienda':
        df_display['Valor'] = df_display['OBS_VALUE'].apply(lambda x: f"{x:,.2f} {indicador['unidad']}")
    else:
        df_display['Valor'] = df_display['OBS_VALUE'].apply(lambda x: f"{x:,.0f} {indicador['unidad']}")
    
    # Calcular crecimiento anual
    df_display['Crecimiento %'] = df_display['OBS_VALUE'].pct_change() * 100
    df_display['Crecimiento %'] = df_display['Crecimiento %'].apply(
        lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
    )
    
    return df_display[['Año', 'Valor', 'Crecimiento %']]

def main():
    # Título principal
    st.title("📊 Indicadores Demográficos INEGI")
    st.markdown("Consulta datos de población, vivienda y demográficos para cualquier municipio de México")
    st.markdown("---")
    
    # Sidebar para selección de ubicación
    with st.sidebar:
        st.header("📍 Selección de Ubicación")
        st.markdown("---")
        
        # Selector de estado
        estado_seleccionado = st.selectbox(
            "Selecciona un Estado:",
            options=list(ESTADOS_MEXICO.keys()),
            format_func=lambda x: f"{x} - {ESTADOS_MEXICO[x]}",
            index=20  # Puebla por defecto
        )
        
        estado_nombre = ESTADOS_MEXICO[estado_seleccionado]
        
        st.markdown("---")
        st.subheader("🏙️ Código de Municipio")
        
        # Entrada numérica para el código de municipio
        municipio_numero = st.number_input(
            "Número de municipio (código INEGI):",
            min_value=1,
            max_value=999,
            value=136,  # Cuautlancingo por defecto
            step=1,
            help="Ingresa el código numérico del municipio según INEGI (ej: 136 para Cuautlancingo, Puebla)"
        )
        
        # Convertir a string con 3 dígitos
        municipio_codigo = str(int(municipio_numero)).zfill(3)
        
        # Mostrar código formateado
        st.info(f"**Código municipio:** {municipio_codigo}")
        st.info(f"**Código completo INEGI:** {estado_seleccionado}{municipio_codigo}")
        
        st.markdown("---")
        st.subheader("📊 Indicadores a mostrar")
        mostrar_poblacion = st.checkbox("Población Total", value=True)
        mostrar_viviendas = st.checkbox("Viviendas Habitadas", value=True)
        mostrar_ocupantes = st.checkbox("Ocupantes por Vivienda", value=True)
        
        st.markdown("---")
        
        # Botón para consultar datos
        if st.button("🔍 Consultar Datos", type="primary", use_container_width=True):
            st.session_state.consultar = True
            st.rerun()
        
        # Botón para limpiar cache
        if st.button("🧹 Limpiar Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache limpiado!")
            if 'consultar' in st.session_state:
                st.session_state.consultar = False
        
        st.markdown("---")
        
        # Mostrar código INEGI para copiar
        st.subheader("📝 Código INEGI")
        st.code(f"ESTADO = \"{estado_seleccionado}\"\nMUNICIPIO = \"{municipio_codigo}\"")
        
        st.markdown("---")
        
        # Ejemplos de códigos comunes
        with st.expander("📚 Ejemplos de códigos"):
            st.markdown("""
            **Puebla (21):**
            - 136: Cuautlancingo
            - 114: Puebla (municipio)
            - 001: Acajete
            
            **Ciudad de México (09):**
            - 002: Azcapotzalco
            - 003: Coyoacán
            - 015: Álvaro Obregón
            
            **Jalisco (14):**
            - 039: Guadalajara
            - 067: Puerto Vallarta
            - 120: Zapopan
            
            **Nota:** Los códigos van del 001 al 999 según cada estado.
            """)
    
    # Mostrar ubicación seleccionada
    st.subheader(f"📍 Datos para Municipio {municipio_codigo}, {estado_nombre}")
    st.caption(f"Código INEGI: {estado_seleccionado}{municipio_codigo}")
    
    # Mostrar indicadores seleccionados
    indicadores_seleccionados = {}
    if mostrar_poblacion:
        indicadores_seleccionados['poblacion'] = INDICADORES['poblacion']
    if mostrar_viviendas:
        indicadores_seleccionados['viviendas'] = INDICADORES['viviendas']
    if mostrar_ocupantes:
        indicadores_seleccionados['ocupantes_vivienda'] = INDICADORES['ocupantes_vivienda']
    
    if not indicadores_seleccionados:
        st.warning("Selecciona al menos un indicador en la barra lateral.")
        return
    
    # Verificar si se debe consultar datos
    if 'consultar' not in st.session_state:
        st.session_state.consultar = False
    
    if st.session_state.consultar:
        # Barra de progreso para la carga de datos
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Obtener datos
        datos_completos = {}
        errores = []
        
        total_indicadores = len(indicadores_seleccionados)
        for i, (key, indicador) in enumerate(indicadores_seleccionados.items()):
            status_text.text(f"Obteniendo {indicador['nombre']}...")
            progress = (i + 1) / total_indicadores
            progress_bar.progress(progress)
            
            df, error = obtener_datos_indicador(
                indicador['codigo'], 
                estado_seleccionado, 
                municipio_codigo
            )
            
            if error:
                errores.append(f"{indicador['nombre']}: {error}")
                datos_completos[key] = None
            else:
                datos_completos[key] = df
        
        # Limpiar barra de progreso
        progress_bar.empty()
        status_text.empty()
        
        # Mostrar errores si los hay
        if errores:
            with st.expander("⚠️ Advertencias y Errores", expanded=True):
                for error in errores:
                    st.warning(error)
        
        # Verificar si hay datos para mostrar
        datos_validos = [d for d in datos_completos.values() if d is not None and not d.empty]
        if not datos_validos:
            st.error("""
            ❌ No se pudieron obtener datos para los indicadores seleccionados.
            
            **Posibles causas:**
            1. El código de municipio podría ser incorrecto
            2. El municipio no tiene datos disponibles para los indicadores seleccionados
            3. Problemas de conexión con la API del INEGI
            
            **Sugerencias:**
            - Verifica el código del municipio (001-999)
            - Prueba con otro código de municipio
            - Asegúrate de que el estado sea correcto
            """)
            return
        
        st.success(f"✅ Datos obtenidos exitosamente para Municipio {municipio_codigo}")
        
        # Mostrar visualización comparativa
        st.markdown("---")
        st.subheader("📈 Visualización Comparativa")
        
        try:
            fig = crear_visualizacion_comparativa(datos_completos, estado_nombre, municipio_codigo)
            st.pyplot(fig)
            
            # Opción para descargar la gráfica
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💾 Descargar Gráfica como PNG"):
                    nombre_archivo = f"indicadores_{estado_seleccionado}_{municipio_codigo}.png"
                    fig.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
                    
                    with open(nombre_archivo, "rb") as file:
                        btn = st.download_button(
                            label="📥 Descargar ahora",
                            data=file,
                            file_name=nombre_archivo,
                            mime="image/png"
                        )
                    
        except Exception as e:
            st.error(f"Error al crear la visualización: {e}")
            return
        
        st.markdown("---")
        
        # Mostrar tablas detalladas
        st.subheader("📋 Tablas Detalladas por Indicador")
        
        cols = st.columns(min(3, len(indicadores_seleccionados)))
        
        for i, (key, indicador) in enumerate(indicadores_seleccionados.items()):
            if key in datos_completos and datos_completos[key] is not None:
                with cols[i % len(cols)]:
                    st.markdown(f"**{indicador['nombre']}**")
                    
                    tabla = crear_tabla_detallada(datos_completos[key], indicador)
                    if tabla is not None:
                        st.dataframe(
                            tabla,
                            use_container_width=True,
                            hide_index=True,
                            height=300
                        )
                        
                        # Estadísticas rápidas
                        df = datos_completos[key]
                        with st.expander("📊 Estadísticas Detalladas"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                crecimiento_total = ((df['OBS_VALUE'].iloc[-1] - df['OBS_VALUE'].iloc[0]) / 
                                                   df['OBS_VALUE'].iloc[0] * 100)
                                st.metric("Valor Actual", 
                                        f"{df['OBS_VALUE'].iloc[-1]:,.0f}",
                                        f"{crecimiento_total:+.1f}% total")
                            with col2:
                                st.metric("Valor Mínimo", 
                                        f"{df['OBS_VALUE'].min():,.0f}",
                                        f"Año {int(df.loc[df['OBS_VALUE'].idxmin(), 'TIME_PERIOD'])}")
                            with col3:
                                st.metric("Valor Máximo", 
                                        f"{df['OBS_VALUE'].max():,.0f}",
                                        f"Año {int(df.loc[df['OBS_VALUE'].idxmax(), 'TIME_PERIOD'])}")
                            
                            # Crecimiento promedio anual
                            if len(df) > 1:
                                crecimiento_anual_promedio = (df['OBS_VALUE'].iloc[-1] / df['OBS_VALUE'].iloc[0]) ** (1/(len(df)-1)) - 1
                                st.metric("Crecimiento Anual Promedio", 
                                        f"{crecimiento_anual_promedio*100:+.2f}%")
        
        st.markdown("---")
        
        # Análisis comparativo final
        st.subheader("🔍 Análisis Comparativo")
        
        # Verificar que tenemos datos para comparar
        indicadores_validos = [key for key in datos_completos 
                              if datos_completos[key] is not None and not datos_completos[key].empty]
        
        if len(indicadores_validos) >= 2:
            analisis_text = f"### 📊 Análisis para Municipio {municipio_codigo}, {estado_nombre}\n\n"
            
            # Tendencias
            analisis_text += "#### 📈 Tendencias Observadas:\n\n"
            for key in indicadores_validos:
                df = datos_completos[key]
                crecimiento = ((df['OBS_VALUE'].iloc[-1] - df['OBS_VALUE'].iloc[0]) / 
                              df['OBS_VALUE'].iloc[0] * 100)
                
                if crecimiento > 10:
                    tendencia = "📈 ALTA"
                    color = "green"
                elif crecimiento > 0:
                    tendencia = "↗️ MODERADA"
                    color = "lightgreen"
                elif crecimiento > -10:
                    tendencia = "↘️ BAJA"
                    color = "orange"
                else:
                    tendencia = "📉 DECRECIENTO"
                    color = "red"
                
                analisis_text += f"- **{INDICADORES[key]['nombre']}**: <span style='color:{color}'>{tendencia}</span> ({crecimiento:+.1f}%)\n"
            
            # Análisis de correlación
            if 'poblacion' in indicadores_validos and 'viviendas' in indicadores_validos:
                df_pob = datos_completos['poblacion']
                df_viv = datos_completos['viviendas']
                
                años_comunes = sorted(set(df_pob['TIME_PERIOD']).intersection(set(df_viv['TIME_PERIOD'])))
                if len(años_comunes) > 1:
                    pob_comunes = [df_pob[df_pob['TIME_PERIOD'] == año]['OBS_VALUE'].values[0] for año in años_comunes]
                    viv_comunes = [df_viv[df_viv['TIME_PERIOD'] == año]['OBS_VALUE'].values[0] for año in años_comunes]
                    
                    correlacion = np.corrcoef(pob_comunes, viv_comunes)[0,1]
                    
                    analisis_text += f"\n#### 🔗 Correlación Población-Viviendas: {correlacion:.3f}\n\n"
                    
                    if correlacion > 0.8:
                        analisis_text += "**Interpretación**: Alta correlación positiva. El crecimiento de viviendas sigue estrechamente al crecimiento de población."
                    elif correlacion > 0.5:
                        analisis_text += "**Interpretación**: Correlación moderada. Existe una relación positiva entre el crecimiento de población y viviendas."
                    elif correlacion > 0:
                        analisis_text += "**Interpretación**: Correlación baja positiva. Relación débil entre las variables."
                    elif correlacion == 0:
                        analisis_text += "**Interpretación**: No hay correlación lineal entre las variables."
                    else:
                        analisis_text += "**Interpretación**: Correlación negativa. Comportamientos opuestos entre las variables."
            
            st.markdown(analisis_text, unsafe_allow_html=True)
        
        # Opción para exportar datos
        st.markdown("---")
        st.subheader("📤 Exportar Datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Exportar a Excel"):
                # Crear un archivo Excel con múltiples hojas
                with pd.ExcelWriter(f"datos_{estado_seleccionado}_{municipio_codigo}.xlsx") as writer:
                    for key in datos_completos:
                        if datos_completos[key] is not None and not datos_completos[key].empty:
                            df = datos_completos[key]
                            df_export = df[['TIME_PERIOD', 'OBS_VALUE']].copy()
                            df_export.columns = ['Año', INDICADORES[key]['nombre']]
                            df_export.to_excel(writer, sheet_name=key[:31], index=False)
                
                with open(f"datos_{estado_seleccionado}_{municipio_codigo}.xlsx", "rb") as file:
                    st.download_button(
                        label="📥 Descargar Excel",
                        data=file,
                        file_name=f"datos_{estado_seleccionado}_{municipio_codigo}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        with col2:
            if st.button("📄 Exportar a CSV"):
                # Crear un DataFrame combinado
                dfs = []
                for key in datos_completos:
                    if datos_completos[key] is not None and not datos_completos[key].empty:
                        df = datos_completos[key].copy()
                        df['Indicador'] = INDICADORES[key]['nombre']
                        df = df[['TIME_PERIOD', 'Indicador', 'OBS_VALUE']]
                        dfs.append(df)
                
                if dfs:
                    df_combinado = pd.concat(dfs, ignore_index=True)
                    df_combinado.to_csv(f"datos_{estado_seleccionado}_{municipio_codigo}.csv", index=False)
                    
                    with open(f"datos_{estado_seleccionado}_{municipio_codigo}.csv", "rb") as file:
                        st.download_button(
                            label="📥 Descargar CSV",
                            data=file,
                            file_name=f"datos_{estado_seleccionado}_{municipio_codigo}.csv",
                            mime="text/csv"
                        )
        
        with col3:
            if st.button("🔄 Nueva Consulta"):
                st.session_state.consultar = False
                st.rerun()
    
    else:
        # Mostrar instrucciones si no se ha consultado
        st.info("""
        ### Instrucciones:
        1. **Selecciona un estado** en el menú lateral
        2. **Ingresa el código del municipio** (número de 1 a 999)
        3. **Selecciona los indicadores** que deseas consultar
        4. **Haz clic en 'Consultar Datos'** para obtener la información
        
        ### Ejemplo para Puebla:
        - Estado: 21 - Puebla
        - Municipio: 136 (Cuautlancingo)
        - Código completo: 21136
        """)
        
   
    # Información del pie de página
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    with col2:
        st.caption(f"📍 {estado_nombre} - Municipio {municipio_codigo}")
    with col3:
        st.caption("Fuente: API INEGI")

if __name__ == "__main__":
    main()

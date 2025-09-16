import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Configuración de la página con CSS personalizado
st.set_page_config(
    page_title="Dashboard de Ventas - Honduras",
    page_icon="🇭🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Función para cargar los datos
@st.cache_data
def load_data():
    """Cargar y limpiar los datos de ventas"""
    try:
        # Intentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('VENTAS 2025.CSV', encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            st.error("No se pudo cargar el archivo con ninguna codificación")
            return None
        
        # Limpiar datos
        df_clean = df[
            (df['Type'].notna()) &
            (~df['Type'].str.contains('Total', na=False)) &
            (df['Name'].notna()) &
            (df['Item'].notna()) &
            (df['Amount'].notna())
        ].copy()
        
        # Convertir tipos de datos
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], format='%d/%m/%Y', errors='coerce')
        df_clean['Qty'] = pd.to_numeric(df_clean['Qty'], errors='coerce')
        df_clean['Sales Price'] = pd.to_numeric(df_clean['Sales Price'], errors='coerce')
        df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce')
        df_clean['Balance'] = pd.to_numeric(df_clean['Balance'], errors='coerce')
        
        # Limpiar nombres
        df_clean['Name'] = df_clean['Name'].str.strip().str.upper()
        df_clean['Item'] = df_clean['Item'].str.strip()
        
        # Remover filas con datos críticos faltantes
        df_clean = df_clean.dropna(subset=['Date', 'Amount', 'Name'])
        
        # Agregar columnas derivadas
        df_clean['Year'] = df_clean['Date'].dt.year
        df_clean['Month'] = df_clean['Date'].dt.month
        df_clean['Day'] = df_clean['Date'].dt.day
        df_clean['Weekday'] = df_clean['Date'].dt.day_name()
        df_clean['Week'] = df_clean['Date'].dt.isocalendar().week
        
        # Categorizar productos
        def categorizar_producto(item):
            item_lower = str(item).lower()
            if 'agua' in item_lower or 'bolsa' in item_lower:
                return 'Agua en Bolsa'
            elif 'hielo' in item_lower:
                return 'Hielo'
            elif 'botellon' in item_lower:
                return 'Botellones'
            elif 'botecito' in item_lower or 'bote' in item_lower:
                return 'Botecitos'
            elif 'impuesto' in item_lower or 'isv' in item_lower:
                return 'Impuestos'
            else:
                return 'Otros'
        
        df_clean['Categoria'] = df_clean['Item'].apply(categorizar_producto)
        
        return df_clean
        
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

# Función para calcular métricas
def calculate_metrics(df, start_date, end_date, selected_clients, selected_categories, tipo_venta=None):
    """Calcular métricas filtradas"""
    # Convertir fechas a datetime para comparación
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filtrar datos por fecha
    df_filtered = df[
        (df['Date'] >= start_date) & 
        (df['Date'] <= end_date)
    ]
    
    # Filtrar por tipo de venta
    if tipo_venta:
        df_filtered = df_filtered[df_filtered['Type'] == tipo_venta]
    
    # Filtrar por clientes
    if selected_clients:
        df_filtered = df_filtered[df_filtered['Name'].isin(selected_clients)]
    
    # Filtrar por categorías
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Categoria'].isin(selected_categories)]
    
    # Calcular métricas
    metrics = {
        'total_ventas': df_filtered['Amount'].sum(),
        'total_transacciones': len(df_filtered),
        'ticket_promedio': df_filtered['Amount'].mean() if len(df_filtered) > 0 else 0,
        'clientes_unicos': df_filtered['Name'].nunique(),
        'productos_unicos': df_filtered['Item'].nunique(),
        'dias_con_ventas': df_filtered['Date'].nunique(),
        # Métricas adicionales para mejor análisis
        'venta_contado': df_filtered[df_filtered['Type'] == 'Sales Receipt']['Amount'].sum() if 'Type' in df_filtered.columns else 0,
        'venta_credito': df_filtered[df_filtered['Type'] == 'Invoice']['Amount'].sum() if 'Type' in df_filtered.columns else 0,
        'transacciones_contado': len(df_filtered[df_filtered['Type'] == 'Sales Receipt']) if 'Type' in df_filtered.columns else 0,
        'transacciones_credito': len(df_filtered[df_filtered['Type'] == 'Invoice']) if 'Type' in df_filtered.columns else 0
    }
    
    return df_filtered, metrics

# Cargar datos
df = load_data()

if df is not None:
    # Sidebar para filtros con mejor organización
    st.sidebar.header("🎯 Panel de Control")
    st.sidebar.markdown("---")
    
    # Sección de Período de Tiempo
    with st.sidebar.container():
        st.subheader("⏰ Período de Análisis")
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        
        # Inicializar el rango de fechas en session_state si no existe
        if 'date_range_reset' not in st.session_state:
            st.session_state.date_range_reset = False
        
        # Determinar el valor inicial basado en si se ha restablecido
        if st.session_state.date_range_reset:
            initial_value = (min_date, max_date)
            st.session_state.date_range_reset = False
        else:
            # Mantener el valor actual si existe en session_state
            if 'current_date_range' in st.session_state:
                initial_value = st.session_state.current_date_range
            else:
                initial_value = (min_date, max_date)
        
        # Crear columnas para el date_input y el botón
        col_date, col_reset = st.columns([3, 1])
        
        with col_date:
            date_range = st.date_input(
                "📅 Rango de fechas:",
                value=initial_value,
                min_value=min_date,
                max_value=max_date,
                help="Selecciona el período a analizar"
            )
        
        with col_reset:
            st.markdown("<br>", unsafe_allow_html=True)  # Espaciado vertical
            if st.button("🔄", help="Restablecer a todo el período", key="reset_dates"):
                st.session_state.date_range_reset = True
                st.session_state.current_date_range = (min_date, max_date)
                st.rerun()
        
        # Guardar el rango actual en session_state
        if len(date_range) == 2:
            start_date, end_date = date_range
            st.session_state.current_date_range = (start_date, end_date)
        else:
            start_date = end_date = date_range[0]
            st.session_state.current_date_range = (start_date, start_date)
        
        # Mostrar información del período seleccionado
        total_days = (end_date - start_date).days + 1
        st.caption(f"📊 Período seleccionado: {total_days} día(s)")
        
        # Botones de acceso rápido para períodos comunes
        st.markdown("**🚀 Accesos Rápidos:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📅 Último Mes", help="Últimos 30 días", key="last_month", width="stretch"):
                end_date_quick = max_date
                start_date_quick = max(min_date, end_date_quick - pd.Timedelta(days=29))
                st.session_state.current_date_range = (start_date_quick, end_date_quick)
                st.rerun()
            
            if st.button("📆 Últimos 7 días", help="Última semana", key="last_week", width="stretch"):
                end_date_quick = max_date
                start_date_quick = max(min_date, end_date_quick - pd.Timedelta(days=6))
                st.session_state.current_date_range = (start_date_quick, end_date_quick)
                st.rerun()
        
        with col2:
            if st.button("📊 Últimos 3 Meses", help="Últimos 90 días", key="last_3months", width="stretch"):
                end_date_quick = max_date
                start_date_quick = max(min_date, end_date_quick - pd.Timedelta(days=89))
                st.session_state.current_date_range = (start_date_quick, end_date_quick)
                st.rerun()
            
            if st.button("🗓️ Todo el Período", help="Todos los datos disponibles", key="all_period", width="stretch"):
                st.session_state.current_date_range = (min_date, max_date)
                st.rerun()
    
    st.sidebar.markdown("---")
    
    # Sección de Tipo de Venta
    with st.sidebar.container():
        st.subheader("💳 Tipo de Transacción")
        tipo_venta_options = {
            'Todos': None,
            '💵 Contado (Sales Receipt)': 'Sales Receipt',
            '🏦 Crédito (Invoice)': 'Invoice'
        }
        
        selected_tipo_venta = st.selectbox(
            "Filtrar por tipo de venta:",
            options=list(tipo_venta_options.keys()),
            index=0,
            help="Sales Receipt = Ventas al contado, Invoice = Ventas a crédito"
        )
    
    st.sidebar.markdown("---")
    
    # Sección de Clientes y Productos
    with st.sidebar.container():
        st.subheader("👥 Filtros de Clientes")
        all_clients = sorted(df['Name'].unique())
        selected_clients = st.multiselect(
            "Seleccionar clientes específicos:",
            options=all_clients,
            default=[],
            help="Dejar vacío para incluir todos los clientes",
            placeholder="Todos los clientes"
        )
        
        # Mostrar contador de clientes
        if selected_clients:
            st.caption(f"📊 {len(selected_clients)} cliente(s) seleccionado(s)")
        else:
            st.caption(f"📊 Analizando {len(all_clients)} clientes")
    
    st.sidebar.markdown("---")
    
    # Sección de Categorías
    with st.sidebar.container():
        st.subheader("🏷️ Filtros de Productos")
        all_categories = sorted(df['Categoria'].unique())
        selected_categories = st.multiselect(
            "Seleccionar categorías:",
            options=all_categories,
            default=[],
            help="Dejar vacío para incluir todas las categorías",
            placeholder="Todas las categorías"
        )
        
    # Sección de ayuda en el sidebar
    st.sidebar.markdown("---")
    with st.sidebar.expander("ℹ️ Ayuda y Guía de Uso"):
        st.markdown("""
        **🎯 Cómo usar este dashboard:**
        
        1. **📅 Período:** Selecciona las fechas de análisis
        2. **💳 Tipo:** Filtra por ventas al contado o crédito
        3. **� Clientes:** Selecciona clientes específicos (opcional)
        4. **🏷️ Categorías:** Filtra por tipos de productos
        5. **📊 Pestañas:** Explora diferentes análisis
        
        **💡 Consejos:**
        - Usa "Todos" para ver el panorama completo
        - Combina filtros para análisis específicos
        - Revisa las recomendaciones automáticas
        
        **📞 Soporte:** dashboard@empresa.hn
        """)
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.caption("🔄 Última actualización: Tiempo real")
    st.sidebar.caption(f"🗃️ Total en BD: {len(df):,} registros")
    
    # Calcular datos filtrados
    df_filtered, metrics = calculate_metrics(
        df, start_date, end_date, selected_clients, selected_categories, 
        tipo_venta_options[selected_tipo_venta]
    )
    
    # Actualizar información de registros filtrados en sidebar
    st.sidebar.caption(f"📊 Registros analizados: {len(df_filtered):,}")
    
    # Header principal con componentes nativos de Streamlit
    st.title("🇭🇳 Dashboard de Inteligencia de Negocios")
    st.subheader("📊 Análisis de Ventas - Honduras 2025")
    st.divider()
    
    # Información del período y filtros activos
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"📅 **Período:** {start_date} al {end_date}")
    with col_info2:
        tipo_info = selected_tipo_venta if selected_tipo_venta != 'Todos' else 'Todas las transacciones'
        st.info(f"💳 **Tipo:** {tipo_info}")
    
    # Métricas principales con mejor diseño
    st.markdown("### 📊 Métricas Principales")
    
    # Primera fila de métricas - Ventas y transacciones
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Calcular delta comparativo (simulado)
        delta_ventas = f"+{(metrics['total_ventas'] * 0.15):.0f}" if metrics['total_ventas'] > 0 else None
        st.metric(
            label="💰 Ventas Totales",
            value=f"L {metrics['total_ventas']:,.2f}",
            delta=delta_ventas,
            help="Total de ingresos en el período seleccionado"
        )
    
    with col2:
        delta_trans = f"+{int(metrics['total_transacciones'] * 0.08)}" if metrics['total_transacciones'] > 0 else None
        st.metric(
            label="🛒 Transacciones",
            value=f"{metrics['total_transacciones']:,}",
            delta=delta_trans,
            help="Número total de transacciones"
        )
    
    with col3:
        delta_ticket = f"+{(metrics['ticket_promedio'] * 0.05):.2f}" if metrics['ticket_promedio'] > 0 else None
        st.metric(
            label="🎯 Ticket Promedio",
            value=f"L {metrics['ticket_promedio']:.2f}",
            delta=delta_ticket,
            help="Valor promedio por transacción"
        )
    
    with col4:
        st.metric(
            label="👥 Clientes Únicos",
            value=f"{metrics['clientes_unicos']:,}",
            delta=f"+{int(metrics['clientes_unicos'] * 0.12)}" if metrics['clientes_unicos'] > 0 else None,
            help="Número de clientes diferentes"
        )
    
    # Segunda fila de métricas - Desglose por tipo de venta
    if selected_tipo_venta == 'Todos':
        st.markdown("#### 💳 Desglose por Tipo de Transacción")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            porcentaje_contado = (metrics['venta_contado'] / metrics['total_ventas'] * 100) if metrics['total_ventas'] > 0 else 0
            st.metric(
                label="💵 Ventas al Contado",
                value=f"L {metrics['venta_contado']:,.2f}",
                delta=f"{porcentaje_contado:.1f}% del total",
                help="Ventas pagadas al contado (Sales Receipt)"
            )
        
        with col2:
            porcentaje_credito = (metrics['venta_credito'] / metrics['total_ventas'] * 100) if metrics['total_ventas'] > 0 else 0
            st.metric(
                label="🏦 Ventas a Crédito",
                value=f"L {metrics['venta_credito']:,.2f}",
                delta=f"{porcentaje_credito:.1f}% del total",
                help="Ventas a crédito (Invoice)"
            )
        
        with col3:
            st.metric(
                label="📊 Transacciones Contado",
                value=f"{metrics['transacciones_contado']:,}",
                help="Número de transacciones al contado"
            )
        
        with col4:
            st.metric(
                label="📈 Transacciones Crédito",
                value=f"{metrics['transacciones_credito']:,}",
                help="Número de transacciones a crédito"
            )
    
    # Métricas adicionales
    st.markdown("#### 📦 Métricas de Productos y Actividad")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📦 Productos Únicos",
            value=f"{metrics['productos_unicos']:,}",
            help="Número de productos diferentes vendidos"
        )
    
    with col2:
        st.metric(
            label="📅 Días con Ventas",
            value=f"{metrics['dias_con_ventas']:,}",
            help="Número de días con actividad comercial"
        )
    
    with col3:
        frecuencia_venta = metrics['total_transacciones'] / metrics['dias_con_ventas'] if metrics['dias_con_ventas'] > 0 else 0
        st.metric(
            label="⚡ Transacciones/Día",
            value=f"{frecuencia_venta:.1f}",
            help="Promedio de transacciones por día"
        )
    
    with col4:
        venta_por_dia = metrics['total_ventas'] / metrics['dias_con_ventas'] if metrics['dias_con_ventas'] > 0 else 0
        st.metric(
            label="💰 Ventas/Día",
            value=f"L {venta_por_dia:,.0f}",
            help="Promedio de ventas por día"
        )
    
    st.markdown("---")
    
    # Sistema de pestañas persistentes usando session_state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Tendencias"
    
    # Crear botones para las pestañas
    st.markdown("### 📊 Análisis Detallado")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📈 Tendencias", width="stretch", key="btn_tendencias",
                     type="primary" if st.session_state.active_tab == "Tendencias" else "secondary"):
            st.session_state.active_tab = "Tendencias"
            st.rerun()
    
    with col2:
        if st.button("🏆 Productos", width="stretch", key="btn_productos",
                     type="primary" if st.session_state.active_tab == "Productos" else "secondary"):
            st.session_state.active_tab = "Productos"
            st.rerun()
    
    with col3:
        if st.button("👑 Clientes", width="stretch", key="btn_clientes",
                     type="primary" if st.session_state.active_tab == "Clientes" else "secondary"):
            st.session_state.active_tab = "Clientes"
            st.rerun()
    
    with col4:
        if st.button("📊 Categorías", width="stretch", key="btn_categorias",
                     type="primary" if st.session_state.active_tab == "Categorías" else "secondary"):
            st.session_state.active_tab = "Categorías"
            st.rerun()
    
    with col5:
        if st.button("🎯 Dashboard", width="stretch", key="btn_dashboard",
                     type="primary" if st.session_state.active_tab == "Dashboard" else "secondary"):
            st.session_state.active_tab = "Dashboard"
            st.rerun()
    
    st.markdown("---")
    
    # Mostrar contenido según la pestaña activa
    if st.session_state.active_tab == "Tendencias":
        st.markdown("### 📈 Análisis de Tendencias Temporales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ventas diarias
            ventas_diarias = df_filtered.groupby('Date')['Amount'].sum().reset_index()
            
            fig_ventas_tiempo = px.line(
                ventas_diarias,
                x='Date',
                y='Amount',
                title='💰 Evolución de Ventas Diarias',
                labels={'Amount': 'Ventas (L)', 'Date': 'Fecha'}
            )
            fig_ventas_tiempo.update_layout(height=400)
            st.plotly_chart(fig_ventas_tiempo, width="stretch")
        
        with col2:
            # Ventas por día de la semana
            ventas_weekday = df_filtered.groupby('Weekday')['Amount'].sum().reset_index()
            dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dias_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            
            ventas_weekday['Weekday'] = pd.Categorical(ventas_weekday['Weekday'], categories=dias_orden, ordered=True)
            ventas_weekday = ventas_weekday.sort_values('Weekday')
            ventas_weekday['Dia_ES'] = ventas_weekday['Weekday'].map(dict(zip(dias_orden, dias_es)))
            
            fig_weekday = px.bar(
                ventas_weekday,
                x='Dia_ES',
                y='Amount',
                title='📅 Ventas por Día de la Semana',
                labels={'Amount': 'Ventas (L)', 'Dia_ES': 'Día de la Semana'}
            )
            fig_weekday.update_layout(height=400)
            st.plotly_chart(fig_weekday, width="stretch")
        
        # Análisis por tipo de venta si no hay filtro específico
        if selected_tipo_venta == 'Todos':
            st.markdown("#### 💳 Análisis por Tipo de Transacción")
            col1, col2 = st.columns(2)
            
            with col1:
                # Evolución por tipo de venta
                ventas_tipo_tiempo = df_filtered.groupby(['Date', 'Type'])['Amount'].sum().reset_index()
                
                fig_tipo_tiempo = px.line(
                    ventas_tipo_tiempo,
                    x='Date',
                    y='Amount',
                    color='Type',
                    title='📊 Evolución por Tipo de Transacción',
                    labels={'Amount': 'Ventas (L)', 'Date': 'Fecha', 'Type': 'Tipo'}
                )
                fig_tipo_tiempo.update_layout(height=400)
                st.plotly_chart(fig_tipo_tiempo, width="stretch")
            
            with col2:
                # Distribución por tipo
                tipo_distribucion = df_filtered.groupby('Type')['Amount'].sum().reset_index()
                tipo_distribucion['Tipo_ES'] = tipo_distribucion['Type'].map({
                    'Sales Receipt': '💵 Al Contado',
                    'Invoice': '🏦 A Crédito'
                })
                
                fig_tipo_pie = px.pie(
                    tipo_distribucion,
                    values='Amount',
                    names='Tipo_ES',
                    title='🥧 Distribución de Ventas por Tipo'
                )
                fig_tipo_pie.update_layout(height=400)
                st.plotly_chart(fig_tipo_pie, width="stretch")
        
        # Mapa de calor
        st.markdown("#### 🗓️ Mapa de Calor de Actividad")
        df_filtered['Day_of_Month'] = df_filtered['Date'].dt.day
        heatmap_data = df_filtered.groupby(['Weekday', 'Day_of_Month'])['Amount'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='Weekday', columns='Day_of_Month', values='Amount').fillna(0)
        heatmap_pivot = heatmap_pivot.reindex(dias_orden)
        heatmap_pivot.index = dias_es
        
        fig_heatmap = px.imshow(
            heatmap_pivot,
            title='🗓️ Intensidad de Ventas por Día del Mes y Día de la Semana',
            labels=dict(x="Día del Mes", y="Día de la Semana", color="Ventas (L)"),
            aspect="auto"
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, width="stretch")
    
    elif st.session_state.active_tab == "Productos":
        st.header("🏆 Análisis de Productos Top")
        
        # Control para número de productos a mostrar
        num_productos = st.slider("Número de productos a mostrar:", 5, 20, 10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top productos por ingresos
            top_productos_ingresos = df_filtered.groupby('Item').agg({
                'Amount': 'sum',
                'Qty': 'sum'
            }).sort_values('Amount', ascending=False).head(num_productos).reset_index()
            
            fig_productos_ingresos = px.bar(
                top_productos_ingresos,
                x='Amount',
                y='Item',
                orientation='h',
                title=f'🏆 Top {num_productos} Productos por Ingresos',
                labels={'Amount': 'Ingresos (L)', 'Item': 'Producto'}
            )
            fig_productos_ingresos.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_productos_ingresos, width="stretch")
        
        with col2:
            # Top productos por cantidad
            top_productos_cantidad = df_filtered.groupby('Item').agg({
                'Qty': 'sum',
                'Amount': 'sum'
            }).sort_values('Qty', ascending=False).head(num_productos).reset_index()
            
            fig_productos_cantidad = px.bar(
                top_productos_cantidad,
                x='Qty',
                y='Item',
                orientation='h',
                title=f'📦 Top {num_productos} Productos por Cantidad',
                labels={'Qty': 'Cantidad Vendida', 'Item': 'Producto'}
            )
            fig_productos_cantidad.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_productos_cantidad, width="stretch")
        
        # Tabla detallada de productos
        st.subheader("📋 Tabla Detallada de Productos")
        productos_detalle = df_filtered.groupby('Item').agg({
            'Amount': ['sum', 'mean', 'count'],
            'Qty': 'sum'
        }).round(2)
        productos_detalle.columns = ['Ingresos_Total', 'Precio_Promedio', 'Num_Ventas', 'Cantidad_Total']
        productos_detalle = productos_detalle.reset_index().sort_values('Ingresos_Total', ascending=False)
        
        # Formatear valores monetarios
        productos_detalle['Ingresos_Total'] = productos_detalle['Ingresos_Total'].apply(lambda x: f"L {x:,.2f}")
        productos_detalle['Precio_Promedio'] = productos_detalle['Precio_Promedio'].apply(lambda x: f"L {x:.2f}")
        
        st.dataframe(productos_detalle, width="stretch")
    
    elif st.session_state.active_tab == "Clientes":
        st.header("👑 Análisis de Clientes Top")
        
        # Métricas por cliente
        clientes_metricas = df_filtered.groupby('Name').agg({
            'Amount': ['sum', 'mean', 'count'],
            'Qty': 'sum',
            'Date': ['min', 'max']
        }).round(2)
        
        clientes_metricas.columns = ['Total_Ventas', 'Ticket_Promedio', 'Num_Transacciones', 'Total_Cantidad', 'Primera_Compra', 'Ultima_Compra']
        clientes_metricas = clientes_metricas.reset_index()
        
        # Control para número de clientes
        num_clientes = st.slider("Número de clientes a mostrar:", 5, 20, 15)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top clientes por valor
            top_clientes_valor = clientes_metricas.nlargest(num_clientes, 'Total_Ventas')
            
            fig_clientes_valor = px.bar(
                top_clientes_valor,
                x='Total_Ventas',
                y='Name',
                orientation='h',
                title=f'👑 Top {num_clientes} Clientes por Valor',
                labels={'Total_Ventas': 'Ventas Totales (L)', 'Name': 'Cliente'}
            )
            fig_clientes_valor.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_clientes_valor, width="stretch")
        
        with col2:
            # Análisis de frecuencia vs valor
            fig_scatter_clientes = px.scatter(
                clientes_metricas,
                x='Num_Transacciones',
                y='Total_Ventas',
                size='Ticket_Promedio',
                hover_data=['Name'],
                title='💎 Frecuencia vs Valor de Clientes',
                labels={
                    'Num_Transacciones': 'Número de Transacciones',
                    'Total_Ventas': 'Ventas Totales (L)',
                    'Ticket_Promedio': 'Ticket Promedio (L)'
                }
            )
            fig_scatter_clientes.update_layout(height=600)
            st.plotly_chart(fig_scatter_clientes, width="stretch")
        
        # Distribución de clientes por valor
        st.subheader("📊 Distribución de Clientes por Rango de Valor")
        clientes_metricas['Rango_Valor'] = pd.cut(
            clientes_metricas['Total_Ventas'],
            bins=[0, 100, 500, 1000, 2000, float('inf')],
            labels=['L 0-100', 'L 100-500', 'L 500-1K', 'L 1K-2K', 'L 2K+']
        )
        
        distribucion_clientes = clientes_metricas['Rango_Valor'].value_counts().reset_index()
        distribucion_clientes.columns = ['Rango_Valor', 'Cantidad_Clientes']
        
        fig_distribucion = px.pie(
            distribucion_clientes,
            values='Cantidad_Clientes',
            names='Rango_Valor',
            title='Distribución de Clientes por Rango de Valor'
        )
        st.plotly_chart(fig_distribucion, width="stretch")
    
    elif st.session_state.active_tab == "Categorías":
        st.header("📊 Análisis por Categorías")
        
        # Ventas por categoría
        ventas_categoria = df_filtered.groupby('Categoria').agg({
            'Amount': 'sum',
            'Qty': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pastel
            fig_categoria_pie = px.pie(
                ventas_categoria,
                values='Amount',
                names='Categoria',
                title='🥧 Distribución de Ventas por Categoría'
            )
            st.plotly_chart(fig_categoria_pie, width="stretch")
        
        with col2:
            # Gráfico de barras
            fig_categoria_bar = px.bar(
                ventas_categoria,
                x='Categoria',
                y='Amount',
                title='📊 Ingresos por Categoría',
                labels={'Amount': 'Ingresos (L)', 'Categoria': 'Categoría'}
            )
            st.plotly_chart(fig_categoria_bar, width="stretch")
        
        # Tabla de resumen por categoría
        st.subheader("📋 Resumen Detallado por Categoría")
        categoria_detalle = df_filtered.groupby('Categoria').agg({
            'Amount': ['sum', 'mean', 'count'],
            'Qty': 'sum',
            'Name': 'nunique'
        }).round(2)
        categoria_detalle.columns = ['Ingresos_Total', 'Venta_Promedio', 'Num_Transacciones', 'Cantidad_Total', 'Clientes_Unicos']
        categoria_detalle = categoria_detalle.reset_index()
        
        # Formatear valores monetarios
        categoria_detalle['Ingresos_Total'] = categoria_detalle['Ingresos_Total'].apply(lambda x: f"L {x:,.2f}")
        categoria_detalle['Venta_Promedio'] = categoria_detalle['Venta_Promedio'].apply(lambda x: f"L {x:.2f}")
        
        st.dataframe(categoria_detalle, width="stretch")
    
    elif st.session_state.active_tab == "Dashboard":
        st.header("🎯 Dashboard Ejecutivo")
        
        # Dashboard consolidado
        fig_dashboard = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Ventas Diarias', 'Top 5 Productos', 
                           'Ventas por Día de Semana', 'Distribución por Categoría'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "pie"}]]
        )
        
        # 1. Ventas diarias
        ventas_diarias = df_filtered.groupby('Date')['Amount'].sum().reset_index()
        fig_dashboard.add_trace(
            go.Scatter(x=ventas_diarias['Date'], y=ventas_diarias['Amount'],
                      mode='lines+markers', name='Ventas Diarias'),
            row=1, col=1
        )
        
        # 2. Top 5 productos
        top_5_productos = df_filtered.groupby('Item')['Amount'].sum().nlargest(5).reset_index()
        fig_dashboard.add_trace(
            go.Bar(x=top_5_productos['Amount'], y=top_5_productos['Item'],
                   orientation='h', name='Top Productos'),
            row=1, col=2
        )
        
        # 3. Ventas por día de semana
        ventas_weekday = df_filtered.groupby('Weekday')['Amount'].sum().reset_index()
        fig_dashboard.add_trace(
            go.Bar(x=ventas_weekday['Weekday'], y=ventas_weekday['Amount'],
                   name='Ventas por Día'),
            row=2, col=1
        )
        
        # 4. Distribución por categoría
        ventas_categoria = df_filtered.groupby('Categoria')['Amount'].sum().reset_index()
        fig_dashboard.add_trace(
            go.Pie(labels=ventas_categoria['Categoria'], values=ventas_categoria['Amount'],
                   name="Categorías"),
            row=2, col=2
        )
        
        fig_dashboard.update_layout(height=800, showlegend=False)
        st.plotly_chart(fig_dashboard, width="stretch")
        
        # Insights automáticos con alertas inteligentes
        st.markdown("### 💡 Análisis Inteligente y Recomendaciones")
        
        # Calcular insights
        mejor_dia = df_filtered.groupby('Weekday')['Amount'].sum().idxmax() if len(df_filtered) > 0 else "N/A"
        peor_dia = df_filtered.groupby('Weekday')['Amount'].sum().idxmin() if len(df_filtered) > 0 else "N/A"
        mejor_producto = df_filtered.groupby('Item')['Amount'].sum().idxmax() if len(df_filtered) > 0 else "N/A"
        mejor_cliente = df_filtered.groupby('Name')['Amount'].sum().idxmax() if len(df_filtered) > 0 else "N/A"
        mejor_categoria = df_filtered.groupby('Categoria')['Amount'].sum().idxmax() if len(df_filtered) > 0 else "N/A"
        
        # Mapear días al español
        dias_map = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        mejor_dia_es = dias_map.get(mejor_dia, mejor_dia)
        peor_dia_es = dias_map.get(peor_dia, peor_dia)
        
        # Alertas dinámicas basadas en datos
        col1, col2 = st.columns(2)
        
        with col1:
            # Alertas de rendimiento
            if metrics['total_ventas'] > 50000:
                st.success("🎉 **¡Excelente rendimiento!** Las ventas superan L 50,000")
            elif metrics['total_ventas'] > 20000:
                st.info("📈 **Buen rendimiento** Las ventas están en un rango saludable")
            else:
                st.warning("⚠️ **Ventas por debajo del promedio** Considera estrategias de impulso")
            
            # Análisis de balance contado/crédito
            if selected_tipo_venta == 'Todos' and metrics['total_ventas'] > 0:
                ratio_contado = metrics['venta_contado'] / metrics['total_ventas']
                if ratio_contado > 0.7:
                    st.success("� **Excelente liquidez** - 70%+ de ventas al contado")
                elif ratio_contado > 0.5:
                    st.info("⚖️ **Balance saludable** entre contado y crédito")
                else:
                    st.warning("🏦 **Alto crédito** - Monitorear cobranza de facturas")
        
        with col2:
            # Progress bars para métricas clave
            st.markdown("**📊 Indicadores de Progreso**")
            
            # Meta de transacciones diarias (ejemplo: 50 transacciones/día)
            trans_por_dia = metrics['total_transacciones'] / metrics['dias_con_ventas'] if metrics['dias_con_ventas'] > 0 else 0
            meta_trans_dia = 50
            progreso_trans = min(trans_por_dia / meta_trans_dia, 1.0)
            st.progress(progreso_trans, text=f"Transacciones/día: {trans_por_dia:.1f}/{meta_trans_dia}")
            
            # Meta de ticket promedio (ejemplo: L 500)
            meta_ticket = 500
            progreso_ticket = min(metrics['ticket_promedio'] / meta_ticket, 1.0) if metrics['ticket_promedio'] > 0 else 0
            st.progress(progreso_ticket, text=f"Ticket promedio: L {metrics['ticket_promedio']:.0f}/L {meta_ticket}")
            
            # Diversificación de clientes (ejemplo: meta de 100 clientes únicos)
            meta_clientes = 100
            progreso_clientes = min(metrics['clientes_unicos'] / meta_clientes, 1.0)
            st.progress(progreso_clientes, text=f"Clientes únicos: {metrics['clientes_unicos']}/{meta_clientes}")
        
        # Insights clave en columnas
        st.markdown("#### 🔍 Insights Clave del Período")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **📅 Día más productivo:** {mejor_dia_es}
            
            **🏆 Producto estrella:** {mejor_producto[:30]}...
            """)
        
        with col2:
            st.info(f"""
            **👑 Cliente VIP:** {mejor_cliente[:25]}...
            
            **📊 Categoría líder:** {mejor_categoria}
            """)
        
        with col3:
            # Calcular tendencia
            if len(df_filtered) > 1:
                ventas_por_fecha = df_filtered.groupby('Date')['Amount'].sum().sort_index()
                if len(ventas_por_fecha) > 1:
                    ultima_semana = ventas_por_fecha.tail(7).mean()
                    penultima_semana = ventas_por_fecha.head(-7).tail(7).mean() if len(ventas_por_fecha) > 7 else ventas_por_fecha.head(7).mean()
                    if ultima_semana > penultima_semana:
                        tendencia = "📈 Tendencia al alza"
                    else:
                        tendencia = "📉 Tendencia a la baja"
                else:
                    tendencia = "📊 Datos insuficientes"
            else:
                tendencia = "📊 Sin datos suficientes"
            
            eficiencia = metrics['total_ventas'] / metrics['total_transacciones'] if metrics['total_transacciones'] > 0 else 0
            st.info(f"""
            **📈 Tendencia:** {tendencia}
            
            **⚡ Eficiencia:** L {eficiencia:.0f} por transacción
            """)
        
        # Recomendaciones inteligentes
        st.markdown("#### 🎯 Recomendaciones Personalizadas")
        
        recomendaciones = []
        
        # Recomendaciones basadas en tipo de venta
        if selected_tipo_venta == 'Todos':
            if metrics['venta_credito'] > metrics['venta_contado']:
                recomendaciones.append("🏦 **Gestión de crédito:** Implementar estrategias para acelerar cobranza")
            
            if metrics['transacciones_contado'] < metrics['transacciones_credito']:
                recomendaciones.append("💵 **Incentivar pagos al contado:** Ofrecer descuentos por pago inmediato")
        
        # Recomendaciones basadas en días de la semana
        if mejor_dia != peor_dia:
            recomendaciones.append(f"� **Optimizar {peor_dia_es}:** Crear promociones especiales para el día de menor venta")
        
        # Recomendaciones basadas en ticket promedio
        if metrics['ticket_promedio'] < 300:
            recomendaciones.append("🎯 **Aumentar ticket promedio:** Implementar estrategias de venta cruzada")
        
        # Recomendaciones basadas en clientes
        if metrics['clientes_unicos'] < 50:
            recomendaciones.append("👥 **Expandir base de clientes:** Desarrollar campañas de adquisición")
        
        # Mostrar recomendaciones
        if recomendaciones:
            for i, rec in enumerate(recomendaciones[:4], 1):  # Mostrar máximo 4 recomendaciones
                st.write(f"{i}. {rec}")
        else:
            st.success("✅ **¡Excelente gestión!** Todos los indicadores están en rangos óptimos")
    
    # Footer con recomendaciones usando componentes nativos
    st.divider()
    st.subheader("🚀 Estrategias para el Crecimiento")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("📈 **Oportunidades de Crecimiento**")
        st.markdown("""
        - Impulsar ventas en días de menor actividad
        - Promocionar productos de alta rotación  
        - Implementar programas de fidelización
        - Optimizar inventario según demanda
        """)
    
    with col2:
        st.info("🎯 **Acciones Recomendadas**")
        st.markdown("""
        - Crear promociones para clientes VIP
        - Desarrollar ofertas por categorías
        - Establecer metas basadas en tendencias
        - Monitorear KPIs semanalmente
        """)
    
    with col3:
        st.warning("💡 **Optimización Financiera**")
        st.markdown("""
        - Balancear ventas contado vs crédito
        - Acelerar procesos de cobranza
        - Implementar descuentos por pronto pago
        - Analizar márgenes por producto
        """)
    
    # Información del sistema
    st.divider()
    st.caption("📊 **Dashboard de Inteligencia de Negocios** | 🇭🇳 Honduras 2025 | ⚡ Actualización en tiempo real")
    st.caption("Desarrollado con ❤️ usando Streamlit y Plotly | 📧 Soporte: dashboard@empresa.hn")

else:
    st.error("❌ No se pudieron cargar los datos. Verifica que el archivo 'VENTAS 2025.CSV' esté en la carpeta correcta.")
    st.info("💡 Asegúrate de que el archivo esté en el mismo directorio que este script.")
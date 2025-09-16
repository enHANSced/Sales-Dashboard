import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Configuración de la página
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
def calculate_metrics(df, start_date, end_date, selected_clients, selected_categories):
    """Calcular métricas filtradas"""
    # Convertir fechas a datetime para comparación
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filtrar datos
    df_filtered = df[
        (df['Date'] >= start_date) & 
        (df['Date'] <= end_date)
    ]
    
    if selected_clients:
        df_filtered = df_filtered[df_filtered['Name'].isin(selected_clients)]
    
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Categoria'].isin(selected_categories)]
    
    # Calcular métricas
    metrics = {
        'total_ventas': df_filtered['Amount'].sum(),
        'total_transacciones': len(df_filtered),
        'ticket_promedio': df_filtered['Amount'].mean(),
        'clientes_unicos': df_filtered['Name'].nunique(),
        'productos_unicos': df_filtered['Item'].nunique(),
        'dias_con_ventas': df_filtered['Date'].nunique()
    }
    
    return df_filtered, metrics

# Cargar datos
df = load_data()

if df is not None:
    # Sidebar para filtros
    st.sidebar.header("🔧 Filtros de Análisis")
    
    # Filtro de fechas
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "📅 Seleccionar período:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]
    
    # Filtro de clientes
    all_clients = sorted(df['Name'].unique())
    selected_clients = st.sidebar.multiselect(
        "👥 Seleccionar clientes:",
        options=all_clients,
        default=[],
        help="Dejar vacío para incluir todos los clientes"
    )
    
    # Filtro de categorías
    all_categories = sorted(df['Categoria'].unique())
    selected_categories = st.sidebar.multiselect(
        "🏷️ Seleccionar categorías:",
        options=all_categories,
        default=[],
        help="Dejar vacío para incluir todas las categorías"
    )
    
    # Calcular datos filtrados
    df_filtered, metrics = calculate_metrics(df, start_date, end_date, selected_clients, selected_categories)
    
    # Header principal
    st.title("🇭🇳 Dashboard de Inteligencia de Negocios")
    st.subheader("📊 Análisis de Ventas - Honduras 2025")
    
    # Mostrar período seleccionado
    st.info(f"📅 Análisis del período: {start_date} al {end_date}")
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="💰 Ventas Totales",
            value=f"L {metrics['total_ventas']:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="🛒 Transacciones",
            value=f"{metrics['total_transacciones']:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="🎯 Ticket Promedio",
            value=f"L {metrics['ticket_promedio']:.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="👥 Clientes Únicos",
            value=f"{metrics['clientes_unicos']:,}",
            delta=None
        )
    
    with col5:
        st.metric(
            label="📦 Productos Únicos",
            value=f"{metrics['productos_unicos']:,}",
            delta=None
        )
    
    # Pestañas para diferentes análisis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Tendencias", "🏆 Top Productos", "👑 Top Clientes", 
        "📊 Categorías", "🎯 Dashboard Ejecutivo"
    ])
    
    with tab1:
        st.header("📈 Análisis de Tendencias")
        
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
            st.plotly_chart(fig_ventas_tiempo, use_container_width=True)
        
        with col2:
            # Ventas por día de la semana
            ventas_weekday = df_filtered.groupby('Weekday')['Amount'].sum().reset_index()
            dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            ventas_weekday['Weekday'] = pd.Categorical(ventas_weekday['Weekday'], categories=dias_orden, ordered=True)
            ventas_weekday = ventas_weekday.sort_values('Weekday')
            
            fig_weekday = px.bar(
                ventas_weekday,
                x='Weekday',
                y='Amount',
                title='📅 Ventas por Día de la Semana',
                labels={'Amount': 'Ventas (L)', 'Weekday': 'Día de la Semana'}
            )
            fig_weekday.update_layout(height=400)
            st.plotly_chart(fig_weekday, use_container_width=True)
        
        # Mapa de calor
        st.subheader("🗓️ Mapa de Calor de Ventas")
        df_filtered['Day_of_Month'] = df_filtered['Date'].dt.day
        heatmap_data = df_filtered.groupby(['Weekday', 'Day_of_Month'])['Amount'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='Weekday', columns='Day_of_Month', values='Amount').fillna(0)
        heatmap_pivot = heatmap_pivot.reindex(dias_orden)
        
        fig_heatmap = px.imshow(
            heatmap_pivot,
            title='Intensidad de Ventas por Día del Mes y Día de la Semana',
            labels=dict(x="Día del Mes", y="Día de la Semana", color="Ventas (L)"),
            aspect="auto"
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab2:
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
            st.plotly_chart(fig_productos_ingresos, use_container_width=True)
        
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
            st.plotly_chart(fig_productos_cantidad, use_container_width=True)
        
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
        
        st.dataframe(productos_detalle, use_container_width=True)
    
    with tab3:
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
            st.plotly_chart(fig_clientes_valor, use_container_width=True)
        
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
            st.plotly_chart(fig_scatter_clientes, use_container_width=True)
        
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
        st.plotly_chart(fig_distribucion, use_container_width=True)
    
    with tab4:
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
            st.plotly_chart(fig_categoria_pie, use_container_width=True)
        
        with col2:
            # Gráfico de barras
            fig_categoria_bar = px.bar(
                ventas_categoria,
                x='Categoria',
                y='Amount',
                title='📊 Ingresos por Categoría',
                labels={'Amount': 'Ingresos (L)', 'Categoria': 'Categoría'}
            )
            st.plotly_chart(fig_categoria_bar, use_container_width=True)
        
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
        
        st.dataframe(categoria_detalle, use_container_width=True)
    
    with tab5:
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
        st.plotly_chart(fig_dashboard, use_container_width=True)
        
        # Insights automáticos
        st.subheader("💡 Insights Clave")
        
        # Calcular insights
        mejor_dia = df_filtered.groupby('Weekday')['Amount'].sum().idxmax()
        peor_dia = df_filtered.groupby('Weekday')['Amount'].sum().idxmin()
        mejor_producto = df_filtered.groupby('Item')['Amount'].sum().idxmax()
        mejor_cliente = df_filtered.groupby('Name')['Amount'].sum().idxmax()
        mejor_categoria = df_filtered.groupby('Categoria')['Amount'].sum().idxmax()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"📅 **Mejor día de ventas:** {mejor_dia}")
            st.info(f"🏆 **Producto top:** {mejor_producto}")
        
        with col2:
            st.info(f"👑 **Cliente top:** {mejor_cliente}")
            st.info(f"📊 **Categoría líder:** {mejor_categoria}")
        
        with col3:
            crecimiento_ventas = ((metrics['total_ventas'] / len(df_filtered)) * 100) if len(df_filtered) > 0 else 0
            st.info(f"💰 **Venta promedio:** L {metrics['ticket_promedio']:.2f}")
            st.info(f"🎯 **Días con ventas:** {metrics['dias_con_ventas']}")
    
    # Footer con recomendaciones
    st.markdown("---")
    st.subheader("🚀 Recomendaciones Estratégicas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📈 Oportunidades de Crecimiento:**
        - Impulsar ventas en días de menor actividad
        - Promocionar productos de alta rotación
        - Implementar programas de fidelización
        - Optimizar inventario según demanda
        """)
    
    with col2:
        st.markdown("""
        **🎯 Acciones Recomendadas:**
        - Crear promociones para clientes VIP
        - Desarrollar ofertas por categorías
        - Establecer metas basadas en tendencias
        - Monitorear KPIs semanalmente
        """)

else:
    st.error("❌ No se pudieron cargar los datos. Verifica que el archivo 'VENTAS 2025.CSV' esté en la carpeta correcta.")
    st.info("💡 Asegúrate de que el archivo esté en el mismo directorio que este script.")
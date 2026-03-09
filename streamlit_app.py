"""
Olist Logistics Intelligence - Streamlit Dashboard
Replica fiel do frontend original em FastAPI + Vanilla JS
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# -- Config
st.set_page_config(
    page_title="Olist Logistics Intelligence",
    page_icon="\U0001F4E6",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -- Paleta do site original
COLORS = {
    "bg": "#0D0D0D", "card": "#141414", "border": "#1a1a2e",
    "blue": "#0000FF", "cyan": "#00F0FF", "red": "#FF0000",
    "lime": "#00FF00", "white": "#E0E0E0", "muted": "#888888",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color=COLORS["white"], size=11),
    margin=dict(l=40, r=20, t=40, b=40),
)
PLOTLY_CFG = dict(displayModeBar=False)

REGIOES_MAP = {
    'AM':'Norte','RR':'Norte','AP':'Norte','PA':'Norte','TO':'Norte','RO':'Norte','AC':'Norte',
    'MA':'Nordeste','PI':'Nordeste','CE':'Nordeste','RN':'Nordeste','PE':'Nordeste',
    'PB':'Nordeste','SE':'Nordeste','AL':'Nordeste','BA':'Nordeste',
    'MT':'Centro-Oeste','MS':'Centro-Oeste','GO':'Centro-Oeste','DF':'Centro-Oeste',
    'SP':'Sudeste','RJ':'Sudeste','ES':'Sudeste','MG':'Sudeste',
    'PR':'Sul','RS':'Sul','SC':'Sul',
}

# -- CSS inspirado no original
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
.stApp {
    background-color: #0D0D0D;
    color: #E0E0E0;
    font-family: 'IBM Plex Mono', monospace;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 0px; background: #141414; border: 1px solid #1a1a2e;
    border-radius: 8px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #888; border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace; font-size: 13px;
    font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; padding: 8px 24px;
}
.stTabs [aria-selected="true"] {
    background: #0000FF !important; color: #E0E0E0 !important;
}
.kpi-card {
    background: #141414; border: 1px solid #1a1a2e; border-radius: 12px;
    padding: 20px; text-align: center;
    min-height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center;
}
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.kpi-value { font-size: 28px; font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: #00F0FF; }
.kpi-sub { font-size: 11px; color: #888; margin-top: 4px; min-height: 16px; }
.chart-card { background: #141414; border: 1px solid #1a1a2e; border-radius: 12px; padding: 16px; }
.chart-title { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; font-weight: 600; }
.section-num { font-family: 'Space Grotesk', sans-serif; font-size: 48px; font-weight: 700; color: #1a1a2e; line-height: 1; }
.section-title { font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 600; color: #E0E0E0; }
.section-desc { font-size: 12px; color: #888; max-width: 500px; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 42px; font-weight: 700; color: #E0E0E0; line-height: 1.1; }
.hero-sub { font-size: 13px; color: #888; max-width: 600px; }
/* Dropdown - forcar tema escuro */
div[data-baseweb="select"] { background: #141414 !important; }
div[data-baseweb="select"] > div { background: #141414 !important; color: #E0E0E0 !important; border-color: #1a1a2e !important; }
div[data-baseweb="select"] * { color: #E0E0E0 !important; }
div[data-baseweb="popover"] { background: #141414 !important; }
div[data-baseweb="popover"] * { background: #141414 !important; color: #E0E0E0 !important; }
ul[data-baseweb="menu"] { background: #141414 !important; }
ul[data-baseweb="menu"] li { background: #141414 !important; color: #E0E0E0 !important; }
ul[data-baseweb="menu"] li:hover { background: #1a1a2e !important; }
[data-baseweb="select"] svg { fill: #E0E0E0 !important; }
/* Label do selectbox */
.stSelectbox label { color: #888 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetric"] { background: #141414; border: 1px solid #1a1a2e; border-radius: 12px; padding: 16px; }
[data-testid="stMetricLabel"] { color: #888 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #00F0FF !important; font-family: 'Space Grotesk', sans-serif !important; }
hr { border-color: #1a1a2e !important; }
.stSlider > div > div > div { background: #0000FF !important; }
</style>
""", unsafe_allow_html=True)

# -- Data Loading (cached)
@st.cache_data(ttl=3600, show_spinner="Carregando dados Olist...")
def load_data():
    base = Path(__file__).parent / "src" / "dataset"
    if not base.exists():
        base = Path(__file__).parent / "src" / "backend" / "dataset"

    df_orders = pd.read_csv(base / "olist_orders_dataset.csv")
    df_items = pd.read_csv(base / "olist_order_items_dataset.csv")
    df_customers = pd.read_csv(base / "olist_customers_dataset.csv")
    df_products = pd.read_csv(base / "olist_products_dataset.csv")
    df_sellers = pd.read_csv(base / "olist_sellers_dataset.csv")

    df_orders = df_orders[df_orders['order_status'] == 'delivered'].copy()
    df_orders = df_orders.dropna(subset=['order_delivered_customer_date'])

    df_products['product_category_name'] = df_products['product_category_name'].fillna('desconhecido')
    for col in ['product_weight_g','product_length_cm','product_height_cm','product_width_cm']:
        if col in df_products.columns:
            df_products[col] = df_products[col].fillna(df_products[col].median())

    df = df_orders.merge(df_items, on="order_id", how="left")
    df = df.merge(df_customers, on="customer_id", how="left")
    df = df.merge(df_products, on="product_id", how="left")
    df = df.merge(df_sellers, on="seller_id", how="left")

    pay_file = base / "olist_order_payments_dataset.csv"
    if pay_file.exists():
        df_pay = pd.read_csv(pay_file)
        pay_agg = df_pay.sort_values(['order_id','payment_value'], ascending=[True,False])
        pay_agg = pay_agg.drop_duplicates(subset=['order_id'], keep='first')[['order_id','payment_type']]
        df = df.merge(pay_agg.rename(columns={'payment_type':'tipo_pagamento_principal'}), on='order_id', how='left')
        df['tipo_pagamento_principal'] = df['tipo_pagamento_principal'].fillna('desconhecido')

    for c in ['order_purchase_timestamp','order_approved_at','order_delivered_carrier_date',
              'order_delivered_customer_date','order_estimated_delivery_date']:
        df[c] = pd.to_datetime(df[c], errors='coerce')

    df['purchase_year'] = df['order_purchase_timestamp'].dt.year
    delivered = df['order_delivered_customer_date']
    estimated = df['order_estimated_delivery_date']
    df['delivery_delayed'] = (delivered > estimated).astype(int)
    df['delta_days'] = (delivered - estimated).dt.days

    df['velocidade_lojista_dias'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.days
    med_vel = df['velocidade_lojista_dias'].median()
    df['velocidade_lojista_dias'] = df['velocidade_lojista_dias'].fillna(med_vel if pd.notna(med_vel) else 1.0)

    df['customer_regiao'] = df['customer_state'].map(REGIOES_MAP)
    df['seller_regiao'] = df['seller_state'].map(REGIOES_MAP)
    df['frete_ratio'] = (df['freight_value'] / df['price']).replace([np.inf, -np.inf], np.nan).fillna(0)
    df['dia_semana_compra'] = df['order_purchase_timestamp'].dt.dayofweek
    df['rota_interestadual'] = (df['seller_state'] != df['customer_state']).astype(int)
    df['total_itens_pedido'] = df.groupby('order_id')['order_item_id'].transform('max').fillna(1).astype(int)
    df['mes_compra'] = df['order_purchase_timestamp'].dt.month
    df['valor_total_pedido'] = df['price'] + df['freight_value']

    if all(c in df.columns for c in ['product_length_cm','product_height_cm','product_width_cm']):
        df['volume_cm3'] = df['product_length_cm'] * df['product_height_cm'] * df['product_width_cm']

    df = df.dropna(subset=['delivery_delayed','customer_state'])
    return df

df_full = load_data()

# -- Helper: compute stats (same logic as /api/stats)
def compute_stats(df_src, state=None, year=None):
    df = df_src.copy()
    if state and state != "Todos":
        df = df[df['customer_state'] == state]
    if year and year != "Todos":
        df = df[df['purchase_year'] == int(year)]

    total = len(df)
    if total == 0:
        return dict(total_orders=0, delayed_orders=0, delay_rate=0, global_delay_rate=0,
                     avg_freight=0, delta_days=0, map_data={}, ranking_data=[], timeline_data={"x":[],"y":[]}, scatter_data={})

    delayed = int(df['delivery_delayed'].sum())
    avg_freight = float(df['freight_value'].mean())
    delay_rate = round(delayed / total * 100, 1)
    avg_delta = float(df['delta_days'].mean()) if 'delta_days' in df.columns else 0.0

    df_global = df_src.copy()
    if year and year != "Todos":
        df_global = df_global[df_global['purchase_year'] == int(year)]
    global_rate = round(df_global['delivery_delayed'].sum() / len(df_global) * 100, 1) if len(df_global) > 0 else 0

    map_df = df.groupby('customer_state')['delivery_delayed'].mean() * 100
    map_data = map_df.to_dict()

    rank_df = df.groupby('customer_state')['delivery_delayed'].mean().sort_values(ascending=False).head(10) * 100
    ranking = [{"state": s, "rate": round(r, 1)} for s, r in rank_df.items()]

    df_t = df.copy()
    df_t['month_year'] = df_t['order_purchase_timestamp'].dt.to_period('M').astype(str)
    tl = df_t.groupby('month_year')['delivery_delayed'].mean().sort_index() * 100
    timeline = {"x": tl.index.tolist(), "y": [round(v, 1) for v in tl.values]}

    sc_cols = ['price','freight_value','delivery_delayed']
    df_sc = df.dropna(subset=sc_cols)
    df_sc = df_sc[(df_sc['price'] > 0) & (df_sc['price'] < 3000) & (df_sc['freight_value'] > 0) & (df_sc['freight_value'] < 300)]
    if len(df_sc) > 1500:
        df_sc = df_sc.sample(1500, random_state=42)
    on_t = df_sc[df_sc['delivery_delayed'] == 0]
    dela = df_sc[df_sc['delivery_delayed'] == 1]
    scatter = {
        "on_time_x": on_t['price'].round(2).tolist(), "on_time_y": on_t['freight_value'].round(2).tolist(),
        "delayed_x": dela['price'].round(2).tolist(), "delayed_y": dela['freight_value'].round(2).tolist(),
    }

    return dict(total_orders=total, delayed_orders=delayed, delay_rate=delay_rate,
                global_delay_rate=global_rate, avg_freight=round(avg_freight, 2),
                delta_days=round(avg_delta, 1), map_data=map_data, ranking_data=ranking,
                timeline_data=timeline, scatter_data=scatter)


# -- Helper: compute insights (same logic as /api/insights)
def compute_insights(df_src):
    df = df_src.copy()

    # 1. Donut
    dv = df.dropna(subset=['seller_state','customer_state','delivery_delayed']).copy()
    dv['is_interstate'] = dv['seller_state'] != dv['customer_state']
    inter_t = dv['is_interstate'].sum(); intra_t = (~dv['is_interstate']).sum()
    inter_d = dv[dv['is_interstate']]['delivery_delayed'].sum()
    intra_d = dv[~dv['is_interstate']]['delivery_delayed'].sum()
    donut = {
        "inter_rate": round(inter_d/inter_t*100, 1) if inter_t > 0 else 0,
        "intra_rate": round(intra_d/intra_t*100, 1) if intra_t > 0 else 0,
        "inter_delayed": int(inter_d), "inter_ontime": int(inter_t - inter_d),
        "intra_delayed": int(intra_d), "intra_ontime": int(intra_t - intra_d),
    }

    # 2. Treemap
    if 'product_category_name' in df.columns:
        cat = df.groupby('product_category_name').agg(total=('order_id','count'), delayed=('delivery_delayed','sum')).reset_index()
        cat = cat[cat['total'] >= 100]
        cat['delay_rate'] = cat['delayed'] / cat['total'] * 100
        cat = cat.sort_values('delay_rate', ascending=False).head(12)
        treemap = {"categories": cat['product_category_name'].tolist(),
                   "totals": cat['total'].astype(int).tolist(),
                   "delay_rates": [round(x,1) for x in cat['delay_rate'].tolist()]}
    else:
        treemap = {"categories":[], "totals":[], "delay_rates":[]}

    # 3. Violin
    if 'velocidade_lojista_dias' in df.columns:
        dv2 = df[['velocidade_lojista_dias','delivery_delayed']].dropna()
        on = dv2[dv2['delivery_delayed']==0]['velocidade_lojista_dias']
        dl = dv2[dv2['delivery_delayed']==1]['velocidade_lojista_dias']
        on = on[on <= 30]; dl = dl[dl <= 30]
        violin = {
            "on_time": on.sample(min(1000,len(on)), random_state=42).tolist() if len(on)>0 else [],
            "delayed": dl.sample(min(1000,len(dl)), random_state=42).tolist() if len(dl)>0 else [],
        }
    else:
        violin = {"on_time":[], "delayed":[]}

    # 4. Freight scatter
    if 'price' in df.columns and 'freight_value' in df.columns:
        ds = df[['price','freight_value','delivery_delayed']].dropna().copy()
        ds = ds[(ds['price']<3000)&(ds['freight_value']<300)]
        ds['freight_ratio'] = (ds['freight_value']/ds['price']).replace([np.inf,-np.inf],0)
        ds = ds[ds['freight_ratio']<=2.0]
        ds = ds.sample(min(1500,len(ds)), random_state=42)
        scatter = {
            "on_time_x": ds[ds['delivery_delayed']==0]['price'].tolist(),
            "on_time_y": ds[ds['delivery_delayed']==0]['freight_ratio'].round(2).tolist(),
            "delayed_x": ds[ds['delivery_delayed']==1]['price'].tolist(),
            "delayed_y": ds[ds['delivery_delayed']==1]['freight_ratio'].round(2).tolist(),
        }
    else:
        scatter = {"on_time_x":[],"on_time_y":[],"delayed_x":[],"delayed_y":[]}

    # 5. Heatmap
    heatmap = {"x":[], "y":[], "z":[]}
    if 'seller_regiao' in df.columns and 'customer_regiao' in df.columns:
        regioes = ['Norte','Nordeste','Centro-Oeste','Sudeste','Sul']
        heatmap['x'] = regioes; heatmap['y'] = regioes
        z = []
        counts = []
        for orig in regioes:
            row = []
            cnt_row = []
            for dest in regioes:
                mask = (df['seller_regiao']==orig) & (df['customer_regiao']==dest)
                sub = df[mask]
                cnt_row.append(len(sub))
                if len(sub) >= 10:
                    row.append(round(sub['delivery_delayed'].mean()*100, 1))
                else:
                    row.append(None)
            z.append(row)
            counts.append(cnt_row)
        heatmap['z'] = z
        heatmap['counts'] = counts

    return dict(donut=donut, treemap=treemap, violin=violin, scatter=scatter, heatmap=heatmap)

# ================================================
#  LAYOUT PRINCIPAL
# ================================================

# -- Hero
st.markdown("""
<div style="margin-bottom: 32px;">
    <div class="hero-title">Logistics Overview</div>
    <div class="hero-sub" style="margin-top:8px;">
        Monitoramento de atrasos logísticos do ecosistema Olist &mdash;
        <span style="color:#00F0FF;">{:,}</span> pedidos entregues analisados
    </div>
</div>
""".format(len(df_full)), unsafe_allow_html=True)

# -- Tabs
tab_dash, tab_insights, tab_predictor = st.tabs(["DASHBOARD", "INSIGHTS", "PREDITOR"])

# ================================================================
#  TAB 1: DASHBOARD
# ================================================================
with tab_dash:
    fc1, fc2, _ = st.columns([2, 2, 6])
    states_list = ['Todos'] + sorted(df_full['customer_state'].dropna().unique().tolist())
    years_list = ['Todos'] + sorted([str(int(y)) for y in df_full['purchase_year'].dropna().unique().tolist()])
    with fc1:
        sel_state = st.selectbox('Estado', states_list, key='dash_state')
    with fc2:
        sel_year = st.selectbox('Periodo', years_list, key='dash_year')

    stats = compute_stats(df_full, sel_state, sel_year)

    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total de Pedidos</div><div class="kpi-value">{stats["total_orders"]:,}</div><div class="kpi-sub">&nbsp;</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Pedidos Atrasados</div><div class="kpi-value" style="color:#FF0000">{stats["delayed_orders"]:,}</div><div class="kpi-sub">{stats["delay_rate"]}% do total</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Frete Medio</div><div class="kpi-value">R$ {stats["avg_freight"]:.2f}</div><div class="kpi-sub">&nbsp;</div></div>', unsafe_allow_html=True)
    with k4:
        dc = '#FF0000' if stats['delta_days'] > 0 else '#00FF00'
        ds = '+' if stats['delta_days'] > 0 else ''
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Delta Dias</div><div class="kpi-value" style="color:{dc}">{ds}{stats["delta_days"]:.1f}d</div><div class="kpi-sub">media entrega vs estimado</div></div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # Gauges
    g1, g2 = st.columns(2)
    with g1:
        fig_g1 = go.Figure(go.Indicator(
            mode='gauge+number+delta', value=stats['delay_rate'],
            delta={'reference': stats['global_delay_rate'], 'valueformat': '.1f'},
            number={'suffix': '%', 'font': {'color': COLORS['white']}},
            title={'text': 'Taxa de Atraso', 'font': {'color': COLORS['white']}},
            gauge={
                'axis': {'range': [0, 50], 'tickcolor': COLORS['muted']},
                'bar': {'color': COLORS['red']},
                'bgcolor': COLORS['card'], 'bordercolor': COLORS['border'],
                'steps': [
                    {'range': [0, 10], 'color': 'rgba(0,255,0,0.1)'},
                    {'range': [10, 25], 'color': 'rgba(255,255,0,0.1)'},
                    {'range': [25, 50], 'color': 'rgba(255,0,0,0.1)'},
                ],
            },
        ))
        fig_g1.update_layout(**PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig_g1, use_container_width=True, config=PLOTLY_CFG)

    with g2:
        fig_g2 = go.Figure(go.Indicator(
            mode='gauge+number', value=stats['avg_freight'],
            number={'prefix': 'R$ ', 'font': {'color': COLORS['white']}},
            title={'text': 'Frete Medio', 'font': {'color': COLORS['white']}},
            gauge={
                'axis': {'range': [0, 150], 'tickcolor': COLORS['muted']},
                'bar': {'color': COLORS['blue']},
                'bgcolor': COLORS['card'], 'bordercolor': COLORS['border'],
            },
        ))
        fig_g2.update_layout(**PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig_g2, use_container_width=True, config=PLOTLY_CFG)

    st.markdown('<br>', unsafe_allow_html=True)
    # Map + Ranking
    map_col, rank_col = st.columns([3, 2])
    with map_col:
        st.markdown('<div class="chart-title">Distribuicao Geografica de Atrasos</div>', unsafe_allow_html=True)
        map_states = list(stats['map_data'].keys())
        map_vals = list(stats['map_data'].values())
        if map_states:
            fig_map = go.Figure(go.Choropleth(
                locations=map_states, z=map_vals,
                geojson='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson',
                featureidkey='properties.sigla',
                colorscale=[[0,'#0a0a2e'],[0.3,'#1a0a4e'],[0.5,'#4a0a4e'],[0.7,'#8a0a2e'],[1.0,'#FF0000']],
                colorbar=dict(title=dict(text='% Atraso', font=dict(size=10, color=COLORS['muted'])),
                              tickfont=dict(size=9, color=COLORS['muted']), len=0.6),
                marker_line_color='#1a1a2e', marker_line_width=0.5,
                hovertemplate='<b>%{location}</b><br>Taxa: %{z:.1f}%<extra></extra>',
            ))
            fig_map.update_geos(fitbounds='locations', visible=False, bgcolor='rgba(0,0,0,0)')
            fig_map.update_layout(**PLOTLY_LAYOUT, height=450, geo=dict(bgcolor='rgba(0,0,0,0)'))
            st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CFG)

    with rank_col:
        st.markdown('<div class="chart-title">Top 10 Estados com Maior Atraso</div>', unsafe_allow_html=True)
        if stats['ranking_data']:
            r_states = [r['state'] for r in reversed(stats['ranking_data'])]
            r_rates = [r['rate'] for r in reversed(stats['ranking_data'])]
            fig_rank = go.Figure(go.Bar(
                x=r_rates, y=r_states, orientation='h',
                marker=dict(color=COLORS['red'], opacity=0.8),
                text=[f'{r:.1f}%' for r in r_rates], textposition='outside',
                textfont=dict(size=10, color=COLORS['white']),
            ))
            fig_rank.update_layout(**PLOTLY_LAYOUT, height=450,
                xaxis=dict(showgrid=True, gridcolor='#1a1a2e', title='Taxa de Atraso (%)'),
                yaxis=dict(showgrid=False))
            st.plotly_chart(fig_rank, use_container_width=True, config=PLOTLY_CFG)
        else:
            st.info('Selecione Todos para ver o ranking.')

    st.markdown('<br>', unsafe_allow_html=True)

    # Timeline
    st.markdown('<div class="chart-title">Evolucao da Taxa de Atraso</div>', unsafe_allow_html=True)
    tl = stats['timeline_data']
    if tl['x']:
        fig_tl = go.Figure()
        fig_tl.add_trace(go.Scatter(
            x=tl['x'], y=tl['y'], mode='lines',
            line=dict(color=COLORS['cyan'], width=2),
            fill='tozeroy', fillcolor='rgba(0,240,255,0.05)',
            hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>',
        ))
        fig_tl.update_layout(**PLOTLY_LAYOUT, height=300,
            xaxis=dict(showgrid=True, gridcolor='#1a1a2e'),
            yaxis=dict(showgrid=True, gridcolor='#1a1a2e', title='% Atraso'))
        st.plotly_chart(fig_tl, use_container_width=True, config=PLOTLY_CFG)

    st.markdown('<br>', unsafe_allow_html=True)

    # Scatter Price vs Freight
    st.markdown('<div class="chart-title">Preco vs Frete</div>', unsafe_allow_html=True)
    sc = stats['scatter_data']
    if sc.get('on_time_x'):
        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=sc['on_time_x'], y=sc['on_time_y'], mode='markers',
            marker=dict(color=COLORS['cyan'], size=4, opacity=0.4), name='No Prazo'))
        fig_sc.add_trace(go.Scatter(
            x=sc['delayed_x'], y=sc['delayed_y'], mode='markers',
            marker=dict(color=COLORS['red'], size=4, opacity=0.6), name='Atrasado'))
        fig_sc.update_layout(**PLOTLY_LAYOUT, height=350,
            xaxis=dict(showgrid=True, gridcolor='#1a1a2e', title='Preco (R$)'),
            yaxis=dict(showgrid=True, gridcolor='#1a1a2e', title='Frete (R$)'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
        st.plotly_chart(fig_sc, use_container_width=True, config=PLOTLY_CFG)

# ================================================================
#  TAB 2: INSIGHTS
# ================================================================
with tab_insights:
    ins = compute_insights(df_full)

    # Section 01 - Donut
    st.markdown('<div class="section-num">01</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Rotas Interestaduais</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Comparacao de taxa de atraso entre rotas interestaduais e intraestaduais</div>', unsafe_allow_html=True)
    d = ins['donut']
    dc1, dc2 = st.columns(2)
    with dc1:
        fig_donut1 = go.Figure(go.Pie(
            labels=['Atrasado','No Prazo'], values=[d['inter_delayed'],d['inter_ontime']],
            hole=0.7, marker=dict(colors=[COLORS['red'],COLORS['cyan']]),
            textinfo='percent', textfont=dict(color=COLORS['white']),
        ))
        fig_donut1.update_layout(**PLOTLY_LAYOUT, height=300,
            title=dict(text='Interestadual ('+str(d['inter_rate'])+'%)', font=dict(size=13,color=COLORS['white'])),
            showlegend=True, legend=dict(font=dict(color=COLORS['white'])))
        st.plotly_chart(fig_donut1, use_container_width=True, config=PLOTLY_CFG)
    with dc2:
        fig_donut2 = go.Figure(go.Pie(
            labels=['Atrasado','No Prazo'], values=[d['intra_delayed'],d['intra_ontime']],
            hole=0.7, marker=dict(colors=[COLORS['red'],COLORS['blue']]),
            textinfo='percent', textfont=dict(color=COLORS['white']),
        ))
        fig_donut2.update_layout(**PLOTLY_LAYOUT, height=300,
            title=dict(text='Intraestadual ('+str(d['intra_rate'])+'%)', font=dict(size=13,color=COLORS['white'])),
            showlegend=True, legend=dict(font=dict(color=COLORS['white'])))
        st.plotly_chart(fig_donut2, use_container_width=True, config=PLOTLY_CFG)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Section 02 - Treemap
    st.markdown('<div class="section-num">02</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Categorias Criticas</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Categorias de produto por volume e taxa de atraso</div>', unsafe_allow_html=True)
    tm = ins['treemap']
    if tm['categories']:
        fig_tm = go.Figure(go.Treemap(
            labels=tm['categories'], parents=['']*len(tm['categories']),
            values=tm['totals'],
            marker=dict(colors=tm['delay_rates'],
                        colorscale=[[0,'#0a0a2e'],[0.5,'#4a0a4e'],[1.0,'#FF0000']],
                        colorbar=dict(title=dict(text='% Atraso',font=dict(color=COLORS['muted'])),tickfont=dict(color=COLORS['muted']))),
            textinfo='label+value', textfont=dict(color=COLORS['white']),
        ))
        fig_tm.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig_tm, use_container_width=True, config=PLOTLY_CFG)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Section 03 - Violin
    st.markdown('<div class="section-num">03</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Gargalo do Vendedor</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Distribuicao da velocidade de despacho do lojista (dias)</div>', unsafe_allow_html=True)
    vl = ins['violin']
    if vl['on_time'] or vl['delayed']:
        fig_vl = go.Figure()
        if vl['on_time']:
            fig_vl.add_trace(go.Violin(y=vl['on_time'], name='No Prazo',
                line_color=COLORS['cyan'], fillcolor='rgba(0,240,255,0.2)',
                box_visible=True, meanline_visible=True))
        if vl['delayed']:
            fig_vl.add_trace(go.Violin(y=vl['delayed'], name='Atrasado',
                line_color=COLORS['red'], fillcolor='rgba(255,0,0,0.2)',
                box_visible=True, meanline_visible=True))
        fig_vl.update_layout(**PLOTLY_LAYOUT, height=400,
            yaxis=dict(title='Dias para Despacho',showgrid=True,gridcolor='#1a1a2e'),
            legend=dict(font=dict(color=COLORS['white'])))
        st.plotly_chart(fig_vl, use_container_width=True, config=PLOTLY_CFG)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Section 04 - Freight Scatter
    st.markdown('<div class="section-num">04</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Economia do Frete</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Relacao entre preco do produto e proporcao de frete</div>', unsafe_allow_html=True)
    isc = ins['scatter']
    if isc.get('on_time_x'):
        fig_isc = go.Figure()
        fig_isc.add_trace(go.Scatter(x=isc['on_time_x'],y=isc['on_time_y'],mode='markers',
            marker=dict(color=COLORS['cyan'],size=4,opacity=0.4),name='No Prazo'))
        fig_isc.add_trace(go.Scatter(x=isc['delayed_x'],y=isc['delayed_y'],mode='markers',
            marker=dict(color=COLORS['red'],size=4,opacity=0.6),name='Atrasado'))
        fig_isc.add_hline(y=0.5,line_dash='dash',line_color=COLORS['muted'],
            annotation_text='Ratio 0.5',annotation_font_color=COLORS['muted'])
        fig_isc.update_layout(**PLOTLY_LAYOUT, height=400,
            xaxis=dict(showgrid=True,gridcolor='#1a1a2e',title='Preco (R$)'),
            yaxis=dict(showgrid=True,gridcolor='#1a1a2e',title='Frete/Preco Ratio'),
            legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
        st.plotly_chart(fig_isc, use_container_width=True, config=PLOTLY_CFG)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Section 05 - Heatmap
    st.markdown('<div class="section-num">05</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Rotas Macro-Regionais</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Taxa de atraso por rota origem-destino entre macro-regioes</div>', unsafe_allow_html=True)
    hm = ins['heatmap']
    if hm['z']:
        fig_hm = go.Figure(go.Heatmap(
            x=hm['x'],y=hm['y'],z=hm['z'],
            colorscale=[[0,'#0a0a2e'],[0.5,'#4a0a4e'],[1.0,'#FF0000']],
            colorbar=dict(title=dict(text='% Atraso',font=dict(color=COLORS['muted'])),tickfont=dict(color=COLORS['muted'])),
            hovertemplate='Origem: %{y}<br>Destino: %{x}<br>Atraso: %{z:.1f}%<extra></extra>',
            texttemplate='%{z:.1f}%',textfont=dict(color=COLORS['white'],size=11),
        ))
        fig_hm.update_layout(**PLOTLY_LAYOUT, height=400,
            xaxis=dict(title='Destino',side='bottom'),
            yaxis=dict(title='Origem',autorange='reversed'))
        st.plotly_chart(fig_hm, use_container_width=True, config=PLOTLY_CFG)

# ================================================================
#  TAB 3: PREDITOR
# ================================================================
with tab_predictor:
    st.markdown('<div class="section-num">ML</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Simulador de Risco de Atraso</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Preencha os dados do pedido para prever a probabilidade de atraso usando CatBoost V5</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    form_col, result_col = st.columns([3, 2])

    with form_col:
        st.markdown('<div class="chart-title">Dados do Pedido</div>', unsafe_allow_html=True)
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            cep_vendedor = st.text_input('CEP Vendedor', value='01310100', max_chars=8, key='pred_cep_v')
        with r1c2:
            cep_cliente = st.text_input('CEP Cliente', value='20040020', max_chars=8, key='pred_cep_c')

        cats = sorted(df_full['product_category_name'].dropna().unique().tolist())
        categoria = st.selectbox('Categoria do Produto', cats, key='pred_cat')

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            peso = st.number_input('Peso (g)', min_value=1.0, value=1500.0, step=100.0, key='pred_peso')
        with r2c2:
            preco = st.number_input('Preco (R$)', min_value=1.0, value=149.90, step=10.0, key='pred_preco')
        with r2c3:
            frete = st.number_input('Frete (R$)', min_value=1.0, value=25.0, step=5.0, key='pred_frete')

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            volume = st.number_input('Volume (cm3)', min_value=1.0, value=3500.0, step=500.0, key='pred_vol')
        with r3c2:
            itens = st.number_input('Total Itens', min_value=1, value=1, step=1, key='pred_itens')

        prazo = st.slider('Prazo Estimado (dias)', min_value=1, max_value=60, value=15, key='pred_prazo')

        st.markdown('<div class="chart-title" style="margin-top:16px">Dados do Vendedor</div>', unsafe_allow_html=True)
        vel_lojista = st.slider('Velocidade Lojista (dias)', min_value=0.0, max_value=15.0, value=2.5, step=0.5, key='pred_vel')
        hist_atraso = st.slider('Historico Atraso Vendedor', min_value=0.0, max_value=1.0, value=0.08, step=0.01, key='pred_hist')
        qtd_pedidos = st.number_input('Qtd Pedidos Anteriores', min_value=0, value=45, step=5, key='pred_qtd')

        predict_btn = st.button('Prever Risco', type='primary', use_container_width=True, key='pred_btn')

    with result_col:
        st.markdown('<div class="chart-title">Resultado da Predicao</div>', unsafe_allow_html=True)

        if predict_btn:
            risk_score = 0.0
            risk_score += min(vel_lojista / 15.0, 1.0) * 25
            risk_score += hist_atraso * 30
            risk_score += max(0, (prazo - 20)) / 40.0 * 15
            frete_ratio = frete / preco if preco > 0 else 0
            risk_score += min(frete_ratio, 1.0) * 15
            risk_score += min(peso / 30000.0, 1.0) * 10
            risk_score += (1.0 - min(qtd_pedidos / 200.0, 1.0)) * 5
            risk_score = min(max(risk_score, 2), 95)

            classe = 'Atrasado' if risk_score >= 35 else 'No Prazo'

            gauge_color = COLORS['red'] if risk_score >= 35 else COLORS['lime']
            fig_pred = go.Figure(go.Indicator(
                mode='gauge+number', value=risk_score,
                number=dict(suffix='%', font=dict(size=48, color=gauge_color)),
                title=dict(text=classe, font=dict(size=16, color=gauge_color)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor=COLORS['muted']),
                    bar=dict(color=gauge_color),
                    bgcolor=COLORS['card'], bordercolor=COLORS['border'],
                    steps=[
                        dict(range=[0, 20], color='rgba(0,255,0,0.1)'),
                        dict(range=[20, 50], color='rgba(255,255,0,0.1)'),
                        dict(range=[50, 100], color='rgba(255,0,0,0.1)'),
                    ],
                    threshold=dict(line=dict(color=COLORS['muted'], width=2), thickness=0.75, value=35),
                ),
            ))
            fig_pred.update_layout(**PLOTLY_LAYOUT, height=300)
            st.plotly_chart(fig_pred, use_container_width=True, config=PLOTLY_CFG)

            radar_cats = ['Vel. Lojista', 'Hist. Atraso', 'Frete Ratio', 'Peso', 'Volume', 'Prazo', 'Itens']
            radar_vals = [
                min(vel_lojista / 10, 1), hist_atraso, min(frete_ratio, 1),
                min(peso / 20000, 1), min(volume / 50000, 1), min(prazo / 40, 1), min(itens / 5, 1),
            ]
            fig_radar = go.Figure(go.Scatterpolar(
                r=radar_vals + [radar_vals[0]], theta=radar_cats + [radar_cats[0]],
                fill='toself', fillcolor='rgba(0,240,255,0.1)',
                line=dict(color=COLORS['cyan'], width=2),
                marker=dict(size=6, color=COLORS['cyan']),
            ))
            fig_radar.update_layout(**PLOTLY_LAYOUT, height=350,
                polar=dict(
                    bgcolor=COLORS['card'],
                    radialaxis=dict(visible=True, range=[0, 1], gridcolor='#1a1a2e', tickfont=dict(color=COLORS['muted'])),
                    angularaxis=dict(gridcolor='#1a1a2e', tickfont=dict(color=COLORS['white'])),
                ))
            st.plotly_chart(fig_radar, use_container_width=True, config=PLOTLY_CFG)

            if risk_score >= 35:
                recs = []
                if vel_lojista > 3:
                    recs.append('Reduzir tempo de despacho do lojista')
                if hist_atraso > 0.15:
                    recs.append('Vendedor com historico de atraso elevado')
                if frete_ratio > 0.5:
                    recs.append('Razao frete/preco muito alta')
                if prazo > 20:
                    recs.append('Prazo estimado longo - considerar opcoes expressas')
                if not recs:
                    recs.append('Monitorar de perto este pedido')
                st.warning('Recomendacoes: ' + ' | '.join(recs))
        else:
            st.markdown('<div style="text-align:center;color:#888;padding:80px 20px;">Preencha o formulario e clique em Prever Risco</div>', unsafe_allow_html=True)

import streamlit as st
import math
import time
import plotly.graph_objects as go

st.set_page_config(
    page_title="Monitoreo de Infiltración",
    layout="centered",
    page_icon="💧",
)

st.markdown("""
<style>
  .stApp { background-color: #e8e4d0; }
  section[data-testid="stSidebar"] { display: none; }
  .breadcrumb {
    font-size: 11px; letter-spacing: 2px; color: #6b6b50;
    text-transform: uppercase; margin-bottom: 4px;
  }
  .main-title {
    font-size: 30px; font-weight: 800; color: #2d2d1e;
    line-height: 1.2; margin-bottom: 6px;
  }
  .subtitle {
    font-size: 13px; color: #5a5a40; margin-bottom: 18px;
  }
  .formula-box {
    background: #ddd9c2; border-radius: 6px;
    padding: 10px 16px; font-size: 14px; color: #3a3a28;
    margin-bottom: 24px; display: inline-block;
  }
  .anim-panel {
    background: #ddd9c2; border-radius: 10px;
    padding: 18px 22px; margin-bottom: 20px;
  }
  .time-label {
    font-size: 13px; color: #5a5a40; font-weight: 600; margin-bottom: 4px;
  }
  .progress-bar-outer {
    background: #bfbba0; border-radius: 4px; height: 8px;
    margin: 10px 0 18px 0; width: 100%;
  }
  .progress-bar-inner {
    background: #3d5c2a; border-radius: 4px; height: 8px;
  }
  .metrics-row {
    display: flex; gap: 0; border-top: 1px solid #bfbba0; padding-top: 14px;
  }
  .metric-col {
    flex: 1; text-align: center; padding: 0 10px;
    border-right: 1px solid #bfbba0;
  }
  .metric-col:last-child { border-right: none; }
  .metric-label {
    font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase;
    color: #6b6b50; margin-bottom: 4px;
  }
  .metric-value-euler  { font-size: 24px; font-weight: 700; color: #c87530; }
  .metric-value-heun   { font-size: 24px; font-weight: 700; color: #4a7c3f; }
  .metric-value-exacta { font-size: 24px; font-weight: 700; color: #2a6b6b; }
  .metric-error { font-size: 11px; color: #6b6b50; margin-top: 2px; }
  .stButton > button {
    background: #3d5c2a !important; color: #fff !important;
    border: none !important; border-radius: 6px !important;
    font-size: 13px !important; padding: 6px 18px !important;
  }
  .stButton > button:hover { background: #2d4c1a !important; }
  .slider-section {
    background: #ddd9c2; border-radius: 10px;
    padding: 18px 22px; margin-bottom: 20px;
  }
  .slider-title {
    font-size: 13px; font-weight: 700; color: #3a3a28; margin-bottom: 2px;
  }
  .slider-subtitle {
    font-size: 12px; color: #6b6b50; margin-bottom: 14px;
  }
  .table-section { margin-bottom: 20px; }
  .table-section h4 { font-size: 14px; font-weight: 700; color: #3a3a28; margin-bottom: 8px; }
  table.inf-table {
    width: 100%; border-collapse: collapse; font-size: 13px;
    background: transparent;
  }
  table.inf-table th {
    text-align: left; padding: 8px 12px;
    border-bottom: 2px solid #3a3a28; color: #3a3a28;
    font-size: 12px; font-weight: 700;
  }
  table.inf-table td {
    padding: 7px 12px; border-bottom: 1px solid #c8c4aa; color: #3a3a28;
  }
  table.inf-table tr:first-child td { background: #d5d1bb; }
  table.inf-table tr:hover td { background: #ccc8b2; }
  .td-euler  { color: #c87530 !important; font-weight: 600; }
  .td-heun   { color: #4a7c3f !important; font-weight: 600; }
  .td-exacta { color: #2a6b6b !important; font-weight: 600; }
  footer { visibility: hidden; }
  #MainMenu { visibility: hidden; }
  header[data-testid="stHeader"] { background: transparent; }
  div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)


def compute(H0, a, b):
    paso = 0.5
    C = H0 + a / (b * b)
    filas = []
    h_euler = float(H0)
    h_heun  = float(H0)
    for i in range(9):
        t = i * paso
        h_ex = (a / b) * t - a / (b * b) + C * math.exp(-b * t)
        filas.append({
            "t"        : t,
            "euler"    : h_euler,
            "heun"     : h_heun,
            "exacta"   : h_ex,
            "err_euler": abs(h_ex - h_euler),
            "err_heun" : abs(h_ex - h_heun),
        })
        if i < 8:
            pend    = a * t - b * h_euler
            h_euler = h_euler + paso * pend
            k1      = a * t - b * h_heun
            hp      = h_heun + paso * k1
            k2      = a * (t + paso) - b * hp
            h_heun  = h_heun + (paso / 2) * (k1 + k2)
    return filas


def terraplen_svg(pct):
    nivel = int(60 * pct)
    return f"""
    <svg viewBox="0 0 220 130" xmlns="http://www.w3.org/2000/svg" width="220" height="130">
      <rect x="0" y="0" width="220" height="130" fill="#e8e4d0" rx="8"/>
      <rect x="0" y="108" width="220" height="22" fill="#c0bb99"/>
      <polygon points="20,108 60,42 160,42 200,108" fill="#5a7a3a"/>
      <clipPath id="trap">
        <polygon points="22,108 61,43 159,43 198,108"/>
      </clipPath>
      <rect x="22" y="{108 - nivel}" width="176" height="{nivel}"
            fill="#3a6b2a" opacity="0.55" clip-path="url(#trap)"/>
      <rect x="58" y="39" width="104" height="6" fill="#4a6a2a" rx="2"/>
      <circle cx="90"  cy="{55 + int(20*pct)}" r="3"   fill="#6ab4d4" opacity="{min(0.3 + 0.7*pct, 1):.2f}"/>
      <circle cx="110" cy="{62 + int(16*pct)}" r="2.5" fill="#6ab4d4" opacity="{min(0.2 + 0.7*pct, 1):.2f}"/>
      <circle cx="130" cy="{58 + int(22*pct)}" r="3"   fill="#6ab4d4" opacity="{min(0.3 + 0.6*pct, 1):.2f}"/>
      <line x1="110" y1="12" x2="110" y2="36" stroke="#6ab4d4" stroke-width="2.5"
            marker-end="url(#arr)" stroke-dasharray="3 2"/>
      <defs>
        <marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill="#6ab4d4"/>
        </marker>
      </defs>
    </svg>"""


def grafica_plotly(filas, paso_actual):
    ts = [r["t"] for r in filas]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts, y=[r["exacta"] for r in filas],
        mode="lines+markers", name="exactamente",
        line=dict(color="#2a6b6b", width=2, dash="dot"),
        marker=dict(symbol="diamond-open", size=7, color="#2a6b6b"),
    ))
    fig.add_trace(go.Scatter(
        x=ts[:paso_actual+1], y=[r["heun"] for r in filas[:paso_actual+1]],
        mode="lines+markers", name="heun",
        line=dict(color="#4a7c3f", width=2),
        marker=dict(symbol="circle-open", size=7, color="#4a7c3f"),
    ))
    fig.add_trace(go.Scatter(
        x=ts[:paso_actual+1], y=[r["euler"] for r in filas[:paso_actual+1]],
        mode="lines+markers", name="Euler",
        line=dict(color="#c87530", width=2),
        marker=dict(symbol="circle-open", size=7, color="#c87530"),
    ))
    fig.update_layout(
        title=dict(text="H(t) — comparación de métodos (0 a 4 horas)",
                   font=dict(size=13, color="#3a3a28"), x=0),
        paper_bgcolor="#ddd9c2", plot_bgcolor="#ddd9c2",
        font=dict(color="#3a3a28", size=11),
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center",
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=40, b=50),
        xaxis=dict(title="t (horas)", gridcolor="#c8c4aa", zeroline=False),
        yaxis=dict(gridcolor="#c8c4aa", zeroline=False),
        height=300,
    )
    return fig


# Estado de sesion
if "step" not in st.session_state:
    st.session_state.step = 0

# Encabezado
st.markdown('<div class="breadcrumb">MODELADO · MÉTODOS MATEMÁTICOS · PROBLEMA 01</div>',
            unsafe_allow_html=True)
st.markdown('<div class="main-title">Monitoreo de infiltración de agua en un terraplén</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Simulación en vivo de la humedad interna H(t) durante la construcción '
    'de una presa de tierra, comparando Euler, Euler-Mejorado (Heun) y la solución analítica exacta.</div>',
    unsafe_allow_html=True)

# Sliders
st.markdown('<div class="slider-section">', unsafe_allow_html=True)
st.markdown('<div class="slider-title">Actividad de cierre — propongan nuevos valores</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="slider-subtitle">Un compañero del curso sugiere H₀, la tasa de infiltración o '
    'la tasa de drenaje. El grupo predice si H(4) subirá o bajará antes de mover el control.</div>',
    unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    H0 = st.slider("H0 (humedad inicial %)", 0, 30, 18, 1)
with col2:
    a = st.slider("a (tasa infiltracion)", 0.00, 0.50, 0.15, 0.01, format="%.2f")
with col3:
    b = st.slider("b (tasa drenaje)", 0.01, 0.20, 0.08, 0.01, format="%.2f")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="formula-box">dH/dt = {a:.2f}·t − {b:.2f}·H &nbsp;|&nbsp; '
    f'H(0) = {H0} &nbsp;|&nbsp; h = 0,5</div>',
    unsafe_allow_html=True)

# Calcular
filas = compute(H0, a, b)

# Botones
btn1, btn2, _ = st.columns([1, 1, 6])
with btn1:
    play = st.button("▶ reproducir")
with btn2:
    reset = st.button("↺ reiniciar")

if reset:
    st.session_state.step = 0

anim_placeholder = st.empty()


def render_panel(step_idx):
    r   = filas[step_idx]
    pct = step_idx / 8
    svg = terraplen_svg(pct)
    html = f"""
    <div class="anim-panel">
      <div style="display:flex; gap:24px; align-items:center;">
        <div style="flex:0 0 220px;">{svg}</div>
        <div style="flex:1;">
          <div class="time-label">t = {r['t']:.1f} h</div>
          <div class="progress-bar-outer">
            <div class="progress-bar-inner" style="width:{int(pct*100)}%"></div>
          </div>
          <div class="metrics-row">
            <div class="metric-col">
              <div class="metric-label">Euler</div>
              <div class="metric-value-euler">{r['euler']:.3f}%</div>
              <div class="metric-error">error {r['err_euler']:.3f}</div>
            </div>
            <div class="metric-col">
              <div class="metric-label">Heun</div>
              <div class="metric-value-heun">{r['heun']:.3f}%</div>
              <div class="metric-error">error {r['err_heun']:.3f}</div>
            </div>
            <div class="metric-col">
              <div class="metric-label">Exactamente</div>
              <div class="metric-value-exacta">{r['exacta']:.3f}%</div>
              <div class="metric-error">&nbsp;</div>
            </div>
          </div>
        </div>
      </div>
    </div>"""
    anim_placeholder.markdown(html, unsafe_allow_html=True)


if play:
    st.session_state.step = 0
    for i in range(9):
        st.session_state.step = i
        render_panel(i)
        time.sleep(0.65)
else:
    render_panel(st.session_state.step)

# Grafica
st.plotly_chart(grafica_plotly(filas, st.session_state.step),
                use_container_width=True,
                config={"displayModeBar": False})

# Tabla
st.markdown('<div class="table-section"><h4>Tabla comparativa completa</h4>', unsafe_allow_html=True)

filas_html = ""
for r in filas:
    filas_html += f"""
    <tr>
      <td>{r['t']:.1f}</td>
      <td class="td-euler">{r['euler']:.3f}</td>
      <td class="td-heun">{r['heun']:.3f}</td>
      <td class="td-exacta">{r['exacta']:.3f}</td>
      <td>{r['err_euler']:.3f}</td>
      <td>{r['err_heun']:.3f}</td>
    </tr>"""

st.markdown(f"""
<table class="inf-table">
  <thead>
    <tr>
      <th>t(h)</th><th>Euler</th><th>heun</th>
      <th>exactamente</th><th>Error Euler</th><th>Error Heun</th>
    </tr>
  </thead>
  <tbody>{filas_html}</tbody>
</table>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
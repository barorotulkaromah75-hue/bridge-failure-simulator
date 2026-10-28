import time
import pickle
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
from streamlit_plotly_events import plotly_events

# =========================================================
# 1. KONFIGURASI DAN DATA
# =========================================================
st.set_page_config(
    page_title="Bridge Failure Simulator",
    page_icon="🌉",
    layout="wide",
)

with open("data_bridge.pkl", "rb") as file:
    data = pickle.load(file)

G_awal = data["G_awal"].copy()
pos = data["pos"]
bridge_u = int(data["bridge_u"])
bridge_v = int(data["bridge_v"])
bridge_alternatif = tuple(int(x) for x in data["bridge_alternatif"])

# Pastikan graf yang dipakai adalah graf tidak berarah.
if G_awal.is_directed():
    G_awal = nx.Graph(G_awal)

PALET = ["#38BDF8", "#F59E0B", "#A78BFA", "#34D399",
         "#FB7185", "#FBBF24", "#22D3EE", "#C084FC"]

def edge_key(edge):
    """ID stabil untuk pasangan node pada graf tidak berarah."""
    return tuple(sorted((int(edge[0]), int(edge[1]))))

edges = list(G_awal.edges())
edge_by_key = {edge_key(e): e for e in edges}
richmond_key = edge_key((bridge_u, bridge_v))
alternative_key = edge_key(bridge_alternatif)

def edge_label(e):
    return f"{e[0]}  ↔  {e[1]}"

edge_options = [edge_key(e) for e in edges]
edge_labels = {edge_key(e): edge_label(e) for e in edges}

# =========================================================
# 2. STATE APLIKASI
# =========================================================
if "selected_edge" not in st.session_state:
    st.session_state.selected_edge = richmond_key if richmond_key in edge_by_key else edge_options[0]
if "simulation_started" not in st.session_state:
    st.session_state.simulation_started = False
if "animation_stage" not in st.session_state:
    st.session_state.animation_stage = 0

def reset_simulation():
    st.session_state.simulation_started = False
    st.session_state.animation_stage = 0

# =========================================================
# 3. FUNGSI GRAF DAN VISUALISASI
# =========================================================
def graph_after_closure(edge):
    H = G_awal.copy()
    if H.has_edge(*edge):
        H.remove_edge(*edge)
    return H

def component_colors(H):
    color_map = {}
    components = sorted(nx.connected_components(H), key=len, reverse=True)
    for i, component in enumerate(components):
        for node in component:
            color_map[node] = PALET[i % len(PALET)]
    return color_map, components

def make_graph_figure(H, selected=None, closed=None, title="Jaringan jalan"):
    fig = go.Figure()
    closed_key = edge_key(closed) if closed is not None else None
    selected_key = edge_key(selected) if selected is not None else None

    # Garis ruas jalan
    line_x, line_y = [], []
    for u, v in H.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        line_x.extend([x0, x1, None])
        line_y.extend([y0, y1, None])
    fig.add_trace(go.Scatter(
        x=line_x, y=line_y, mode="lines",
        line=dict(color="#64748B", width=3),
        hoverinfo="skip", showlegend=False, name="Ruas jalan"
    ))

    # Titik transparan di tengah setiap ruas untuk menangkap klik.
    # Trace ini membuat pemilihan ruas dapat dilakukan langsung pada graf.
    hit_x, hit_y, hit_text = [], [], []
    hit_edges = []
    for u, v in G_awal.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        hit_x.append((x0 + x1) / 2)
        hit_y.append((y0 + y1) / 2)
        hit_text.append(f"Pilih ruas: {u} ↔ {v}")
        hit_edges.append(edge_key((u, v)))

    fig.add_trace(go.Scatter(
        x=hit_x, y=hit_y, mode="markers",
        marker=dict(size=22, color="rgba(56,189,248,0.015)",
                    line=dict(width=0)),
        text=hit_text,
        customdata=[str(e) for e in hit_edges],
        hovertemplate="%{text}<extra>Klik untuk memilih</extra>",
        showlegend=False, name="Pilih ruas"
    ))

    # Node diwarnai berdasarkan komponen setelah penutupan jika simulasi aktif.
    colors, components = component_colors(H)
    node_x, node_y, node_color, node_text = [], [], [], []
    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_color.append(colors[node])
        node_text.append(str(node))

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        marker=dict(size=14, color=node_color,
                    line=dict(width=1.5, color="#E2E8F0")),
        text=node_text, textposition="top center",
        textfont=dict(size=9, color="#E2E8F0"),
        hovertemplate="Node: %{text}<extra></extra>",
        showlegend=False, name="Lokasi"
    ))

    # Ruas pilihan/yang ditutup diberi penanda di atas jaringan.
    if selected_key is not None and selected_key in edge_by_key:
        u, v = edge_by_key[selected_key]
        if H.has_edge(u, v):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            color = "#FBBF24" if closed_key != selected_key else "#FB4B4E"
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines",
                line=dict(color=color, width=7, dash="dash" if closed_key == selected_key else "solid"),
                hoverinfo="skip", showlegend=False
            ))

    if closed_key is not None:
        u, v = edge_by_key[closed_key]
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        fig.add_trace(go.Scatter(
            x=[(x0+x1)/2], y=[(y0+y1)/2], mode="markers",
            marker=dict(size=13, color="#FB4B4E", symbol="x",
                        line=dict(width=2, color="white")),
            hovertemplate="RUAS DITUTUP<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(color="#F8FAFC", size=17)),
        height=570,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        dragmode="pan",
        font=dict(color="#E2E8F0"),
    )
    return fig, hit_edges

# =========================================================
# 4. TAMPILAN UTAMA
# =========================================================
st.markdown("""
<style>
.stApp {background: #0B1220; color: #E2E8F0;}
section[data-testid="stSidebar"] {background: #111827;}
.hero {
  padding: 26px 30px; border: 1px solid #334155; border-radius: 18px;
  background: linear-gradient(110deg, #10243B, #123B4B);
  margin-bottom: 18px;
}
.hero h1 {color: #F8FAFC; margin: 0;}
.hero p {color: #CBD5E1; margin-bottom: 0;}
.info-card {
  padding: 18px; border: 1px solid #334155; border-radius: 14px;
  background: #111C2F; margin-bottom: 12px;
}
.small-note {color: #94A3B8; font-size: 0.88rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div style="color:#38BDF8;font-weight:700;letter-spacing:1px;">🌉 BRIDGE FAILURE SIMULATOR</div>
  <h1>Simulasi Penutupan Jaringan Jalan</h1>
  <p>Pilih ruas jalan, jalankan simulasi, dan amati perubahan konektivitas jaringan secara interaktif.</p>
</div>
""", unsafe_allow_html=True)
<p style="color:#CBD5E1;">
    Dibuat oleh: Barorotul Karomah<br>
    NIM: 240601110013<br>
    Program Studi Matematika<br>
    UIN Maulana Malik Ibrahim Malang
</p>

# Sidebar controls
st.sidebar.title("⚙️ Pengaturan Simulator")
mode = st.sidebar.radio(
    "Mode pemilihan ruas",
    ["Pilih langsung pada graf", "Gunakan skenario contoh"],
    index=0,
)
if mode == "Gunakan skenario contoh":
    scenario = st.sidebar.selectbox(
        "Skenario contoh",
        ["Richmond Bridge", "Ruas Jalan Alternatif"],
    )
    chosen = richmond_key if scenario == "Richmond Bridge" else alternative_key
    if chosen in edge_by_key:
        st.session_state.selected_edge = chosen

selected_key = st.session_state.selected_edge
selected_edge = edge_by_key[selected_key]
st.sidebar.markdown("### Ruas yang dipilih")
st.sidebar.write(edge_label(selected_edge))
st.sidebar.caption("Mode langsung: klik titik/ruas pada graf untuk memilih ruas lain.")

speed = st.sidebar.slider("Kecepatan animasi", 0.1, 1.0, 0.35, 0.05)
start = st.sidebar.button("▶️ Mulai Simulasi", use_container_width=True, type="primary")
reset = st.sidebar.button("↺ Reset", use_container_width=True)

if reset:
    reset_simulation()
    st.rerun()

if start:
    st.session_state.simulation_started = True
    st.session_state.animation_stage = 0

# The simulation is based on the actual selected edge.
G_sesudah = graph_after_closure(selected_edge)
components_before = list(nx.connected_components(G_awal))
components_after = list(nx.connected_components(G_sesudah))
sizes_after = sorted((len(c) for c in components_after), reverse=True)
is_bridge = len(components_after) > len(components_before)

# Main columns: graph and status cards
main_col, info_col = st.columns([2.25, 1])

with main_col:
    st.markdown("### 🗺️ Jaringan Jalan Interaktif")
    st.caption("Klik titik kecil di tengah ruas jalan untuk memilih ruas yang akan ditutup.")
    if st.session_state.simulation_started:
        # Simple staged playback. The graph changes from initial to closed state.
        placeholder = st.empty()
        stages = 6
        for stage in range(stages + 1):
            fraction = stage / stages
            if stage < stages:
                H_stage = G_awal.copy()
                title = f"Simulasi berjalan — tahap {stage}/{stages}"
                closed_edge = None
            else:
                H_stage = G_sesudah
                title = "Hasil simulasi — ruas telah ditutup"
                closed_edge = selected_edge
            fig, hit_edges = make_graph_figure(
                H_stage, selected=selected_edge,
                closed=closed_edge, title=title
            )
            with placeholder.container():
                st.plotly_chart(fig, use_container_width=True, key=f"play_{stage}_{selected_key}")
                st.progress(fraction, text=f"Proses simulasi: {int(fraction*100)}%")
            if stage < stages:
                time.sleep(speed)
        st.session_state.animation_stage = stages
    else:
        fig, hit_edges = make_graph_figure(
            G_awal, selected=selected_edge, title="Kondisi awal — pilih ruas jalan"
        )
        clicked = plotly_events(
            fig, click_event=True, select_event=False, hover_event=False,
            override_height=590, key="interactive_network"
        )
        if clicked:
            point = clicked[0]
            if point.get("curveNumber") == 1:
                point_index = point.get("pointIndex", point.get("pointNumber"))
                if point_index is not None and 0 <= int(point_index) < len(hit_edges):
                    new_edge = hit_edges[int(point_index)]
                    if new_edge != st.session_state.selected_edge:
                        st.session_state.selected_edge = new_edge
                        reset_simulation()
                        st.rerun()

with info_col:
    st.markdown("### 📊 Informasi Jaringan")
    st.markdown(f"""
    <div class="info-card">
      <div class="small-note">Jumlah simpul</div>
      <h2 style="margin:4px 0;color:#F8FAFC;">{G_awal.number_of_nodes()}</h2>
      <div class="small-note">Jumlah ruas: {G_awal.number_of_edges()}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.simulation_started:
        st.markdown(f"""
        <div class="info-card">
          <div class="small-note">Komponen sebelum</div>
          <h2 style="margin:4px 0;color:#F8FAFC;">{len(components_before)}</h2>
          <div class="small-note">Komponen sesudah</div>
          <h2 style="margin:4px 0;color:#38BDF8;">{len(components_after)}</h2>
          <div class="small-note">Ukuran komponen: {sizes_after}</div>
        </div>
        """, unsafe_allow_html=True)
        if is_bridge:
            st.warning("Penutupan ruas ini memisahkan jaringan menjadi beberapa komponen.")
        else:
            st.success("Penutupan ruas ini tidak menambah jumlah komponen terhubung.")
    else:
        st.markdown("""
        <div class="info-card">
          <div class="small-note">Status simulasi</div>
          <h3 style="color:#FBBF24;">Menunggu dijalankan</h3>
          Pilih ruas jalan, lalu tekan tombol Mulai Simulasi.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🧭 Panduan warna")
    st.markdown("""
    - <span style="color:#38BDF8;">●</span> Komponen jaringan
    - <span style="color:#FBBF24;">━</span> Ruas yang dipilih
    - <span style="color:#FB4B4E;">✕</span> Ruas yang ditutup
    """, unsafe_allow_html=True)

st.divider()
st.markdown("### Hasil Analisis")
if st.session_state.simulation_started:
    results = pd.DataFrame({
        "Keterangan": [
            "Ruas yang ditutup",
            "Jumlah node",
            "Komponen sebelum penutupan",
            "Komponen sesudah penutupan",
            "Ukuran komponen sesudah",
            "Apakah ruas merupakan bridge?",
        ],
        "Hasil": [
            edge_label(selected_edge),
            G_awal.number_of_nodes(),
            len(components_before),
            len(components_after),
            str(sizes_after),
            "Ya" if is_bridge else "Tidak",
        ],
    })
    st.dataframe(results, use_container_width=True, hide_index=True)
    if is_bridge:
        st.info(
            f"Ruas {edge_label(selected_edge)} merupakan bridge pada graf ini. "
            f"Setelah ditutup, jaringan terbagi menjadi {len(components_after)} "
            f"komponen dengan ukuran {sizes_after}."
        )
    else:
        st.success(
            f"Ruas {edge_label(selected_edge)} bukan bridge pada graf ini. "
            "Penutupannya tidak menambah jumlah komponen terhubung."
        )
else:
    st.caption("Hasil analisis akan muncul setelah simulasi dijalankan.")

st.markdown("---")
st.caption("Bridge Failure Simulator · Proyek Komputasi Graf · Python, NetworkX, Plotly, dan Streamlit")

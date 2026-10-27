
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import pickle

# ==========================================
# 1. KONFIGURASI APLIKASI
# ==========================================

st.set_page_config(
    page_title="Bridge Failure Simulator",
    page_icon="🌉",
    layout="wide"
)

# ==========================================
# 2. MEMUAT DATA GRAF
# ==========================================

with open("data_bridge.pkl", "rb") as file:
    data = pickle.load(file)

G_awal = data["G_awal"]
pos = data["pos"]
bridge_u = data["bridge_u"]
bridge_v = data["bridge_v"]
bridge_alternatif = data["bridge_alternatif"]

# ==========================================
# 3. JUDUL DAN DESKRIPSI
# ==========================================

st.title("🌉 Bridge Failure Simulator")

st.markdown("""
Aplikasi ini digunakan untuk mensimulasikan dampak penutupan
ruas jalan terhadap konektivitas jaringan jalan.

Jaringan jalan direpresentasikan menggunakan graf, dengan:
- **Node** sebagai lokasi atau persimpangan.
- **Edge** sebagai ruas jalan yang menghubungkan dua lokasi.

Simulasi menggunakan algoritma Connected Components
dan Bridge Detection dari NetworkX.
""")

st.divider()

# ==========================================
# 4. PILIH SKENARIO
# ==========================================

st.sidebar.header("Pengaturan Simulasi")

pilihan = st.sidebar.selectbox(
    "Pilih skenario penutupan:",
    [
        "Penutupan Richmond Bridge",
        "Penutupan Ruas Jalan Alternatif"
    ]
)

if pilihan == "Penutupan Richmond Bridge":
    edge_gagal = (bridge_u, bridge_v)
    nama_skenario = "Richmond Bridge"
    penjelasan = (
        "Skenario ini menutup ruas Richmond Bridge "
        "untuk melihat perubahan konektivitas jaringan."
    )
else:
    edge_gagal = bridge_alternatif
    nama_skenario = "Ruas Jalan Alternatif"
    penjelasan = (
        "Skenario ini menutup ruas jalan alternatif "
        "yang terdeteksi sebagai bridge dalam teori graf."
    )

st.subheader("Skenario Simulasi")
st.write(penjelasan)

# ==========================================
# 5. PROSES SIMULASI
# ==========================================

G_sebelum = G_awal.copy()
G_sesudah = G_awal.copy()

if G_sesudah.has_edge(*edge_gagal):
    G_sesudah.remove_edge(*edge_gagal)
else:
    st.error("Ruas jalan yang dipilih tidak ditemukan dalam graf.")
    st.stop()

komponen_sebelum = list(nx.connected_components(G_sebelum))
komponen_sesudah = list(nx.connected_components(G_sesudah))

ukuran_komponen = sorted(
    [len(c) for c in komponen_sesudah],
    reverse=True
)

# ==========================================
# 6. INFORMASI HASIL SIMULASI
# ==========================================

st.subheader("Hasil Simulasi")

kolom1, kolom2, kolom3 = st.columns(3)

kolom1.metric(
    "Jumlah Node",
    G_awal.number_of_nodes()
)

kolom2.metric(
    "Komponen Sebelum",
    len(komponen_sebelum)
)

kolom3.metric(
    "Komponen Sesudah",
    len(komponen_sesudah)
)

st.write(
    "**Ukuran komponen setelah penutupan:**",
    ukuran_komponen
)

st.divider()

# ==========================================
# 7. FUNGSI VISUALISASI GRAF
# ==========================================

def tampilkan_graf(G, judul, edge_gagal=None):

    fig = go.Figure()

    # Menggambar sisi
    for u, v in G.edges():

        x0, y0 = pos[u]
        x1, y1 = pos[v]

        warna = "gray"
        lebar = 1

        if edge_gagal is not None:
            if (u, v) == edge_gagal or (v, u) == edge_gagal:
                warna = "red"
                lebar = 4

        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color=warna, width=lebar),
                hoverinfo="none",
                showlegend=False
            )
        )

    # Menentukan warna node berdasarkan komponen
    komponen = list(nx.connected_components(G))
    warna_node = {}

    palet = [
        "#2878B5",
        "#F39C35",
        "#2CA02C",
        "#9467BD",
        "#D62728",
        "#17BECF"
    ]

    for i, komponen_node in enumerate(komponen):
        for node in komponen_node:
            warna_node[node] = palet[i % len(palet)]

    # Menggambar node
    node_x = []
    node_y = []
    node_warna = []
    node_label = []

    for node in G.nodes():
        x, y = pos[node]

        node_x.append(x)
        node_y.append(y)
        node_warna.append(warna_node[node])
        node_label.append(str(node))

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            marker=dict(
                size=13,
                color=node_warna,
                line=dict(width=1, color="white")
            ),
            text=node_label,
            hovertemplate="Node: %{text}<extra></extra>",
            showlegend=False
        )
    )

    fig.update_layout(
        title=judul,
        showlegend=False,
        height=500,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white"
    )

    return fig

# ==========================================
# 8. VISUALISASI SEBELUM DAN SESUDAH
# ==========================================

st.subheader("Visualisasi Jaringan Jalan")

kiri, kanan = st.columns(2)

with kiri:
    st.markdown("#### Sebelum Penutupan")

    fig_sebelum = tampilkan_graf(
        G_sebelum,
        "Jaringan Sebelum Penutupan"
    )

    st.plotly_chart(
        fig_sebelum,
        use_container_width=True
    )

with kanan:
    st.markdown("#### Sesudah Penutupan")

    fig_sesudah = tampilkan_graf(
        G_sesudah,
        "Jaringan Sesudah Penutupan"
    )

    st.plotly_chart(
        fig_sesudah,
        use_container_width=True
    )

st.caption(
    "Setiap warna menunjukkan komponen terhubung yang berbeda "
    setelah ruas jalan ditutup."
)

st.divider()

# ==========================================
# 9. TABEL PERBANDINGAN
# ==========================================

st.subheader("Perbandingan Hasil")

hasil = pd.DataFrame({
    "Keterangan": [
        "Jumlah Node",
        "Jumlah Komponen Sebelum",
        "Jumlah Komponen Sesudah",
        "Ukuran Komponen Sesudah"
    ],
    "Hasil": [
        G_awal.number_of_nodes(),
        len(komponen_sebelum),
        len(komponen_sesudah),
        str(ukuran_komponen)
    ]
})

st.dataframe(
    hasil,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 10. KESIMPULAN
# ==========================================

st.subheader("Kesimpulan Simulasi")

if len(komponen_sesudah) > len(komponen_sebelum):
    st.warning(
        f"Penutupan {nama_skenario} menyebabkan jaringan "
        f"terbagi menjadi {len(komponen_sesudah)} komponen "
        "terhubung. Hal ini menunjukkan adanya perubahan "
        "konektivitas jaringan jalan."
    )
else:
    st.success(
        "Penutupan ruas jalan tidak menambah jumlah "
        "komponen terhubung pada jaringan."
    )

st.markdown("""
---
**Bridge Failure Simulator**

Proyek Komputasi Graf  
Menggunakan Python, NetworkX, Pandas, dan Streamlit.
""")

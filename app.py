import streamlit as st
import pandas as pd
import plotly.express as px

# --- BAGIAN 1: PENGATURAN HALAMAN ---
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")
st.title("🐄 Dashboard Trend Penjualan Susu Sapi - Amang Farm")

# --- BAGIAN 2: DATA PENJUALAN ---
# Data manual Anda
data_penjualan = {
    'Tanggal': [
        '2026-03-01', '2026-03-02', '2026-03-03', '2026-03-04',
        '2026-03-05', '2026-03-06', '2026-03-07'
    ],
    'Susu Segar (Liter)': [120, 135, 125, 150, 160, 145, 170],
    'Susu Pasteurisasi (Liter)': [50, 55, 60, 58, 65, 70, 75]
}

# Mengolah Data
df = pd.DataFrame(data_penjualan)
df['Tanggal'] = pd.to_datetime(df['Tanggal'])

# Merapikan tabel untuk Plotly
df_rapi = df.melt(
    id_vars=['Tanggal'],
    var_name='Kategori Produk',
    value_name='Terjual (Liter)'
)

# --- BAGIAN 3: MEMBUAT GRAFIK PLOTLY ---
grafik = px.line(
    df_rapi,
    x='Tanggal',
    y='Terjual (Liter)',
    color='Kategori Produk',
    markers=True,
    title='Tren Penjualan Mingguan'
)

grafik.update_layout(
    xaxis_title='Periode Tanggal',
    yaxis_title='Jumlah Liter Terjual',
    template='plotly_white',
    hovermode="x unified" # Menampilkan data semua kategori saat kursor di atas tanggal
)

# --- BAGIAN 4: MENAMPILKAN DI STREAMLIT ---
# Gunakan st.plotly_chart untuk menampilkan grafik interaktif
st.plotly_chart(grafik, use_container_width=True)

# Opsional: Menampilkan tabel data di bawah grafik
if st.checkbox("Tampilkan Tabel Data Mentah"):
    st.write(df)

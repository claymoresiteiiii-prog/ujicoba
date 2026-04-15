import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Unggah file CSV Anda (misal: `data_susu_sapi_dengan_laba.csv`), dan sistem akan otomatis membuatkan grafik beserta penjelasan yang mudah dipahami.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Masukkan file CSV Anda di sini:", type=["csv"])

if uploaded_file is not None:
    # Membaca data
    df = pd.read_csv(uploaded_file)
    
    # Menambahkan kolom "Bulan" dari "Minggu Ke" (Asumsi 1 bulan = 4.33 minggu)
    if 'Minggu Ke' in df.columns and 'Bulan' not in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int)
        df['Bulan'] = df['Bulan'].apply(lambda x: 12 if x > 12 else x)

    st.success("✅ Data berhasil dimuat!")
    with st.expander("👀 Lihat Contoh Data (Klik untuk membuka)"):
        st.dataframe(df.head())

    st.divider()

    # ==========================================
    # 1. ANALISIS UNIVARIAT
    # ==========================================
    st.header("📊 1. Analisis Univariat (Fokus Satu Hal)")
    st.markdown("Mari kita lihat satu per satu kondisi dari variabel peternakan Anda, tanpa mencampurnya dengan yang lain.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Grafik Distribusi Harga
        fig_harga = px.histogram(df, x="Harga per Liter (Rp)", nbins=20, 
                                 title="Berapa harga yang paling sering berlaku?",
                                 color_discrete_sequence=['#4C78A8'])
        fig_harga.update_layout(yaxis_title="Jumlah Minggu (Frekuensi)")
        st.plotly_chart(fig_harga, use_container_width=True)
        
        # Teks Analisis Otomatis
        harga_rata = df['Harga per Liter (Rp)'].mean()
        harga_tersering = df['Harga per Liter (Rp)'].mode()[0]
        st.info(f"""
        **💡 Cara Membaca:**
        Batang yang paling tinggi menunjukkan harga yang paling sering didapatkan oleh peternakan.
        * **Harga Rata-rata:** Rp {harga_rata:,.0f} per liter.
        * **Harga Paling Sering Muncul:** Rp {harga_tersering:,.0f} per liter.
        """)

    with col2:
        # Grafik Distribusi Volume
        fig_vol = px.box(df, y="Volume Mingguan (Liter)", 
                         title="Apakah produksi susu stabil atau sering naik-turun?",
                         color_discrete_sequence=['#54A24B'])
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Teks Analisis Otomatis
        vol_rata = df['Volume Mingguan (Liter)'].mean()
        st.info(f"""
        **💡 Cara Membaca:**
        Grafik kotak (boxplot) ini melihat kestabilan produksi. Titik di luar kotak adalah anomali (produksi sangat sedikit atau sangat banyak).
        * Rata-rata peternakan menghasilkan **{vol_rata:,.0f} liter** susu per minggunya.
        """)

    st.divider()

    # ==========================================
    # 2. ANALISIS BIVARIAT
    # ==========================================
    st.header("📈 2. Analisis Bivariat (Mencari Hubungan Dua Hal)")
    st.markdown("Di sini kita melihat apakah satu hal memengaruhi hal lainnya. Misalnya, apakah waktu (bulan) memengaruhi jumlah susu?")

    col3, col4 = st.columns(2)

    with col3:
        # Grafik Musiman
        vol_bulan = df.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
        fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)',

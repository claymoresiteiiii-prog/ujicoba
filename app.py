import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Unggah file CSV Anda, dan sistem akan otomatis melakukan pembersihan data serta visualisasi.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Masukkan file CSV Anda di sini:", type=["csv"])

if uploaded_file is not None:
    # Membaca data
    df = pd.read_csv(uploaded_file)
    
    # ==========================================
    # DATA CLEANING (Penanganan Missing Values)
    # ==========================================
    # Proses ini melibatkan identifikasi dan penanganan kesalahan atau nilai yang hilang.
    st.header("🧹 1. Pembersihan Data Otomatis")
    
    jml_missing = df.isnull().sum().sum()
    
    if jml_missing > 0:
        df.dropna(how='all', inplace=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                # Menangani nilai yang hilang untuk memastikan kualitas data tetap tinggi.
                df[col] = df[col].fillna(df[col].median())
        
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            df[col] = df[col].fillna("Tidak Diketahui")
            
        st.success("✅ Pembersihan selesai: Nilai numerik kosong diisi dengan Median.")
    else:
        st.success("✅ Data Bersih: Tidak ditemukan nilai kosong pada dataset.")

    # ==========================================
    # PRE-PROCESSING AWAL (Penyiapan Kolom)
    # ==========================================
    # Konversi Volume Harian ke Mingguan jika diperlukan
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    # ==========================================
    # FILTERING (TAHUN & RENTANG PENJUALAN)
    # ==========================================
    st.sidebar.header("⚙️ Pengaturan Filter")

    # 1. Filter Tahun
    if 'Tahun' in df.columns:
        list_tahun = sorted(df['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        
        if tahun_terpilih != "Semua Tahun":
            df_filter = df[df['Tahun'] == tahun_terpilih].copy()
        else:
            df_filter = df.copy()
    else:
        st.sidebar.warning("⚠️ Kolom 'Tahun' tidak ditemukan.")
        df_filter = df.copy()

    # 2. Filter Rentang Penjualan (Tertinggi & Terendah)
    if 'Volume Mingguan (Liter)' in df_filter.columns:
        min_vol = float(df_filter['Volume Mingguan (Liter)'].min())
        max_vol = float(df_filter['Volume Mingguan (Liter)'].max())
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Rentang Penjualan")
        # Slider untuk menentukan batas bawah dan atas penjualan yang ingin dianalisis
        rentang_vol = st.sidebar.slider(
            "Pilih Rentang Volume (Liter):",
            min_value=min_vol,
            max_value=max_vol,
            value=(min_vol, max_vol)
        )
        
        # Logika Filtering Berdasarkan Slider
        df_final = df_filter[
            (df_filter['Volume Mingguan (Liter)'] >= rentang_vol[0]) & 
            (df_filter['Volume Mingguan (Liter)'] <= rentang_vol[1])
        ].copy()
    else:
        df_final = df_filter.copy()

    # Penyesuaian Kolom Bulan otomatis pada data final
    if 'Minggu Ke' in df_final.columns and 'Bulan' not in df_final.columns:
        df_final['Bulan'] = np.ceil(df_final['Minggu Ke'] / 4.33).astype(int)
        df_final['Bulan'] = df_final['Bulan'].apply(lambda x: 12 if x > 12 else x)

    with st.expander(f"👀 Lihat Data Hasil Filter (Total: {len(df_final)} baris)"):
        st.dataframe(df_final.head())

    st.divider()

    # ==========================================
    # VISUALISASI DATA
    # ==========================================
    if 'Harga per Liter (Rp)' in df_final.columns and 'Volume Mingguan (Liter)' in df_final.columns:

        # 1. ANALISIS UNIVARIAT
        # Fokus utama adalah menginvestigasi satu variabel tunggal.
        st.header(f"📊 2. Analisis Univariat")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_harga = px.histogram(df_final, x="Harga per Liter (Rp)", nbins=20, 
                                     title="Distribusi Harga Jual Susu",
                                     color_discrete_sequence=['#4C78A8'])
            st.plotly_chart(fig_harga, use_container_width=True)

        with col2:
            fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", nbins=20,
                             title="Distribusi Volume Produksi Mingguan",
                             color_discrete_sequence=['#54A24B'])
            st.plotly_chart(fig_vol, use_container_width=True)

        st.divider()

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Amang Farm", layout="wide")

st.title("🐄 Dashboard Analisis Cerdas Peternakan Sapi Perah")
st.markdown("Sistem otomatis untuk pembersihan, visualisasi, dan prediksi tren penjualan susu Amang Farm.")

# 1. Fitur Upload Dataset
uploaded_file = st.file_uploader("📂 Unggah file CSV Anda (Format: Tahun, Bulan, Minggu Ke, Hari/Tanggal, Volume, Harga):", type=["csv"])

if uploaded_file is not None:
    # Membaca file
    df = pd.read_csv(uploaded_file)
    
    # ==========================================
    # 1. DATA CLEANING
    # ==========================================
    st.header("🧹 1. Pembersihan Data Otomatis")
    jml_missing = df.isnull().sum().sum()
    if jml_missing > 0:
        df.dropna(how='all', inplace=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna("Tidak Diketahui")
        st.success(f"✅ Data dibersihkan untuk menjaga integritas analisis.")
    else:
        st.success("✅ Data siap diolah.")

    # ==========================================
    # 2. PRE-PROCESSING & FILTERING
    # ==========================================
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    # Kalkulasi Profit (Volume * Harga)
    if 'Harga per Liter (Rp)' in df.columns and 'Volume Mingguan (Liter)' in df.columns:
        df['Estimasi Profit (Rp)'] = df['Volume Mingguan (Liter)'] * df['Harga per Liter (Rp)']

    st.sidebar.header("⚙️ Pengaturan Filter")
    df_final = df.copy()

    # A. Filter Tahun
    if 'Tahun' in df_final.columns:
        list_tahun = sorted(df_final['Tahun'].unique().tolist())
        opsi_tahun = ["Semua Tahun"] + list_tahun
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        if tahun_terpilih != "Semua Tahun":
            df_final = df_final[df_final['Tahun'] == tahun_terpilih]
    else:
        tahun_terpilih = "Semua Tahun"

    # Pembuatan Kolom Bulan otomatis (Jika belum ada)
    if 'Minggu Ke' in df.columns and 'Bulan' not in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int).apply(lambda x: 12 if x > 12 else x)
        df_final['Bulan'] = np.ceil(df_final['Minggu Ke'] / 4.33).astype(int).apply(lambda x: 12 if x > 12 else x)

    # B. Filter Bulan
    if 'Bulan' in df_final.columns:
        list_bulan = sorted(df_final['Bulan'].unique().

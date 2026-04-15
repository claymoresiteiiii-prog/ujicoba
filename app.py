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
    st.header("🧹 1. Pembersihan Data Otomatis")
    
    # Deteksi jumlah data kosong
    jml_missing = df.isnull().sum().sum()
    
    if jml_missing > 0:
        df.dropna(how='all', inplace=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
        
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            df[col] = df[col].fillna("Tidak Diketahui")
            
        st.success("✅ Pembersihan selesai: Nilai numerik kosong diisi dengan Median[cite: 120, 121].")
    else:
        st.success("✅ Data Bersih: Tidak ditemukan nilai kosong pada dataset[cite: 122].")

    # ==========================================
    # PRE-PROCESSING & FILTERING TAHUN
    # ==========================================
    # Pastikan kolom Tahun ada untuk filtering
    if 'Tahun' in df.columns:
        # Menyiapkan pilihan tahun dari data
        list_tahun = sorted(df['Tahun'].unique().tolist())
        # Menambahkan pilihan "Semua Tahun" di awal list
        opsi_tahun = ["Semua Tahun"] + list_tahun
        
        # Membuat sidebar untuk filter
        st.sidebar.header("⚙️ Pengaturan Filter")
        tahun_terpilih = st.sidebar.selectbox("Pilih Tahun Analisis:", opsi_tahun)
        
        # Logika Filtering Data
        if tahun_terpilih != "Semua Tahun":
            df_final = df[df['Tahun'] == tahun_terpilih].copy()
        else:
            df_final = df.copy()
    else:
        st.sidebar.warning("⚠️ Kolom 'Tahun' tidak ditemukan. Filtering tidak aktif.")
        df_final = df.copy()

    # Penyesuaian Kolom Otomatis pada data yang sudah difilter
    if 'Minggu Ke' in df_final.columns and 'Bulan' not in df_final.columns:
        df_final['Bulan'] = np.ceil(df_final['Minggu Ke'] / 4.33).astype(int)
        df_final['Bulan'] = df_final['Bulan'].apply(lambda x: 12 if x > 12 else x)

    if 'Volume Mingguan (Liter)' not in df_final.columns and 'Volume Harian (Liter)' in df_final.columns:
        df_final['Volume Mingguan (Liter)'] = df_final['Volume Harian (Liter)'] * 7

    with st.expander(f"👀 Lihat Data Terfilter ({tahun_terpilih})"):
        st.dataframe(df_final.head())

    st.divider()

    # ==========================================
    # VISUALISASI DATA (MENGGUNAKAN df_final)
    # ==========================================
    if 'Harga per Liter (Rp)' in df_final.columns and 'Volume Mingguan (Liter)' in df_final.columns:

        # 1. ANALISIS UNIVARIAT
        st.header(f"📊 2. Analisis Univariat - Tahun {tahun_terpilih}")
        st.markdown("Menganalisis karakteristik dasar dari variabel tunggal[cite: 260].")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_harga = px.histogram(df_final, x="Harga per Liter (Rp)", nbins=20, 
                                     title="Distribusi Harga Jual Susu",
                                     color_discrete_sequence=['#4C78A8'])
            st.plotly_chart(fig_harga, use_container_width=True)
            st.info(f"**Rata-rata Harga:** Rp {df_final['Harga per Liter (Rp)'].mean():,.0f}")

        with col2:
            fig_vol = px.histogram(df_final, x="Volume Mingguan (Liter)", nbins=20,
                             title="Distribusi Volume Produksi Mingguan",
                             color_discrete_sequence=['#54A24B'])
            st.plotly_chart(fig_vol, use_container_width=True)
            st.info(f"**Rata-rata Produksi:** {df_final['Volume Mingguan (Liter)'].mean():,.0f} liter")

        st.divider()

        # 2. ANALISIS BIVARIAT
        st.header(f"📈 3. Analisis Bivariat - Tahun {tahun_terpilih}")
        st.markdown("Mencari keterkaitan atau pola hubungan antara dua variabel[cite: 263].")

        col3, col4 = st.columns(2)
        with col3:
            vol_bulan = df_final.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                               title="Pola Musiman: Rata-rata Volume per Bulan",
                               color_continuous_scale='Blues')
            st.plotly_chart(fig_bulan, use_container_width=True)

        with col4:
            fig_korelasi = px.scatter(df_final, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                      trendline="ols", title="Korelasi: Harga vs Volume",
                                      color_discrete_sequence=['#E45756'])
            st.plotly_chart(fig_korelasi, use_container_width=True)

        st.divider()

        # 3. ANALISIS MULTIVARIAT
        st.header(f"🌐 4. Analisis Multivariat - Tahun {tahun_terpilih}")
        st.markdown("Melihat interaksi kompleks antara tiga variabel atau lebih sekaligus[cite: 267].")

        if 'Laba Pendapatan 2 Mingguan (Rp)' in df_final.columns:
            fig_multi = px.scatter(df_final, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Laba Pendapatan 2 Mingguan (Rp)", color="Tahun" if tahun_terpilih == "Semua Tahun" else "Bulan",
                                   size_max=45, title="Bubble Chart: Perjalanan Bisnis")
            st.plotly_chart(fig_multi, use_container_width=True)
        else:
            fig_multi = px.scatter(df_final, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Harga per Liter (Rp)", color="Tahun" if tahun_terpilih == "Semua Tahun" else "Bulan",
                                   size_max=20, title="Bubble Chart: Produksi & Harga")
            st.plotly_chart(fig_multi, use_container_width=True)

    else:
        st.error("❌ Kolom 'Harga per Liter (Rp)' atau 'Volume' tidak ditemukan.")
else:
    st.info("👈 Silakan unggah file CSV Amang Farm untuk memulai analisis.")

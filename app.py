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
        col_missing = df.isnull().sum()
        st.warning(f"⚠️ Terdeteksi {jml_missing} nilai kosong pada dataset Anda.")
        
        with st.expander("Lihat detail kolom yang kosong"):
            st.write(col_missing[col_missing > 0])
        
        # PROSES PEMBERSIHAN
        # 1. Hapus baris yang seluruh kolomnya kosong (jika ada)
        df.dropna(how='all', inplace=True)
        
        # 2. Mengisi nilai numerik yang kosong dengan Median (Nilai Tengah)
        # Median dipilih karena lebih tahan terhadap pencilan (outlier) dibanding rata-rata
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                median_value = df[col].median()
                df[col] = df[col].fillna(median_value)
        
        # 3. Mengisi data teks/kategori yang kosong dengan "Tidak Diketahui"
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            df[col] = df[col].fillna("Tidak Diketahui")
            
        st.success("✅ Pembersihan selesai: Nilai numerik kosong diisi dengan Median, nilai teks diisi dengan label standar.")
    else:
        st.success("✅ Data Bersih: Tidak ditemukan nilai kosong (missing values) pada dataset.")

    # ==========================================
    # PRE-PROCESSING (Penyesuaian Otomatis)
    # ==========================================
    # 1. Membuat kolom "Bulan" dari "Minggu Ke" (Asumsi 1 bulan = 4.33 minggu)
    if 'Minggu Ke' in df.columns and 'Bulan' not in df.columns:
        df['Bulan'] = np.ceil(df['Minggu Ke'] / 4.33).astype(int)
        df['Bulan'] = df['Bulan'].apply(lambda x: 12 if x > 12 else x)

    # 2. Jika file tidak punya 'Volume Mingguan' tapi punya 'Volume Harian', kita buatkan otomatis
    if 'Volume Mingguan (Liter)' not in df.columns and 'Volume Harian (Liter)' in df.columns:
        df['Volume Mingguan (Liter)'] = df['Volume Harian (Liter)'] * 7

    with st.expander("👀 Lihat Data yang Sudah Dibersihkan"):
        st.dataframe(df.head())

    st.divider()

    # Pastikan data esensial ada sebelum menggambar grafik
    if 'Harga per Liter (Rp)' in df.columns and 'Volume Mingguan (Liter)' in df.columns:

        # ==========================================
        # 1. ANALISIS UNIVARIAT
        # ==========================================
        st.header("📊 2. Analisis Univariat")
        st.markdown("Menganalisis karakteristik dasar dari variabel tunggal[cite: 260].")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_harga = px.histogram(df, x="Harga per Liter (Rp)", nbins=20, 
                                     title="Distribusi Harga Jual Susu",
                                     color_discrete_sequence=['#4C78A8'])
            fig_harga.update_layout(yaxis_title="Frekuensi")
            st.plotly_chart(fig_harga, use_container_width=True)
            
            harga_rata = df['Harga per Liter (Rp)'].mean()
            st.info(f"**Rata-rata Harga:** Rp {harga_rata:,.0f} per liter.")

        with col2:
            fig_vol = px.histogram(df, x="Volume Mingguan (Liter)", nbins=20,
                             title="Distribusi Volume Produksi Mingguan",
                             color_discrete_sequence=['#54A24B'])
            fig_vol.update_layout(yaxis_title="Frekuensi")
            st.plotly_chart(fig_vol, use_container_width=True)
            
            vol_rata = df['Volume Mingguan (Liter)'].mean()
            st.info(f"**Rata-rata Produksi:** {vol_rata:,.0f} liter/minggu.")

        st.divider()

        # ==========================================
        # 2. ANALISIS BIVARIAT
        # ==========================================
        st.header("📈 3. Analisis Bivariat")
        st.markdown("Mencari keterkaitan atau pola hubungan antara dua variabel[cite: 263].")

        col3, col4 = st.columns(2)

        with col3:
            vol_bulan = df.groupby('Bulan')['Volume Mingguan (Liter)'].mean().reset_index()
            fig_bulan = px.bar(vol_bulan, x='Bulan', y='Volume Mingguan (Liter)', 
                               title="Pola Musiman: Rata-rata Volume per Bulan",
                               text_auto='.0f', color='Volume Mingguan (Liter)', 
                               color_continuous_scale='Blues')
            st.plotly_chart(fig_bulan, use_container_width=True)

        with col4:
            fig_korelasi = px.scatter(df, x="Harga per Liter (Rp)", y="Volume Mingguan (Liter)", 
                                      trendline="ols", title="Korelasi: Harga vs Volume",
                                      opacity=0.6, color_discrete_sequence=['#E45756'])
            st.plotly_chart(fig_korelasi, use_container_width=True)

        st.divider()

        # ==========================================
        # 3. ANALISIS MULTIVARIAT
        # ==========================================
        st.header("🌐 4. Analisis Multivariat")
        st.markdown("Melihat interaksi kompleks antara tiga variabel atau lebih sekaligus[cite: 267].")

        if 'Laba Pendapatan 2 Mingguan (Rp)' in df.columns:
            fig_multi = px.scatter(df, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Laba Pendapatan 2 Mingguan (Rp)", color="Tahun",
                                   hover_name="Bulan", size_max=45,
                                   title="Bubble Chart: Perjalanan Bisnis (Waktu, Volume, Laba, Tahun)")
            st.plotly_chart(fig_multi, use_container_width=True)
        else:
            fig_multi = px.scatter(df, x="Minggu Ke", y="Volume Mingguan (Liter)", 
                                   size="Harga per Liter (Rp)", color="Tahun",
                                   hover_name="Bulan", size_max=20,
                                   title="Bubble Chart: Produksi & Harga Sepanjang Waktu")
            st.plotly_chart(fig_multi, use_container_width=True)

    else:
        st.error("❌ Kolom 'Harga per Liter (Rp)' atau 'Volume' tidak ditemukan dalam file.")
else:
    st.info("👈 Silakan unggah file CSV Amang Farm untuk memulai analisis.")
